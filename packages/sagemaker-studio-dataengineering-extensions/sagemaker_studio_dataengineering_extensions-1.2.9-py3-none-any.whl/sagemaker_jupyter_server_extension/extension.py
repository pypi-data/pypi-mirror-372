from jupyter_server.extension.application import ExtensionApp

from .connection_handler import SageMakerConnectionHandler
from .connections_handler import SageMakerConnectionsHandler
from .creds_handlers import SageMakerCredsHandler
from .debugging_info_handler import SageMakerConnectionDebuggingInfoHandler
from .env_handlers import SageMakerEnvHandler
from .ping_handlers import SageMakerPingHandler
from .post_startup_handler import SageMakerPostStartupHandler
from .spark_history_server import SageMakerSparkHistoryServerHandler
from .workflow_handler import SageMakerWorkflowHandler


class Extension(ExtensionApp):
    name = "sagemaker_jupyter_server_extension"

    handlers = [
        ("sagemaker/ping", SageMakerPingHandler),
        ("api/creds", SageMakerCredsHandler),
        ("api/aws/datazone/connections", SageMakerConnectionsHandler),
        ("api/env", SageMakerEnvHandler),
        ("api/aws/datazone/connection", SageMakerConnectionHandler),
        ("api/sagemaker/workflows/(.*)", SageMakerWorkflowHandler),
        ("api/spark-history-server", SageMakerSparkHistoryServerHandler),
        ("api/poststartup", SageMakerPostStartupHandler),
        ("api/debugging/info/(.*)", SageMakerConnectionDebuggingInfoHandler)
    ]
