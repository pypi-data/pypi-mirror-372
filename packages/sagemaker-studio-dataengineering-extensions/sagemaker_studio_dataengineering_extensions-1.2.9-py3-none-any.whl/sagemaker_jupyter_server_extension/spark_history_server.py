import asyncio
import json
import logging
import subprocess
from functools import cache

import boto3
import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
from tornado.web import HTTPError

from .spark_history_server_utils import ErrorMessage, check_sm_spark_cli_exists, is_valid_s3_uri_dir

logger = logging.getLogger(__name__)

class SageMakerSparkHistoryServerHandler(ExtensionHandlerMixin, APIHandler):

    @tornado.web.authenticated
    async def get(self):
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self.dispatcher, 'GET')
        await self.finish(json.dumps(result))

    @tornado.web.authenticated
    async def post(self):
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self.dispatcher, 'POST')
        await self.finish(json.dumps(result))

    def dispatcher(self, method):
        if method == 'GET':
            return self.get_spark_history_server_status()
        elif method == 'POST':
            payload = json.loads(self.request.body)
            many_args_error = HTTPError(400, 'too many arguments specified')

            if 'command' not in payload:
                raise HTTPError(400, 'command argument is required')

            if 'stop' in payload['command']:
                if len(payload) != 1:
                    raise many_args_error
                return self.stop_spark_history_server()

            if 'start' in payload['command']:
                if 's3Path' in payload:
                    if len(payload) == 2:
                        if is_valid_s3_uri_dir(payload["s3Path"]):
                            return self.start_spark_history_server(payload)
                        raise HTTPError(400, 'invalid S3 URI directory')
                    raise many_args_error
                else:
                    raise HTTPError(400, 's3Path argument is required')

            raise HTTPError(400, 'unsupported command argument')
        else:
            raise HTTPError(405, ErrorMessage.INVALID_REQUEST_METHOD_NOT_SUPPORTED)

    @check_sm_spark_cli_exists()
    def get_spark_history_server_status(self):
        RUNNING = 'running'
        NOT_RUNNING = 'not running'
        RUNNING_TOKEN = 'Spark History Server is running'
        NOT_RUNNING_TOKEN = 'Spark History Server is not running'

        try:
            result = subprocess.run(
                ['sm-spark-cli', 'status'],
                capture_output=True,
                text=True,
                check=True
            ).stdout

            if RUNNING_TOKEN in result:
                return self.format_response(RUNNING, {'message': RUNNING_TOKEN})
            if NOT_RUNNING_TOKEN in result:
                return self.format_response(NOT_RUNNING, {'message': NOT_RUNNING_TOKEN})

            return self.format_response('N/A', {'message': ErrorMessage.UNEXPECTED_ERROR})

        except subprocess.CalledProcessError as e:
            if NOT_RUNNING_TOKEN in e.stdout:
                return self.format_response(NOT_RUNNING, {'message': NOT_RUNNING_TOKEN})
            raise Exception(e)
        except Exception as e:
            self.logException(e)
            raise HTTPError(500, ErrorMessage.UNEXPECTED_ERROR % e)

    @check_sm_spark_cli_exists()
    def stop_spark_history_server(self):
        STOPPED = 'stopped'
        STOPPED_TOKEN = 'Spark History Server Stopped'

        try:
            result = subprocess.run(
                ['sm-spark-cli', 'stop'],
                capture_output=True,
                text=True,
                check=True
            ).stdout

            if STOPPED_TOKEN in result:
                return self.format_response(STOPPED, {'message': STOPPED_TOKEN})

            raise Exception(result)

        except Exception as e:
            self.logException(e)
            raise HTTPError(500, ErrorMessage.UNEXPECTED_ERROR % e)

    @check_sm_spark_cli_exists()
    def start_spark_history_server(self, payload):
        STARTED = 'started'
        STARTED_TOKEN = 'Spark History Server Started'

        space_details = self.get_space_details()
        space_url = space_details['url']
        space_id = space_url.split('.')[0].split('//')[1]

        try:
            subprocess.run(['sm-spark-cli', 'stop'],
                           capture_output=True, text=True, check=True)

            subprocess.run(
                ['sm-spark-cli', 'start', payload['s3Path']],
                input=f'{space_id}\ny\n',
                capture_output=True,
                text=True,
                check=True
            ).check_returncode()

            spark_ui = f'{space_url}/proxy/18080'
            return self.format_response(STARTED, {'spark_ui': spark_ui, 'message': STARTED_TOKEN})

        except Exception as e:
            self.logException(e)
            raise HTTPError(500, ErrorMessage.UNEXPECTED_ERROR % e)

    def format_response(self, status, result):
        return {'status': status, **result}

    @cache
    def get_space_details(self):
        try:
            with open('/opt/ml/metadata/resource-metadata.json') as json_file:
                metadata = json.load(json_file)
                domain_id = metadata['DomainId']
                space_name = metadata['SpaceName']

                response = boto3.Session().client('sagemaker').describe_space(
                    DomainId=domain_id,
                    SpaceName=space_name
                )

                logger.info('[spark-history-server]: space details retrieved')
                return {'url': response['Url']}

        except Exception as e:
            self.logException(e)
            raise HTTPError(
                500, "An error occurred when retrieving space id:", e)

    def logException(self, e: Exception):
        logger.exception('[spark-history-server]:', e)
