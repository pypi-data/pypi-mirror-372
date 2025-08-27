import os
import pytest

from sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata import (
    get_image_metadata_jupyterlab,
)
from sagemaker_studio_jupyter_scheduler.util.aws_clients import SageMakerAsyncBoto3Client
from unittest.mock import AsyncMock, patch
from jupyter_scheduler.exceptions import SchedulerError


class TestJupyterLabImageMetadata:
    TST_DOMAIN_ID = "d-123456789"
    TST_SPACE_NAME = "test-space-name"
    TST_APP_TYPE = "JupyterLab"
    TST_APP_NAME = "default"

    @pytest.mark.asyncio
    async def test_getImageMetadataJupyterlab_1pImage_happyCase(self):
        # Setup
        os.environ["AWS_INTERNAL_IMAGE_OWNER"] = "jupyterlab"
        os.environ["SAGEMAKER_INTERNAL_IMAGE_URI"] = "tst-image-uri"

        # Test
        image_metadata = await get_image_metadata_jupyterlab()

        # Asserts
        assert image_metadata.image_arn == "tst-image-uri"
        assert image_metadata.image_display_name == "SageMaker Distribution"
        assert image_metadata.image_owner == "jupyterlab"
        assert image_metadata.ecr_uri == "tst-image-uri"
        assert image_metadata.mount_path == "/home/sagemaker-user"
        assert image_metadata.uid == "1000"
        assert image_metadata.gid == "100"

    @pytest.mark.asyncio
    async def test_getImageMetadataJupyterlab_1pImage_noEcrUri_schedulerError(self):
        # Setup
        os.environ["AWS_INTERNAL_IMAGE_OWNER"] = "jupyterlab"
        if os.environ.get("SAGEMAKER_INTERNAL_IMAGE_URI", None):
            del os.environ["SAGEMAKER_INTERNAL_IMAGE_URI"]

        # Test and Asserts
        with pytest.raises(SchedulerError) as excinfo:
            image_metadata = await get_image_metadata_jupyterlab()
        assert "Unable to find metadata for current JupyterLab app" in str(
            excinfo.value
        )

    @pytest.mark.asyncio
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_domain_id"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_space_name"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_app_type"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_app_name"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_sagemaker_client"
    )
    async def test_getImageMetadataJupyterlab_customImage_imageProvidedIsAttachedToDomain_happyCase(
        self,
        mock_get_sagemaker_client,
        mock_get_app_name,
        mock_get_app_type,
        mock_get_space_name,
        mock_get_domain_id,
    ):
        # Setup
        os.environ["AWS_INTERNAL_IMAGE_OWNER"] = "Custom"
        os.environ["SAGEMAKER_INTERNAL_IMAGE_URI"] = "tst-image-uri"

        mock_get_domain_id.return_value = self.TST_DOMAIN_ID
        mock_get_space_name.return_value = self.TST_SPACE_NAME
        mock_get_app_type.return_value = self.TST_APP_TYPE
        mock_get_app_name.return_value = self.TST_APP_NAME

        TST_IMAGE_NAME = "tst-custom-image"
        TST_IMAGE_DISPLAY_NAME = "tst-custom-display-image"
        TST_IMAGE_ARN = (
            "arn:aws:sagemaker:us-west-2:123456789123:image/tst-custom-image"
        )
        TST_IMAGE_ECR_URI = "tst-custom-image-uri"
        TST_MOUNT_PATH = "/home/custom-mount-path"
        TST_UID = "123"
        TST_GID = "456"

        mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
        mock_sagemaker_client.describe_domain.return_value = {
            "DefaultUserSettings": {
                "JupyterLabAppSettings": {
                    "CustomImages": [
                        {
                            "ImageName": "tst-custom-image",
                            "AppImageConfigName": "tst-custom-app-image-config",
                        },
                        {
                            "ImageName": "tst-custom-image-1",
                            "AppImageConfigName": "tst-custom-app-image-config-1",
                        },
                    ]
                },
            }
        }
        mock_sagemaker_client.describe_user_profile.return_value = {
            "UserSettings": {
                "JupyterLabAppSettings": {
                    "CustomImages": [
                        {
                            "ImageName": "tst-custom-image-2",
                            "AppImageConfigName": "tst-custom-app-image-config-2",
                        },
                    ]
                },
            }
        }
        mock_sagemaker_client.describe_space.return_value = {
            "OwnershipSettings": {
                "OwnerUserProfileName": "test-user-profile",
            }
        }
        mock_sagemaker_client.describe_app.return_value = {
            "ResourceSpec": {
                "SageMakerImageArn": TST_IMAGE_ARN,
            }
        }
        mock_sagemaker_client.describe_image_version.return_value = {
            "ImageArn": TST_IMAGE_ARN,
            "BaseImage": TST_IMAGE_ECR_URI,
        }
        mock_sagemaker_client.describe_image.return_value = {
            "DisplayName": TST_IMAGE_DISPLAY_NAME,
            "ImageArn": TST_IMAGE_ECR_URI,
            "ImageName": TST_IMAGE_ECR_URI,
            "Verrsion": 1,
        }
        mock_sagemaker_client.describe_app_image_config.return_value = {
            "JupyterLabAppImageConfig": {
                "FileSystemConfig": {
                    "MountPath": TST_MOUNT_PATH,
                    "DefaultUid": TST_UID,
                    "DefaultGid": TST_GID,
                }
            }
        }
        mock_get_sagemaker_client.return_value = mock_sagemaker_client

        # Test
        image_metadata = await get_image_metadata_jupyterlab()

        # Asserts
        mock_sagemaker_client.describe_app.assert_called_with(
            self.TST_DOMAIN_ID,
            self.TST_SPACE_NAME,
            self.TST_APP_TYPE,
            self.TST_APP_NAME,
        )
        mock_sagemaker_client.describe_image_version.assert_called_with(
            TST_IMAGE_NAME, None
        )
        mock_sagemaker_client.describe_space.assert_called_with(
            self.TST_DOMAIN_ID, self.TST_SPACE_NAME
        )
        mock_sagemaker_client.describe_domain.assert_called_with(self.TST_DOMAIN_ID)
        mock_sagemaker_client.describe_user_profile.assert_called_with(
            self.TST_DOMAIN_ID, "test-user-profile"
        )
        mock_sagemaker_client.describe_image.assert_called_with(TST_IMAGE_NAME)
        mock_sagemaker_client.describe_app_image_config.assert_called_with(
            "tst-custom-app-image-config"
        )

        assert image_metadata.image_arn == TST_IMAGE_ARN
        assert image_metadata.image_display_name == TST_IMAGE_DISPLAY_NAME
        assert image_metadata.ecr_uri == TST_IMAGE_ECR_URI
        assert image_metadata.mount_path == TST_MOUNT_PATH
        assert image_metadata.uid == TST_UID
        assert image_metadata.gid == TST_GID


    @pytest.mark.asyncio
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_domain_id"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_space_name"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_app_type"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_app_name"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_sagemaker_client"
    )
    async def test_getImageMetadataJupyterlab_customImage_imageVersionProvidedIsAttachedToDomain_happyCase(
        self,
        mock_get_sagemaker_client,
        mock_get_app_name,
        mock_get_app_type,
        mock_get_space_name,
        mock_get_domain_id,
    ):
        # Setup
        os.environ["AWS_INTERNAL_IMAGE_OWNER"] = "Custom"
        os.environ["SAGEMAKER_INTERNAL_IMAGE_URI"] = "tst-image-uri"

        mock_get_domain_id.return_value = self.TST_DOMAIN_ID
        mock_get_space_name.return_value = self.TST_SPACE_NAME
        mock_get_app_type.return_value = self.TST_APP_TYPE
        mock_get_app_name.return_value = self.TST_APP_NAME

        TST_IMAGE_NAME = "tst-custom-image"
        TST_IMAGE_DISPLAY_NAME = "tst-custom-display-image"
        TST_IMAGE_ARN = (
            "arn:aws:sagemaker:us-west-2:123456789123:image-version/tst-custom-image/1"
        )
        TST_IMAGE_ECR_URI = "tst-custom-image-uri"
        TST_MOUNT_PATH = "/home/custom-mount-path"
        TST_UID = "123"
        TST_GID = "456"

        mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
        mock_sagemaker_client.describe_domain.return_value = {
            "DefaultUserSettings": {
                "JupyterLabAppSettings": {
                    "CustomImages": [
                        {
                            "ImageName": "tst-custom-image",
                            "AppImageConfigName": "tst-custom-app-image-config",
                        },
                        {
                            "ImageName": "tst-custom-image-1",
                            "AppImageConfigName": "tst-custom-app-image-config-1",
                        },
                    ]
                },
            }
        }
        mock_sagemaker_client.describe_user_profile.return_value = {
            "UserSettings": {
                "JupyterLabAppSettings": {
                    "CustomImages": [
                        {
                            "ImageName": "tst-custom-image-2",
                            "AppImageConfigName": "tst-custom-app-image-config-2",
                        },
                    ]
                },
            }
        }
        mock_sagemaker_client.describe_space.return_value = {
            "OwnershipSettings": {
                "OwnerUserProfileName": "test-user-profile",
            }
        }
        mock_sagemaker_client.describe_app.return_value = {
            "ResourceSpec": {
                "SageMakerImageArn": TST_IMAGE_ARN,
            }
        }
        mock_sagemaker_client.describe_image_version.return_value = {
            "ImageArn": TST_IMAGE_ARN,
            "BaseImage": TST_IMAGE_ECR_URI,
        }
        mock_sagemaker_client.describe_image.return_value = {
            "DisplayName": TST_IMAGE_DISPLAY_NAME,
            "ImageArn": TST_IMAGE_ECR_URI,
            "ImageName": TST_IMAGE_ECR_URI,
            "Verrsion": 1,
        }
        mock_sagemaker_client.describe_app_image_config.return_value = {
            "JupyterLabAppImageConfig": {
                "FileSystemConfig": {
                    "MountPath": TST_MOUNT_PATH,
                    "DefaultUid": TST_UID,
                    "DefaultGid": TST_GID,
                }
            }
        }
        mock_get_sagemaker_client.return_value = mock_sagemaker_client

        # Test
        image_metadata = await get_image_metadata_jupyterlab()

        # Asserts
        mock_sagemaker_client.describe_app.assert_called_with(
            self.TST_DOMAIN_ID,
            self.TST_SPACE_NAME,
            self.TST_APP_TYPE,
            self.TST_APP_NAME,
        )
        mock_sagemaker_client.describe_image_version.assert_called_with(
            TST_IMAGE_NAME, 1
        )
        mock_sagemaker_client.describe_space.assert_called_with(
            self.TST_DOMAIN_ID, self.TST_SPACE_NAME
        )
        mock_sagemaker_client.describe_domain.assert_called_with(self.TST_DOMAIN_ID)
        mock_sagemaker_client.describe_user_profile.assert_called_with(
            self.TST_DOMAIN_ID, "test-user-profile"
        )
        mock_sagemaker_client.describe_image.assert_called_with(TST_IMAGE_NAME)
        mock_sagemaker_client.describe_app_image_config.assert_called_with(
            "tst-custom-app-image-config"
        )

        assert image_metadata.image_arn == TST_IMAGE_ARN
        assert image_metadata.image_display_name == TST_IMAGE_DISPLAY_NAME
        assert image_metadata.ecr_uri == TST_IMAGE_ECR_URI
        assert image_metadata.mount_path == TST_MOUNT_PATH
        assert image_metadata.uid == TST_UID
        assert image_metadata.gid == TST_GID

    
    @pytest.mark.asyncio
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_domain_id"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_space_name"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_app_type"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_app_name"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_sagemaker_client"
    )
    async def test_getImageMetadataJupyterlab_customImage_imageProvidedIsAttachedToDomain_mountPathUidGidNotSpecified_shouldUseDefaultUidGid(
        self,
        mock_get_sagemaker_client,
        mock_get_app_name,
        mock_get_app_type,
        mock_get_space_name,
        mock_get_domain_id,
    ):
       # Setup
        os.environ["AWS_INTERNAL_IMAGE_OWNER"] = "Custom"
        os.environ["SAGEMAKER_INTERNAL_IMAGE_URI"] = "tst-image-uri"

        mock_get_domain_id.return_value = self.TST_DOMAIN_ID
        mock_get_space_name.return_value = self.TST_SPACE_NAME
        mock_get_app_type.return_value = self.TST_APP_TYPE
        mock_get_app_name.return_value = self.TST_APP_NAME

        TST_IMAGE_NAME = "tst-custom-image"
        TST_IMAGE_DISPLAY_NAME = "tst-custom-display-image"
        TST_IMAGE_ARN = (
            "arn:aws:sagemaker:us-west-2:123456789123:image-version/tst-custom-image/1"
        )
        TST_IMAGE_ECR_URI = "tst-custom-image-uri"

        mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
        mock_sagemaker_client.describe_domain.return_value = {
            "DefaultUserSettings": {
                "JupyterLabAppSettings": {
                    "CustomImages": [
                        {
                            "ImageName": "tst-custom-image",
                            "AppImageConfigName": "tst-custom-app-image-config",
                        },
                    ]
                },
            }
        }
        mock_sagemaker_client.describe_user_profile.return_value = {
            "UserSettings": {}
        }
        mock_sagemaker_client.describe_space.return_value = {
            "OwnershipSettings": {
                "OwnerUserProfileName": "test-user-profile",
            }
        }
        mock_sagemaker_client.describe_app.return_value = {
            "ResourceSpec": {
                "SageMakerImageArn": TST_IMAGE_ARN,
            }
        }
        mock_sagemaker_client.describe_image_version.return_value = {
            "ImageArn": TST_IMAGE_ARN,
            "BaseImage": TST_IMAGE_ECR_URI,
        }
        mock_sagemaker_client.describe_image.return_value = {
            "DisplayName": TST_IMAGE_DISPLAY_NAME,
            "ImageArn": TST_IMAGE_ECR_URI,
            "ImageName": TST_IMAGE_ECR_URI,
            "Verrsion": 1,
        }
        mock_sagemaker_client.describe_app_image_config.return_value = {
            "JupyterLabAppImageConfig": {}
        }
        mock_get_sagemaker_client.return_value = mock_sagemaker_client

        # Test
        image_metadata = await get_image_metadata_jupyterlab()

        # Asserts
        mock_sagemaker_client.describe_app.assert_called_with(
            self.TST_DOMAIN_ID,
            self.TST_SPACE_NAME,
            self.TST_APP_TYPE,
            self.TST_APP_NAME,
        )
        mock_sagemaker_client.describe_image_version.assert_called_with(
            TST_IMAGE_NAME, 1
        )
        mock_sagemaker_client.describe_space.assert_called_with(
            self.TST_DOMAIN_ID, self.TST_SPACE_NAME
        )
        mock_sagemaker_client.describe_domain.assert_called_with(self.TST_DOMAIN_ID)
        mock_sagemaker_client.describe_user_profile.assert_called_with(
            self.TST_DOMAIN_ID, "test-user-profile"
        )
        mock_sagemaker_client.describe_image.assert_called_with(TST_IMAGE_NAME)
        mock_sagemaker_client.describe_app_image_config.assert_called_with(
            "tst-custom-app-image-config"
        )

        assert image_metadata.image_arn == TST_IMAGE_ARN
        assert image_metadata.image_display_name == TST_IMAGE_DISPLAY_NAME
        assert image_metadata.ecr_uri == TST_IMAGE_ECR_URI
        assert image_metadata.mount_path == "/home/sagemaker-user"
        assert image_metadata.uid == "1000"
        assert image_metadata.gid == "100"


    @pytest.mark.asyncio
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_domain_id"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_space_name"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_app_type"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_app_name"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_sagemaker_client"
    )
    async def test_getImageMetadataJupyterlab_customImage_imageProvidedIsAttachedToUserProfile_happyCase(
        self,
        mock_get_sagemaker_client,
        mock_get_app_name,
        mock_get_app_type,
        mock_get_space_name,
        mock_get_domain_id,
    ):
        # Setup
        os.environ["AWS_INTERNAL_IMAGE_OWNER"] = "Custom"
        os.environ["SAGEMAKER_INTERNAL_IMAGE_URI"] = "tst-image-uri"

        mock_get_domain_id.return_value = self.TST_DOMAIN_ID
        mock_get_space_name.return_value = self.TST_SPACE_NAME
        mock_get_app_type.return_value = self.TST_APP_TYPE
        mock_get_app_name.return_value = self.TST_APP_NAME

        TST_IMAGE_NAME = "tst-custom-image-2"
        TST_IMAGE_DISPLAY_NAME = "tst-custom-display-image-2"
        TST_IMAGE_ARN = (
            "arn:aws:sagemaker:us-west-2:123456789123:image/tst-custom-image-2"
        )
        TST_IMAGE_ECR_URI = "tst-custom-image-uri-2"
        TST_MOUNT_PATH = "/home/custom-mount-path"
        TST_UID = "123"
        TST_GID = "456"

        mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
        mock_sagemaker_client.describe_domain.return_value = {
            "DefaultUserSettings": {
                "JupyterLabAppSettings": {
                    "CustomImages": [
                        {
                            "ImageName": "tst-custom-image",
                            "AppImageConfigName": "tst-custom-app-image-config",
                        },
                        {
                            "ImageName": "tst-custom-image-1",
                            "AppImageConfigName": "tst-custom-app-image-config-1",
                        },
                    ]
                },
            }
        }
        mock_sagemaker_client.describe_user_profile.return_value = {
            "UserSettings": {
                "JupyterLabAppSettings": {
                    "CustomImages": [
                        {
                            "ImageName": "tst-custom-image-2",
                            "AppImageConfigName": "tst-custom-app-image-config-2",
                        },
                    ]
                },
            }
        }
        mock_sagemaker_client.describe_space.return_value = {
            "OwnershipSettings": {
                "OwnerUserProfileName": "test-user-profile",
            }
        }
        mock_sagemaker_client.describe_app.return_value = {
            "ResourceSpec": {
                "SageMakerImageArn": TST_IMAGE_ARN,
            }
        }
        mock_sagemaker_client.describe_image_version.return_value = {
            "ImageArn": TST_IMAGE_ARN,
            "BaseImage": TST_IMAGE_ECR_URI,
        }
        mock_sagemaker_client.describe_image.return_value = {
            "DisplayName": TST_IMAGE_DISPLAY_NAME,
            "ImageArn": TST_IMAGE_ECR_URI,
            "ImageName": TST_IMAGE_ECR_URI,
            "Verrsion": 1,
        }
        mock_sagemaker_client.describe_app_image_config.return_value = {
            "JupyterLabAppImageConfig": {
                "FileSystemConfig": {
                    "MountPath": TST_MOUNT_PATH,
                    "DefaultUid": TST_UID,
                    "DefaultGid": TST_GID,
                }
            }
        }
        mock_get_sagemaker_client.return_value = mock_sagemaker_client

        # Test
        image_metadata = await get_image_metadata_jupyterlab()

        # Asserts
        mock_sagemaker_client.describe_app.assert_called_with(
            self.TST_DOMAIN_ID,
            self.TST_SPACE_NAME,
            self.TST_APP_TYPE,
            self.TST_APP_NAME,
        )
        mock_sagemaker_client.describe_image_version.assert_called_with(
            TST_IMAGE_NAME, None
        )
        mock_sagemaker_client.describe_space.assert_called_with(
            self.TST_DOMAIN_ID, self.TST_SPACE_NAME
        )
        mock_sagemaker_client.describe_domain.assert_called_with(self.TST_DOMAIN_ID)
        mock_sagemaker_client.describe_user_profile.assert_called_with(
            self.TST_DOMAIN_ID, "test-user-profile"
        )
        mock_sagemaker_client.describe_image.assert_called_with(TST_IMAGE_NAME)
        mock_sagemaker_client.describe_app_image_config.assert_called_with(
            "tst-custom-app-image-config-2"
        )

        assert image_metadata.image_arn == TST_IMAGE_ARN
        assert image_metadata.image_display_name == TST_IMAGE_DISPLAY_NAME
        assert image_metadata.ecr_uri == TST_IMAGE_ECR_URI
        assert image_metadata.mount_path == TST_MOUNT_PATH
        assert image_metadata.uid == TST_UID
        assert image_metadata.gid == TST_GID

    @pytest.mark.asyncio
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_domain_id"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_space_name"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_app_type"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_app_name"
    )
    @patch(
        "sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata.get_sagemaker_client"
    )
    async def test_getImageMetadataJupyterlab_customImage_invalidImageArnProvided_schedulerError(
        self,
        mock_get_sagemaker_client,
        mock_get_app_name,
        mock_get_app_type,
        mock_get_space_name,
        mock_get_domain_id,
    ):
        # Setup
        os.environ["AWS_INTERNAL_IMAGE_OWNER"] = "Custom"
        os.environ["SAGEMAKER_INTERNAL_IMAGE_URI"] = "tst-image-uri"

        mock_get_domain_id.return_value = "d-123456789"
        mock_get_space_name.return_value = "test-space-name"
        mock_get_app_type.return_value = "JupyterLab"
        mock_get_app_name.return_value = "default"

        TST_IMAGE_ARN = "invalid-image-arn"

        mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
        mock_sagemaker_client.describe_app.return_value = {
            "ResourceSpec": {
                "SageMakerImageArn": TST_IMAGE_ARN,
            }
        }
        mock_get_sagemaker_client.return_value = mock_sagemaker_client

        # Test and Asserts
        with pytest.raises(SchedulerError) as excinfo:
            image_metadata = await get_image_metadata_jupyterlab()
        assert "Unable to find metadata for current JupyterLab app" in str(
            excinfo.value
        )
