import json
import os
import sys

from botocore.session import Session
from sagemaker_studio_jupyter_scheduler.util.constants import SAGEMAKER_RESOURCE_METADATA_FILE
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironmentDetector,
)

from sagemaker_studio_jupyter_scheduler.model.models import UserTypes, UserDetails

app_metadata_file_location = SAGEMAKER_RESOURCE_METADATA_FILE


DEFAULT_REGION = "us-east-2"


def get_region_name():
    # Get region config in following order:
    # 1. AWS_REGION env var
    # 2. Region from AWS config (for example, through `aws configure`)
    # 3. AWS_DEFAULT_REGION env var
    # 4. If none of above are set, use us-east-2 (same as Studio Lab)
    region_config_chain = [
        os.environ.get(
            "AWS_REGION"
        ),  # this value is set for Studio, so we dont need any special environment specific logic
        Session().get_scoped_config().get("region"),
        os.environ.get("AWS_DEFAULT_REGION"),
        DEFAULT_REGION,
    ]
    for region_config in region_config_chain:
        if region_config is not None:
            return region_config

def get_space_type():
    return os.environ.get("SAGEMAKER_SPACE_TYPE_LOWERCASE")


def _get_app_metadata_file():
    try:
        with open(app_metadata_file_location) as file:
            return json.loads(file.read())
    except:
        return {}


def get_partition():
    return Session().get_partition_for_region(get_region_name())


def get_default_aws_region():
    return os.environ.get("AWS_DEFAULT_REGION")


def get_sagemaker_image():
    image_uri = os.environ.get("SAGEMAKER_INTERNAL_IMAGE_URI")
    image_version = os.environ.get("IMAGE_VERSION")
    if image_uri and image_version:
        return f'{image_uri}:{image_version}'
    elif image_uri:
        return f'{image_uri}'
    return "UNKNOWN"

def get_user_profile_name():
    return _get_app_metadata_file().get("UserProfileName")


def get_shared_space_name():
    return _get_app_metadata_file().get("SpaceName", "")


def get_domain_id():
    return _get_app_metadata_file().get("DomainId")


def get_space_name():
    return _get_app_metadata_file().get("SpaceName", "")


def get_app_type():
    return _get_app_metadata_file().get("AppType", "")


def get_app_name():
    return _get_app_metadata_file().get("ResourceName", "")


def get_user_details():
    user_details = None

    user_profile_name = get_user_profile_name()
    if user_profile_name:
        user_details = UserDetails(
            user_id_key=UserTypes.PROFILE_USER, user_id_value=user_profile_name
        )
    else:
        shared_space_name = get_shared_space_name()
        if shared_space_name:
            user_details = UserDetails(
                user_id_key=UserTypes.SHARED_SPACE_USER, user_id_value=shared_space_name
            )

    return user_details


def get_sagemaker_environment():
    return JupyterLabEnvironmentDetector().current_environment
