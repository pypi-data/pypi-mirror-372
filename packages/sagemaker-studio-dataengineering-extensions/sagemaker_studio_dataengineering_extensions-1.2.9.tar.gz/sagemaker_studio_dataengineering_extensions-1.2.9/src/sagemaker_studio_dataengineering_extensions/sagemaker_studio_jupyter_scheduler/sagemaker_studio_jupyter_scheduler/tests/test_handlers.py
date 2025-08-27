import asyncio
import time
from unittest.mock import MagicMock, patch
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
import pytest

import sagemaker_studio_jupyter_scheduler
from sagemaker_studio_jupyter_scheduler.extension.advanced_environments.sagemaker_advanced_environments import (
    SageMakerAdvancedEnvironments,
)
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
)
from sagemaker_studio_jupyter_scheduler.extension.handlers import AdvancedEnvironmentsHandler

# TODO: need to add unit test, for now manually testing
# @pytest.mark.asyncio
# @patch.object(SageMakerAdvancedEnvironments, "get_advanced_environments")
# @patch(
#     "sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter.JupyterLabEnvironmentDetector",
#     autospec=True,
# )
# async def test_advanced_environment_timeout(mock_detector, mock_advanced):
#     TEST_TIMEOUT_SECS = 2
#     sagemaker_studio_jupyter_scheduler.handlers.MAX_WAIT_TIME_FOR_API_CALL_SECS = (
#         TEST_TIMEOUT_SECS
#     )
#     mock_detector.return_value.current_environment = (
#         JupyterLabEnvironment.VANILLA_JUPYTERLAB
#     )
#     mock_handler_mixin = MagicMock(name="test", spec=ExtensionHandlerMixin)
#     mock_jupyter_handler = MagicMock(spec=JupyterHandler)
#     mock_handler_mixin.ui_methods = {}
#     mock_handler_mixin.ui_modules = {}
#     mock_handler_mixin.settings = {}
#     mock_handler_mixin.connection = {}
#     mock_jupyter_handler.connection = MagicMock()
#     handler = AdvancedEnvironmentsHandler(mock_handler_mixin, mock_jupyter_handler)
#     handler.initialize = MagicMock()
#     handler.get_current_user = MagicMock()
#     handler.finish = MagicMock()

#     async def get_advanced_sleep(logger):
#         await asyncio.sleep(TEST_TIMEOUT_SECS + 50)

#     mock_advanced.side_effect = get_advanced_sleep

#     start = time.time()
#     await handler.get()
#     end = time.time()
#     actual_api_time = end - start

#     # we want the api call to be as close as possible to MAX_WAIT_TIME_FOR_API_CALL_SECS,
#     # adding a 50 ms wiggle room as there are no other api call in this test
#     assert TEST_TIMEOUT_SECS <= actual_api_time <= TEST_TIMEOUT_SECS + 0.05
