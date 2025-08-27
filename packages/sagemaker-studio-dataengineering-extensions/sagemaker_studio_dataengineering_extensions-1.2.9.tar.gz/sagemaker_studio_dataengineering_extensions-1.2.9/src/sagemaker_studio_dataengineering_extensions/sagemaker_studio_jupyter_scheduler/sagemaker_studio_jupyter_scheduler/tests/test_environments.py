import json
import os
from unittest.mock import patch

import pytest
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
    JupyterLabEnvironmentDetector,
)
from sagemaker_studio_jupyter_scheduler.scheduler import SagemakerEnvironmentManager


@pytest.fixture(autouse=True)
def mock_jupyter_lab_environment():
    with patch(
        "sagemaker_studio_jupyter_scheduler.scheduler.environments.JupyterLabEnvironmentDetector",
        autospec=True,
    ) as mock_detector:
        mock_detector.return_value.current_environment = (
            JupyterLabEnvironment.SAGEMAKER_STUDIO
        )
        yield


class TestSagemakerEnvironments:
    patch.dict(os.environ, {"REGION_NAME": "us-west-2", "HOME": "."}, clear=True)

    def test_default_sagemaker_defaults(self):
        envs_response = SagemakerEnvironmentManager().list_environments()
        assert envs_response[0].name == "sagemaker-default-env"
        for instance in envs_response[0].compute_types:
            assert instance.startswith("ml")
