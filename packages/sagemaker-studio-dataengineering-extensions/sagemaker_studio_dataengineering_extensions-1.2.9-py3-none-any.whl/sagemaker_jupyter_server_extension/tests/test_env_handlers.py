import asyncio
import json
import time
from unittest.mock import MagicMock, patch

from sagemaker_jupyter_server_extension.env_handlers import SageMakerEnvHandler

@patch("sagemaker_jupyter_server_extension.env_handlers.SageMakerEnvHandler.read_metadata_file")
@patch("sagemaker_jupyter_server_extension.env_handlers.SageMakerEnvHandler.read_storage_metadata_file")
def test_read_metadata_sm_project_path_from_storage_metadata_file(mock_read_storage_metadata_file, mock_read_metadata_file):
    mock_read_storage_metadata_file.return_value={"smusProjectDirectory": "/home/sagemaker-user/shared"}
    mock_read_metadata_file.return_value={
        "AppType": "JupyterLab",
        "DomainId": "d-1234567890ab",
        "SpaceName": "default-12345abc-0000-1111-aaaa-ab1234567890",
        "ExecutionRoleArn": "arn:aws:iam::123456789012:role/Admin",
        "ResourceArn": "arn:aws:sagemaker:us-west-2:123456789012:app/d-1234567890ab/default-12345abc-0000-1111-aaaa-ab1234567890/JupyterLab/default",
        "ResourceName": "default",
        "AppImageVersion": "",
        "AdditionalMetadata": {
            "DataZoneDomainId": "dzd_1234567890abcd",
            "DataZoneDomainRegion": "us-west-2",
            "DataZoneEndpoint": "https://datazone.us-west-2.api.aws",
            "DataZoneEnvironmentId": "e1234567890abc",
            "DataZoneProjectId": "p1234567890abc",
            "DataZoneScopeName": "dev",
            "DataZoneStage": "gamma",
            "DataZoneUserId": "12345abc-0000-1111-aaaa-ab1234567890",
            "PrivateSubnets": "",
            "ProjectS3Path": "s3://amazon-sagemaker-123456789012-us-west-2-1234567890abcd/shared/",
            "SecurityGroup": ""
        },
        "ResourceArnCaseSensitive": "arn:aws:sagemaker:us-west-2:123456789012:app/d-1234567890ab/default-12345abc-0000-1111-aaaa-ab1234567890/jupyterlab/default",
        "IpAddressType": "ipv4"
        }
    response = SageMakerEnvHandler.read_metadata()
    print(response)
    assert response["project_id"] == "p1234567890abc"
    assert response["domain_id"] == "dzd_1234567890abcd"
    assert response["user_id"] == "12345abc-0000-1111-aaaa-ab1234567890"
    assert response["environment_id"] == "e1234567890abc"
    assert response["project_s3_path"] == "s3://amazon-sagemaker-123456789012-us-west-2-1234567890abcd/shared/"
    assert response["subnets"] == ""
    assert response["security_group"] == ""
    assert response["dz_endpoint"] == "https://datazone.us-west-2.api.aws"
    assert response["dz_stage"] == "gamma"
    assert response["dz_region"] == "us-west-2"
    assert response["aws_region"] == ""
    assert response["sm_domain_id"] == "d-1234567890ab"
    assert response["sm_space_name"] == "default-12345abc-0000-1111-aaaa-ab1234567890"
    assert response["sm_user_profile_name"] == "12345abc-0000-1111-aaaa-ab1234567890"
    assert response["sm_project_path"] == "/home/sagemaker-user/shared"

@patch("sagemaker_jupyter_server_extension.env_handlers.SageMakerEnvHandler.read_metadata_file")
@patch("sagemaker_jupyter_server_extension.env_handlers.SageMakerEnvHandler.read_storage_metadata_file")
def test_read_metadata_sm_project_path_from_metadata_file(mock_read_storage_metadata_file, mock_read_metadata_file):
    mock_read_storage_metadata_file.return_value={"smusProjectDirectory": "/home/sagemaker-user/shared"}
    mock_read_metadata_file.return_value={
        "AppType": "JupyterLab",
        "DomainId": "d-1234567890ab",
        "SpaceName": "default-12345abc-0000-1111-aaaa-ab1234567890",
        "ExecutionRoleArn": "arn:aws:iam::123456789012:role/Admin",
        "ResourceArn": "arn:aws:sagemaker:us-west-2:123456789012:app/d-1234567890ab/default-12345abc-0000-1111-aaaa-ab1234567890/JupyterLab/default",
        "ResourceName": "default",
        "AppImageVersion": "",
        "AdditionalMetadata": {
            "DataZoneDomainId": "dzd_1234567890abcd",
            "DataZoneDomainRegion": "us-west-2",
            "DataZoneEndpoint": "https://datazone.us-west-2.api.aws",
            "DataZoneEnvironmentId": "e1234567890abc",
            "DataZoneProjectId": "p1234567890abc",
            "DataZoneScopeName": "dev",
            "DataZoneStage": "gamma",
            "DataZoneUserId": "12345abc-0000-1111-aaaa-ab1234567890",
            "PrivateSubnets": "",
            "ProjectS3Path": "s3://amazon-sagemaker-123456789012-us-west-2-1234567890abcd/shared/",
            "SecurityGroup": "",
            "ProjectSharedDirectory": "/home/sagemaker-user/test",
            "ProjectStorageType" : "S3"
        },
        "ResourceArnCaseSensitive": "arn:aws:sagemaker:us-west-2:123456789012:app/d-1234567890ab/default-12345abc-0000-1111-aaaa-ab1234567890/jupyterlab/default",
        "IpAddressType": "ipv4"
        }
    response = SageMakerEnvHandler.read_metadata()
    print(response)
    assert response["project_id"] == "p1234567890abc"
    assert response["domain_id"] == "dzd_1234567890abcd"
    assert response["user_id"] == "12345abc-0000-1111-aaaa-ab1234567890"
    assert response["environment_id"] == "e1234567890abc"
    assert response["project_s3_path"] == "s3://amazon-sagemaker-123456789012-us-west-2-1234567890abcd/shared/"
    assert response["subnets"] == ""
    assert response["security_group"] == ""
    assert response["dz_endpoint"] == "https://datazone.us-west-2.api.aws"
    assert response["dz_stage"] == "gamma"
    assert response["dz_region"] == "us-west-2"
    assert response["aws_region"] == ""
    assert response["sm_domain_id"] == "d-1234567890ab"
    assert response["sm_space_name"] == "default-12345abc-0000-1111-aaaa-ab1234567890"
    assert response["sm_user_profile_name"] == "12345abc-0000-1111-aaaa-ab1234567890"
    assert response["sm_project_path"] == "/home/sagemaker-user/test"
