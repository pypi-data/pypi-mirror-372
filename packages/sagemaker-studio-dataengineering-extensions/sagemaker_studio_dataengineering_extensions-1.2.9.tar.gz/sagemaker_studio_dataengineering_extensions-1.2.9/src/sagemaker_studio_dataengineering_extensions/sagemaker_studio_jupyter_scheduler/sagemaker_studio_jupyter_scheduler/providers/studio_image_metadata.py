import asyncio
import json
from typing import Dict
from sagemaker_studio_jupyter_scheduler.util.app_metadata import (
    get_domain_id,
    get_user_profile_name,
    get_shared_space_name,
)
from sagemaker_studio_jupyter_scheduler.util.aws_clients import get_sagemaker_client
from sagemaker_studio_jupyter_scheduler.util.constants import SAGEMAKER_RESOURCE_METADATA_FILE

from sagemaker_studio_jupyter_scheduler.model.models import ImageMetadata
from jupyter_scheduler.exceptions import SchedulerError

SAGEMAKER_INTERNAL_METADATA_FILE = "/opt/.sagemakerinternal/internal-metadata.json"
APP_IMAGE_ARN_KEY = "ImageOrVersionArn"


def get_app_type() -> str:
    resource_metadata = get_metadata_from_config_file(SAGEMAKER_RESOURCE_METADATA_FILE)
    return resource_metadata.get("AppType")
 
 
def get_metadata_from_config_file(
    filepath: str = SAGEMAKER_INTERNAL_METADATA_FILE,
) -> Dict:
    metadata = {}
    with open(filepath, "r") as file:
        metadata = json.load(file)
    return metadata


def get_first_party_image(image_arn: str, metadata: Dict) -> ImageMetadata:
    image_metadata = next(
        (
            ImageMetadata(
                image_arn=image["ImageOrVersionArn"],
                ecr_uri=image["AppImageUri"],
                mount_path=image
                    .get("AppImageConfig", {})
                    .get("FileSystemConfig", {})
                    .get("MountPath", "/root"),
                uid=image
                    .get("AppImageConfig", {})
                    .get("FileSystemConfig", {})
                    .get("DefaultUid", 0),
                gid=image
                    .get("AppImageConfig", {})
                    .get("FileSystemConfig", {})
                    .get("DefaultGid", 0)
            )
            for image in metadata.get("FirstPartyImages", [])
            if image["ImageOrVersionArn"] == image_arn
        ),
        None,
    )
    return image_metadata
    

async def _fetch_custom_images(sm_client):
    DEFAULT_USER_SETTINGS_KEY = "DefaultUserSettings"
    USER_SETTINGS_KEY = "UserSettings"
    # we could be in a shared space app
    # TODO: Refactor shared space as a supported runtime environment
    api_calls = [sm_client.describe_domain(get_domain_id())]

    if get_user_profile_name():
        api_calls.append(
            sm_client.describe_user_profile(
                get_domain_id(), get_user_profile_name()
            )
        )
    else:
        api_calls.append(
            sm_client.describe_space(get_domain_id(), get_shared_space_name())
        )
        DEFAULT_USER_SETTINGS_KEY = "DefaultSpaceSettings"
        USER_SETTINGS_KEY = "SpaceSettings"

    # user details is synonymous to space details
    [domain_details, user_details] = await asyncio.gather(*api_calls)

    return domain_details.get(DEFAULT_USER_SETTINGS_KEY, {}).get(
        "KernelGatewayAppSettings", {}
    ).get("CustomImages", []) + user_details.get(USER_SETTINGS_KEY, {}).get(
        "KernelGatewayAppSettings", {}
    ).get(
        "CustomImages", []
    )


async def get_third_party_image(image_arn: str, metadata: Dict) -> ImageMetadata:
    sagemaker_client = get_sagemaker_client()
    for third_party_image_metadata in metadata.get("CustomImages", []):
        if image_arn == third_party_image_metadata.get(APP_IMAGE_ARN_KEY):
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

            [image_version, custom_images] = await asyncio.gather(
                sagemaker_client.describe_image_version(
                    image_name, image_version_number
                ),
                _fetch_custom_images(sagemaker_client),
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
                "KernelGatewayImageConfig", {}
            ).get("FileSystemConfig", {})

            return ImageMetadata(
                image_arn=image_version.get("ImageArn"),
                ecr_uri=image_version.get("BaseImage"),
                # default values from here - https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateAppImageConfig.html
                mount_path=file_system_config.get("MountPath", "/home/sagemaker-user"),
                uid=str(file_system_config.get("DefaultUid", 0)),
                gid=str(file_system_config.get("DefaultGid", 0)),
            )


async def get_image_metadata_studio(image_arn: str, aws_region: str) -> ImageMetadata:
    metadata = {}
    # read internal-metadata.json file every time to avoid caching old custom image details
    # this will add a little bit of overhead to read a file from EFS but happens only during create job
    # we have good indication to let the customers with a spinning wheel
    # ideally this can be replaced with an api call, for now we are depending on the file
    metadata = get_metadata_from_config_file()

    # first check for 1p images, if no match
    image_metadata = get_first_party_image(image_arn, metadata)

    if not image_metadata:
        image_metadata = await get_third_party_image(image_arn, metadata)

    if not image_metadata:
        raise SchedulerError(
            f"Unable to find metadata for image arn {image_arn} in region: {aws_region}"
        )

    return image_metadata
