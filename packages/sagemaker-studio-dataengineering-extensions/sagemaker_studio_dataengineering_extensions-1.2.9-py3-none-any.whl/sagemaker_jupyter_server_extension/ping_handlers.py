import json

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin


class SageMakerPingHandler(ExtensionHandlerMixin, APIHandler):
    # This function is purely for testing
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "data": "pong",
        }))

    @tornado.web.authenticated
    def head(self):
        # Get _xsrf cookie from request
        xsrf_token = self.get_cookie('_xsrf')
        if xsrf_token:
            # If xsrf_token exists, send it back as part of the response header
            self.set_header('X-Xsrftoken', xsrf_token)
            self.set_header("Access-Control-Expose-Headers", "X-Xsrftoken")
