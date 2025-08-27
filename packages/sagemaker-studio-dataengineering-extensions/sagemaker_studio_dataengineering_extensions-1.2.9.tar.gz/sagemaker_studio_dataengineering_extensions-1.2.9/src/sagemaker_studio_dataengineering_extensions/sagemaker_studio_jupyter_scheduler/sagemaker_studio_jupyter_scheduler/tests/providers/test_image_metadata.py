import json
from unittest.mock import AsyncMock, mock_open, patch
import pytest
from sagemaker_studio_jupyter_scheduler.util.aws_clients import SageMakerAsyncBoto3Client
from sagemaker_studio_jupyter_scheduler.util.environment_detector import JupyterLabEnvironment
from sagemaker_studio_jupyter_scheduler.model.models import (
    DEFAULT_GUID,
    DEFAULT_IMAGE_OWNER,
    DEFAULT_MOUNT_PATH,
    DEFAULT_UID,
)
from sagemaker_studio_jupyter_scheduler.providers.standalone_image_metadata import (
    get_default_ecr_uri_standalone,
    get_default_image_arn_standalone,
    get_default_image_kernel_name_standalone,
    standalone_image_map,
    STANDALONE_IMAGEARN_KEY,
    STANDALONE_ECR_URI_KEY,
    STANDALONE_KERNEL_NAME,
    STANDALONE_DEFAULT_GUID,
    STANDALONE_DEFAULT_UID,
    STANDALONE_DEFAULT_IMAGE_OWNER,
    STANDALONE_DEFAULT_MOUNT_PATH,
)


from sagemaker_studio_jupyter_scheduler.providers.image_metadata import (
    get_image_metadata,
)
from sagemaker_studio_jupyter_scheduler.providers.studio_image_metadata import (
    get_image_metadata_studio,
    get_metadata_from_config_file,
)
from sagemaker_studio_jupyter_scheduler.tests.data.mock_files import (
    MOCK_INTERNAL_METADATA,
)


@pytest.mark.asyncio
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.image_metadata.get_sagemaker_environment",
    return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
)
async def test_standalone_image_metadata_custom_ecr(mock_get_sagemaker_environment):
    test_image_ecr_uri = (
        "708448604839.dkr.ecr.us-east-2.amazonaws.com/custom-sm-studio:latest"
    )
    image_metadata = await get_image_metadata(test_image_ecr_uri, "us-west-2")
    assert image_metadata.ecr_uri == test_image_ecr_uri
    assert image_metadata.gid == DEFAULT_GUID
    assert image_metadata.uid == DEFAULT_UID
    assert image_metadata.image_owner == DEFAULT_IMAGE_OWNER
    assert image_metadata.image_arn == test_image_ecr_uri
    assert image_metadata.mount_path == DEFAULT_MOUNT_PATH


@pytest.mark.asyncio
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.image_metadata.get_sagemaker_environment",
    return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
)
async def test_standalone_image_metadata_default(mock_get_sagemaker_environment):
    test_image_arn = (
        "arn:aws:sagemaker:af-south-1:559312083959:image/sagemaker-base-python-38"
    )

    image_metadata = await get_image_metadata(test_image_arn, "af-south-1")
    assert (
        image_metadata.ecr_uri
        == "559312083959.dkr.ecr.af-south-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc"
    )
    assert image_metadata.gid == STANDALONE_DEFAULT_GUID
    assert image_metadata.uid == STANDALONE_DEFAULT_UID
    assert image_metadata.image_owner == STANDALONE_DEFAULT_IMAGE_OWNER
    assert image_metadata.image_arn == test_image_arn
    assert image_metadata.mount_path == STANDALONE_DEFAULT_MOUNT_PATH


def test_get_default_image_arn_standalone():
    test_region = "us-west-2"
    assert (
        get_default_image_arn_standalone(test_region)
        == standalone_image_map[test_region][STANDALONE_IMAGEARN_KEY]
    )


def test_get_default_image_ecr_uri_standalone():
    test_region = "us-west-2"
    assert (
        get_default_ecr_uri_standalone(test_region)
        == standalone_image_map[test_region][STANDALONE_ECR_URI_KEY]
    )


def test_get_default_image_kernel_details_standalone():
    assert get_default_image_kernel_name_standalone() == STANDALONE_KERNEL_NAME


