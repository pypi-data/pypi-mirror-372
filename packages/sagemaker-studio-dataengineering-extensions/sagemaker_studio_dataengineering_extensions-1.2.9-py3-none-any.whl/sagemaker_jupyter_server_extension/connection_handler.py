import asyncio
import json
import logging
import urllib

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
from tornado import web

from sagemaker_jupyter_server_extension.connection_utils.connection_utils import get_connection

logger = logging.getLogger(__name__)

class SageMakerConnectionHandler(ExtensionHandlerMixin, APIHandler):
    @tornado.web.authenticated
    async def get(self):
        try:
            query_params = dict(urllib.parse.parse_qsl(self.request.query))

            connection_name = query_params.get("name")
            if connection_name is None:
                raise web.HTTPError(400, "Invalid request, connection name is required.")
            logger.info('received request to get connection')
            loop = asyncio.get_running_loop()
            connection = await loop.run_in_executor(None, get_connection, connection_name)
            await self.finish(json.dumps(connection, default=str))
        except Exception as e:
            logger.exception(e)
