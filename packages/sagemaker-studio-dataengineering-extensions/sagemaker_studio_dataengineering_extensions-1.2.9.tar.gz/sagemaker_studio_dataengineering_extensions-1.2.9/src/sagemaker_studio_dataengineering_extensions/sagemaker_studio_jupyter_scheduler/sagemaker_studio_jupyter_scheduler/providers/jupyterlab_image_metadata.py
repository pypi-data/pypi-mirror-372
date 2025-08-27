import os
import json
import asyncio

from jupyter_scheduler.exceptions import SchedulerError

from sagemaker_studio_jupyter_scheduler.util.app_metadata import (
    get_domain_id,
    get_space_name,
    get_app_type,
    get_app_name,
)
from sagemaker_studio_jupyter_scheduler.util.aws_clients import get_sagemaker_client
from sagemaker_studio_jupyter_scheduler.model.models import ImageMetadata


IMAGE_OWNER_ENV_VAR_KEY = "AWS_INTERNAL_IMAGE_OWNER"
IMAGE_URI_ENV_VAR_KEY = "SAGEMAKER_INTERNAL_IMAGE_URI"


def is_custom_image():
    return os.environ.get("AWS_INTERNAL_IMAGE_OWNER") == "Custom"


# For JupyterLab apps, SageMaker Distribution image is the first party image
def get_first_party_image():
    ecr_uri = os.environ.get(IMAGE_URI_ENV_VAR_KEY, None)
    if ecr_uri:
        return ImageMetadata(
            image_arn=ecr_uri,
            image_display_name='SageMaker Distribution',
            image_owner='jupyterlab',
            ecr_uri=ecr_uri,
            # UID, GID and mount_path for SageMaker Distribution image is fixed
            mount_path="/home/sagemaker-user",
            uid="1000",
            gid="100",
        )
    return None


async def _fetch_custom_images(sm_client):
    DEFAULT_USER_SETTINGS_KEY = "DefaultUserSettings"
    USER_SETTINGS_KEY = "UserSettings"
    api_calls = [sm_client.describe_domain(get_domain_id())]

    # For JupyterLab apps, we will get user profile ARN from 'DescribeSpace' API calls
    space_details = await sm_client.describe_space(
        get_domain_id(), get_space_name()
    )
    user_profile_name = space_details.get("OwnershipSettings", {}).get("OwnerUserProfileName", None)

    if user_profile_name:
        api_calls.append(
            sm_client.describe_user_profile(
                get_domain_id(), user_profile_name
            )
        )

    # For JupyterLab apps, custom image settings can only be configured at domain or user
    # profile level
    [domain_details, user_details] = await asyncio.gather(*api_calls)

    return domain_details.get(DEFAULT_USER_SETTINGS_KEY, {}).get(
        "JupyterLabAppSettings", {}
    ).get("CustomImages", []) + user_details.get(USER_SETTINGS_KEY, {}).get(
        "JupyterLabAppSettings", {}
    ).get(
        "CustomImages", []
    )


async def get_image_or_version_arn(sm_client):
    app_details = await sm_client.describe_app(
        get_domain_id(), get_space_name(), get_app_type(), get_app_name()
    )
    resource_spec = app_details.get("ResourceSpec", {})

    app_image_version_arn = resource_spec.get("SageMakerImageVersionArn", None)
    
    if not app_image_version_arn:
        return resource_spec.get("SageMakerImageArn", None)
    return app_image_version_arn


async def get_third_party_image() -> ImageMetadata:
    sagemaker_client = get_sagemaker_client()
    image_arn = await get_image_or_version_arn(sagemaker_client)
    image_name = None
    image_version_number = None

    if ":image/" in image_arn:
        image_name = image_arn.split(":image/")[1]
    elif ":image-version/" in image_arn:
        [
            image_arn_prefix,
            image_name,
            image_version_number,
        ] = image_arn.split("/")
        image_version_number = int(image_version_number)
    else:
        raise ValueError(f"Invalid image arn: {image_arn}")

    [image_version, custom_images, image_details] = await asyncio.gather(
        sagemaker_client.describe_image_version(
            image_name, image_version_number
        ),
        _fetch_custom_images(sagemaker_client),
        sagemaker_client.describe_image(image_name),
    )

    # Search custom images to find image config name
    app_image_config_name = next(
        image["AppImageConfigName"]
        for image in custom_images
        if image["ImageName"] == image_name
    )
    app_image_config = await sagemaker_client.describe_app_image_config(
        app_image_config_name
    )
    file_system_config = app_image_config.get(
        "JupyterLabAppImageConfig", {}
    ).get("FileSystemConfig", {})

    return ImageMetadata(
        image_arn=image_version.get("ImageArn"),
        image_display_name=image_details.get("DisplayName"),
        ecr_uri=image_version.get("BaseImage"),
        # default values from here - https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateAppImageConfig.html
        mount_path=file_system_config.get("MountPath", "/home/sagemaker-user"),
        uid=str(file_system_config.get("DefaultUid", 1000)),
        gid=str(file_system_config.get("DefaultGid", 100)),
    )


async def get_image_metadata_jupyterlab() -> ImageMetadata:
    # For JupyterLab apps, we will always use the same image customer use to start JupyterLap
    # apps for notebook jobs

    if is_custom_image():
        try:
            return await get_third_party_image()
        except:
            raise SchedulerError(
                f"Unable to find metadata for current JupyterLab app"
            )
    else:
        image_metadata = get_first_party_image()
        if not image_metadata:
            raise SchedulerError(
                f"Unable to find metadata for current JupyterLab app"
            )
        return image_metadata
