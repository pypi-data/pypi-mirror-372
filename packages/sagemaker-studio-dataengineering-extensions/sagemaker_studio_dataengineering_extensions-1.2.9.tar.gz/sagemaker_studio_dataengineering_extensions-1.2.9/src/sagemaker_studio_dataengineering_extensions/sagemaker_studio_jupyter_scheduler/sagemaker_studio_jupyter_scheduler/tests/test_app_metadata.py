import json
import os
from unittest.mock import patch, mock_open

import pytest

from sagemaker_studio_jupyter_scheduler.util.app_metadata import (
    get_region_name,
    get_partition,
    get_user_details, get_sagemaker_image,
)
from sagemaker_studio_jupyter_scheduler.model.models import UserTypes

TEST_DEFAULT_REGION = "us-east-1"

MOCK_RESOURCE_METADATA = """
{
    "AppType": "KernelGateway",
    "DomainId": "d-xxxxxxxxxxxx",
    "UserProfileName": "profile-name",
    "ResourceArn": "arn:aws:sagemaker:us-east-2:account-id:app/d-xxxxxxxxxxxx/profile-name/KernelGateway/datascience--1-0-ml-t3-medium",
    "ResourceName": "datascience--1-0-ml",
    "AppImageVersion":""
}
"""

MOCK_RESOURCE_METADATA_SHARED_SPACE = """
{
    "AppType": "KernelGateway",
    "DomainId": "d-xxxxxxxxxxxx",
    "SpaceName": "space-name",
    "ResourceArn": "arn:aws:sagemaker:us-east-2:account-id:app/d-xxxxxxxxxxxx/profile-name/KernelGateway/datascience--1-0-ml-t3-medium",
    "ResourceName": "datascience--1-0-ml",
    "AppImageVersion":""
}
"""


from botocore.session import Session


class TestAppMetadataUtils:
    @patch.object(Session, "get_scoped_config")
    def test_get_region_name(self, get_scoped_config_mock):
        os.environ["AWS_REGION"] = TEST_DEFAULT_REGION
        result = get_region_name()
        assert result == TEST_DEFAULT_REGION

        del os.environ["AWS_REGION"]
        get_scoped_config_mock.return_value = {"region": "us-west-1"}
        result = get_region_name()
        assert result == "us-west-1"

        get_scoped_config_mock.return_value = {}
        os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
        result = get_region_name()
        assert result == "us-west-2"

        del os.environ["AWS_DEFAULT_REGION"]
        result = get_region_name()
        assert result == "us-east-2"

    @patch("sagemaker_studio_jupyter_scheduler.util.app_metadata.get_region_name")
    def test_get_partition(self, get_region_name_mock):
        get_region_name_mock.return_value = "us-east-2"
        result = get_partition()
        assert result == "aws"

    @patch("sagemaker_studio_jupyter_scheduler.util.app_metadata.get_region_name")
    def test_get_partition_roundtable_region(self, get_region_name_mock):
        get_region_name_mock.return_value = "cn-north-1"
        result = get_partition()
        assert result == "aws-cn"

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=MOCK_RESOURCE_METADATA,
    )
    def test_get_user_details_profile(self, mock_file_contents):
        result = get_user_details()
        assert result.user_id_key == UserTypes.PROFILE_USER
        assert (
            result.user_id_value
            == json.loads(MOCK_RESOURCE_METADATA)["UserProfileName"]
        )

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=MOCK_RESOURCE_METADATA_SHARED_SPACE,
    )
    def test_get_user_details_shared_space_profile(self, mock_file_contents):
        result = get_user_details()
        assert result.user_id_key == UserTypes.SHARED_SPACE_USER
        assert (
            result.user_id_value
            == json.loads(MOCK_RESOURCE_METADATA_SHARED_SPACE)["SpaceName"]
        )

    def test_get_sagemaker_image(self):
        with patch.dict(os.environ, {
            'SAGEMAKER_INTERNAL_IMAGE_URI': 'test-uri',
            'IMAGE_VERSION': '1.0'
        }, clear=True):
            result = get_sagemaker_image()
            assert result == 'test-uri:1.0'

        with patch.dict(os.environ, {
            'SAGEMAKER_INTERNAL_IMAGE_URI': 'test-uri',
            'IMAGE_VERSION': ''
        }, clear=True):
            result = get_sagemaker_image()
            assert result == 'test-uri'

        with patch.dict(os.environ, {
            'SAGEMAKER_INTERNAL_IMAGE_URI': '',
            'IMAGE_VERSION': ''
        }, clear=True):
            result = get_sagemaker_image()
            assert result == 'UNKNOWN'