# Studio specific tests
# model converter is the only place image metadata is used for training job creation
# TODO: handle stage detection in studio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_INTERNAL_METADATA)
def test_studio_get_internal_metadata_file(mock_internal_metadata):
    assert json.loads(MOCK_INTERNAL_METADATA) == get_metadata_from_config_file()


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_INTERNAL_METADATA)
async def test_studio_get_first_party_images(mock_internal_metadata):
    test_image_arn = "arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0"
    test_region = "us-west-2"
    image_metadata = await get_image_metadata_studio(test_image_arn, test_region)
    assert image_metadata.gid == "0"
    assert image_metadata.uid == "0"
    assert image_metadata.mount_path == "/root"
    assert image_metadata.image_arn == test_image_arn
    assert (
        image_metadata.ecr_uri
        == "236514542706.dkr.ecr.us-west-2.amazonaws.com/sagemaker-data-science-environment:1.0"
    )

@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_INTERNAL_METADATA)
async def test_studio_get_first_party_images_with_non_root_user(mock_internal_metadata):
    test_image_arn = "arn:aws:sagemaker:us-west-2:123456789012:image/sagemaker-distribution-gpu-v0"
    test_region = "us-west-2"
    image_metadata = await get_image_metadata_studio(test_image_arn, test_region)
    assert image_metadata.gid == "100"
    assert image_metadata.uid == "1000"
    assert image_metadata.mount_path == "/home/sagemaker-user"
    assert image_metadata.image_arn == test_image_arn
    assert (
        image_metadata.ecr_uri
        == "123456789012.dkr.ecr.us-west-2.amazonaws.com/sagemaker-distribution-prod:0.4.1-gpu"
    )


MOCK_DESCRIBE_DOMAIN = {
    "DefaultUserSettings": {
        "KernelGatewayAppSettings": {
            "CustomImages": [
                {
                    "ImageName": "custom-image",
                    "AppImageConfigName": "custom-image-config",
                },
                {
                    "ImageName": "multi-py-conda-image",
                    "AppImageConfigName": "multi-py-conda-image-config",
                },
            ]
        }
    }
}

MOCK_DESCRIBE_USER_PROFILE = {
    "UserSettings": {
        "KernelGatewayAppSettings": {
            "CustomImages": [
                {
                    "ImageName": "another-custom-image",
                    "AppImageConfigName": "another-custom-image-config",
                },
            ]
        }
    }
}

MOCK_DESCRIBE_SPACE_SETTINGS = {
    "SpaceSettings": {
        "KernelGatewayAppSettings": {
            "CustomImages": [
                {
                    "ImageName": "multi-py-conda-image",
                    "AppImageConfigName": "multi-py-conda-image",
                },
            ]
        }
    }
}

MOCK_DESCRIBE_IMAGE_VERSION = {
    "BaseImage": "177118115371.dkr.ecr.us-east-1.amazonaws.com/multi-py-conda-image:0.0.1",
    "ContainerImage": "177118115371.dkr.ecr.us-east-1.amazonaws.com/multi-py-conda-image@sha256:947aec5e04638b43db188fd51ab8e850ac31bf83281c5b61f2e2f4d5e0f06477",
    "CreationTime": 1666064247.19,
    "ImageArn": "arn:aws:sagemaker:us-east-1:177118115371:image/multi-py-conda-image",
    "ImageVersionArn": "arn:aws:sagemaker:us-east-1:177118115371:image-version/multi-py-conda-image/2",
    "ImageVersionStatus": "CREATED",
    "LastModifiedTime": 1666064247.561,
    "Version": 2,
    "Horovod": False,
}

