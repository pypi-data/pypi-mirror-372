import json
import os
from unittest.mock import MagicMock, mock_open, patch
import pytest
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
)

from sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter import (
    InternalMetadataAdapter,
)

SAGEMAKER_INTERNAL_METADATA_FILE = "/opt/.sagemakerinternal/internal-metadata.json"

INTERNAL_METADATA_CONTENT = {
    "Stage": "Production",
    "AppNetworkAccessType": "VpcOnly",
    "FirstPartyImages": ["image1", "image2"],
    "CustomImages": ["custom_image1", "custom_image2"],
}


@pytest.fixture(autouse=True)
def mock_jupyter_lab_environment():
    with patch(
        "sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter.get_sagemaker_environment",
        return_value=JupyterLabEnvironment.SAGEMAKER_STUDIO,
    ):
        yield


class TestInternalMetadataAdapterStudio:
    @patch("os.path.getmtime")
    @patch("builtins.open", mock_open(read_data=json.dumps(INTERNAL_METADATA_CONTENT)))
    def test_init(self, getmtime_mock):
        getmtime_mock.return_value = 0
        adapter = InternalMetadataAdapter()

        assert adapter.config_file == SAGEMAKER_INTERNAL_METADATA_FILE
        assert adapter.metadata == INTERNAL_METADATA_CONTENT

    @patch("os.path.getmtime")
    @patch("builtins.open", mock_open(read_data=json.dumps(INTERNAL_METADATA_CONTENT)))
    def test_get_stage(self, getmtime_mock):
        getmtime_mock.return_value = 0
        adapter = InternalMetadataAdapter()

        assert adapter.get_stage() == "Production"

    @patch("os.path.getmtime")
    def test_get_app_network_access_type(self, getmtime_mock):
        getmtime_mock.return_value = 0

        with patch(
                "builtins.open",
                mock_open(read_data=json.dumps(INTERNAL_METADATA_CONTENT))
        ):
            adapter = InternalMetadataAdapter()
            assert adapter.get_app_network_access_type() == "VpcOnly"

        # clear cache
        if hasattr(InternalMetadataAdapter, 'get_sagemaker_image'):
            InternalMetadataAdapter.get_sagemaker_image.cache_clear()

        # Test for UNKNOWN case
        modified_content = INTERNAL_METADATA_CONTENT.copy()  # Create a copy
        modified_content.pop("AppNetworkAccessType")  # Remove from copy
        with patch(
                "builtins.open",
                mock_open(read_data=json.dumps(modified_content))
        ):
            adapter = InternalMetadataAdapter()
            assert adapter.get_app_network_access_type() == "UNKNOWN"

    @patch("os.path.getmtime")
    @patch("builtins.open")
    def test_get_images(self, open_mock, getmtime_mock):
        # Initial file content
        open_mock.return_value = mock_open(
            read_data=json.dumps(INTERNAL_METADATA_CONTENT)
        ).return_value

        adapter = InternalMetadataAdapter()
        assert adapter.get_first_party_images() == ["image1", "image2"]
        assert adapter.get_custom_images() == ["custom_image1", "custom_image2"]

        # Updated file content 1st time
        updated_content = {
            "Stage": "Production",
            "FirstPartyImages": ["new_image1", "new_image2"],
            "CustomImages": ["new_custom_image1", "new_custom_image2"],
        }
        open_mock.return_value = mock_open(
            read_data=json.dumps(updated_content)
        ).return_value
        getmtime_mock.side_effect = [0, 1]
        assert adapter.get_first_party_images() == ["new_image1", "new_image2"]

        open_mock.return_value = mock_open(
            read_data=json.dumps(updated_content)
        ).return_value
        getmtime_mock.side_effect = [0, 1]
        assert adapter.get_custom_images() == ["new_custom_image1", "new_custom_image2"]

        # Updated file content 2nd time
        other_content = {
            "Stage": "Production",
            "FirstPartyImages": ["other_image1", "other_image2"],
            "CustomImages": ["other_custom_image1", "other_custom_image2"],
        }
        open_mock.return_value = mock_open(
            read_data=json.dumps(other_content)
        ).return_value
        getmtime_mock.side_effect = [0, 1]
        assert adapter.get_first_party_images() == ["other_image1", "other_image2"]

        open_mock.return_value = mock_open(
            read_data=json.dumps(other_content)
        ).return_value
        getmtime_mock.side_effect = [0, 1]
        assert adapter.get_custom_images() == [
            "other_custom_image1",
            "other_custom_image2",
        ]
