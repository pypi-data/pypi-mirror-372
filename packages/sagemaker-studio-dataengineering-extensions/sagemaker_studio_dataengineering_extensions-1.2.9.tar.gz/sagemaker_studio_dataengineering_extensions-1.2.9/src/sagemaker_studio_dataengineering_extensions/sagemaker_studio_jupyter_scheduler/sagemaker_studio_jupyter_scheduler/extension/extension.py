from sagemaker_studio_jupyter_scheduler.logging import init_api_operation_logger
from jupyter_server.extension.application import ExtensionApp
from .handlers import (
    AdvancedEnvironmentsHandler,
    SageMakerImagesListHandler,
    ValidateVolumePathHandler
)

class SageMakerSchedulingApp(ExtensionApp):
    name = "sagemaker_studio_jupyter_scheduler"
    handlers = [
        (r"/sagemaker_studio_jupyter_scheduler/advanced_environments", AdvancedEnvironmentsHandler),
        (r"/sagemaker_studio_jupyter_scheduler/sagemaker_images", SageMakerImagesListHandler),
        (r"/sagemaker_studio_jupyter_scheduler/validate_volume_path", ValidateVolumePathHandler)
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        init_api_operation_logger(self.log)
