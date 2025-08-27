import asyncio
import json
import logging

import boto3
import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)

class SageMakerCredsHandler(ExtensionHandlerMixin, APIHandler):
    @tornado.web.authenticated
    async def get(self):
        try:
            logger.info('Received request to get credentials')
            self.set_header('Cache-Control', 'no-store')
            self.set_header('Expires', '0')

            loop = asyncio.get_running_loop()

            def get_credentials():
                try:
                    session = boto3.Session(profile_name='default')
                    credentials = session.get_credentials()
                    if not credentials:
                        raise ValueError("Failed to obtain credentials")

                    credentials = credentials.get_frozen_credentials()
                    return {
                        "access_key": credentials.access_key,
                        "secret_key": credentials.secret_key,
                        "session_token": credentials.token
                    }
                except boto3.exceptions.Boto3Error as boto_error:
                    raise HTTPError(500, f"AWS credentials error: {str(boto_error)}")
                except Exception as e:
                    raise HTTPError(500, f"Failed to get credentials: {str(e)}")

            try:
                credentials = await loop.run_in_executor(None, get_credentials)
                await self.finish(json.dumps(credentials))
            except tornado.web.HTTPError as http_error:
                self.set_status(http_error.status_code)
                error_response = {
                    "error": True,
                    "message": http_error.log_message,
                    "status": http_error.status_code
                }
                self.finish(json.dumps(error_response))

        except Exception as e:
            logger.exception(e)
            self.set_status(500)
            error_response = {
                "error": True,
                "message": f"{str(e)}",
                "status": 500
            }
            self.finish(json.dumps(error_response))