MOCK_DESCRIBE_APP_IMAGE_CONFIG = {
    "AppImageConfigArn": "arn:aws:sagemaker:us-east-1:177118115371:app-image-config/multi-py-conda-image-config",
    "AppImageConfigName": "multi-py-conda-image-config",
    "CreationTime": 1666064286.771,
    "LastModifiedTime": 1666064286.776,
    "KernelGatewayImageConfig": {
        "KernelSpecs": [
            {
                "Name": "conda-env-py310-py",
                "DisplayName": "conda env py310",
            },
            {
                "Name": "conda-env-py39-py",
                "DisplayName": "conda env py39",
            },
            {
                "Name": "conda-env-py37-py",
                "DisplayName": "conda env py37",
            },
            {
                "Name": "conda-env-py38-py",
                "DisplayName": "conda env py38",
            },
        ],
        "FileSystemConfig": {
            "MountPath": "/home/sagemaker-user",
            "DefaultUid": 1000,
            "DefaultGid": 100,
        },
    },
}


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_INTERNAL_METADATA)
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.studio_image_metadata.get_sagemaker_client"
)
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.studio_image_metadata.get_user_profile_name"
)
async def test_studio_third_party_image(
    mock_get_user_profile_name,
    mock_get_sagemaker_client,
    mock_internal_metadata,
):
    mock_get_user_profile_name.return_value = "user-profile-test"
    mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
    mock_sagemaker_client.describe_domain.return_value = MOCK_DESCRIBE_DOMAIN
    mock_sagemaker_client.describe_image_version.return_value = (
        MOCK_DESCRIBE_IMAGE_VERSION
    )
    mock_sagemaker_client.describe_app_image_config.return_value = (
        MOCK_DESCRIBE_APP_IMAGE_CONFIG
    )
    mock_sagemaker_client.describe_user_profile.return_value = (
        MOCK_DESCRIBE_USER_PROFILE
    )

    mock_get_sagemaker_client.return_value = mock_sagemaker_client
    test_image_arn = (
        "arn:aws:sagemaker:us-east-1:177118115371:image/multi-py-conda-image"
    )
    test_region = "us-west-2"
    image_metadata = await get_image_metadata_studio(test_image_arn, test_region)
    assert image_metadata.image_owner == "Customer Owned"
    assert image_metadata.mount_path == "/home/sagemaker-user"
    assert image_metadata.uid == "1000"
    assert image_metadata.gid == "100"
    mock_sagemaker_client.describe_image_version.assert_called_with(
        "multi-py-conda-image", None
    )
    mock_sagemaker_client.describe_app_image_config.assert_called_with(
        "multi-py-conda-image-config"
    )


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_INTERNAL_METADATA)
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.studio_image_metadata.get_sagemaker_client"
)
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.studio_image_metadata.get_user_profile_name"
)
async def test_studio_third_party_image_with_version(
    mock_get_user_profile_name,
    mock_get_sagemaker_client,
    mock_internal_metadata,
):
    mock_get_user_profile_name.return_value = "user-profile-test"
    mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
    mock_sagemaker_client.describe_domain.return_value = MOCK_DESCRIBE_DOMAIN
    mock_sagemaker_client.describe_image_version.return_value = (
        MOCK_DESCRIBE_IMAGE_VERSION
    )
    mock_sagemaker_client.describe_app_image_config.return_value = (
        MOCK_DESCRIBE_APP_IMAGE_CONFIG
    )
    mock_sagemaker_client.describe_user_profile.return_value = (
        MOCK_DESCRIBE_USER_PROFILE
    )

    mock_get_sagemaker_client.return_value = mock_sagemaker_client
    test_image_arn = (
        "arn:aws:sagemaker:us-east-1:177118115371:image-version/multi-py-conda-image/2"
    )
    test_region = "us-west-2"
    image_metadata = await get_image_metadata_studio(test_image_arn, test_region)
    assert image_metadata.image_owner == "Customer Owned"
    assert image_metadata.mount_path == "/home/sagemaker-user"
    assert image_metadata.uid == "1000"
    assert image_metadata.gid == "100"
    mock_sagemaker_client.describe_image_version.assert_called_with(
        "multi-py-conda-image", 2
    )
    mock_sagemaker_client.describe_app_image_config.assert_called_with(
        "multi-py-conda-image-config"
    )

@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_INTERNAL_METADATA)
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.studio_image_metadata.get_sagemaker_client"
)
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.studio_image_metadata.get_user_profile_name"
)
async def test_shared_sapce_app_with_byoi(mock_get_user_profile_name, mock_get_sagemaker_client,
    mock_internal_metadata,):
    mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
    mock_sagemaker_client.describe_domain.return_value = MOCK_DESCRIBE_DOMAIN
    # Test will throw an exception if shared space code path is not taken
    mock_sagemaker_client.describe_user_profile.side_effect = Exception("It is a shared space app, so no user profile app")
    mock_get_user_profile_name.return_value = None
    mock_sagemaker_client.describe_space.return_value = (
        MOCK_DESCRIBE_SPACE_SETTINGS
    )
    mock_sagemaker_client.describe_image_version.return_value = (
        MOCK_DESCRIBE_IMAGE_VERSION
    )
    mock_sagemaker_client.describe_app_image_config.return_value = (
        MOCK_DESCRIBE_APP_IMAGE_CONFIG
    )

    mock_get_sagemaker_client.return_value = mock_sagemaker_client
    test_image_arn = (
        "arn:aws:sagemaker:us-east-1:177118115371:image-version/multi-py-conda-image/2"
    )
    test_region = "us-west-2"

    image_metadata = await get_image_metadata_studio(test_image_arn, test_region)
    assert image_metadata.image_owner == "Customer Owned"
    assert image_metadata.mount_path == "/home/sagemaker-user"
    assert image_metadata.uid == "1000"
    assert image_metadata.gid == "100"
    mock_sagemaker_client.describe_image_version.assert_called_with(
        "multi-py-conda-image", 2
    )
    mock_sagemaker_client.describe_app_image_config.assert_called_with(
        "multi-py-conda-image"
    )
