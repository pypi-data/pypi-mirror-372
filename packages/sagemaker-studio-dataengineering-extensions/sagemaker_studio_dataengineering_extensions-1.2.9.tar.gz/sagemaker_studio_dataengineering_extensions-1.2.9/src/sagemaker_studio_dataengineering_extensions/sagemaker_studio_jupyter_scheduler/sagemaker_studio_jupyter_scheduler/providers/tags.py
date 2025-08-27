import logging
from sagemaker_studio_jupyter_scheduler.model.models import JobTag
from sagemaker_studio_jupyter_scheduler.util.app_metadata import (
    get_domain_id,
    get_sagemaker_environment,
    get_user_details,
)
from sagemaker_studio_jupyter_scheduler.util.aws_clients import get_sagemaker_client
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
)
from typing import Dict, List

from sagemaker_studio_jupyter_scheduler.model.models import UserTypes, UserDetails


def _deduplicate_tags(tags):
    unique_keys = set()
    deduplicated_list = []
    for tag in tags:
        key = tag["Key"]
        if key not in unique_keys:
            deduplicated_list.append(tag)
            unique_keys.add(key)
    return deduplicated_list


async def _get_studio_tags(
    user_details: UserDetails, logger: logging.Logger
) -> List[Dict[str, str]]:
    tags = []
    if user_details and user_details.user_id_key and user_details.user_id_value:
        tags += [
            {
                "Key": f"sagemaker:{user_details.user_id_key}-name",
                "Value": user_details.user_id_value,
            }
        ]
        sm_client = get_sagemaker_client()
        user_arns = []
        if user_details.user_id_key == UserTypes.SHARED_SPACE_USER:
            space_details = await sm_client.describe_space(
                domain_id=get_domain_id(), space_name=user_details.user_id_value
            )
            user_arns.append(space_details["SpaceArn"])

            owner_user_profile_name = space_details.get("OwnershipSettings", {}).get("OwnerUserProfileName", None)
            if owner_user_profile_name:
                tags += [
                    {
                        "Key": f"sagemaker:{UserTypes.PROFILE_USER}-name",
                        "Value": owner_user_profile_name,
                    }
                ]
                owner_user_profile_details = await sm_client.describe_user_profile(
                    domain_id=get_domain_id(), user_profile_name=owner_user_profile_name
                )
                user_arns.append(owner_user_profile_details["UserProfileArn"])
        else:
            user_profile = await sm_client.describe_user_profile(
                domain_id=get_domain_id(), user_profile_name=user_details.user_id_value
            )
            user_arns.append(user_profile["UserProfileArn"])

        user_tags = []
        for user_arn in user_arns:
          user_tags += (await sm_client.list_tags(resource_arn=user_arn))["Tags"]
        logger.info(f"user profile tags retrieved - {user_tags}")

        # filter any "aws:" internal tags, this is needed because Looseleaf adds aws: tags for beta & gamma stacks
        # this change will also protect us from any future internal aws: tags added by Sagemaker
        sanitized_tags = [
            tag for tag in user_tags if not tag["Key"].startswith("aws:")
        ]
        logger.info(f"sanitized user profile tags - {sanitized_tags}")
    return _deduplicate_tags(tags + sanitized_tags)


def _get_base_tags(
    job_name: str, notebook_name: str, headless_driver_version: str
) -> List[Dict[str, str]]:
    return [
        {"Key": "sagemaker:name", "Value": job_name},
        {"Key": "sagemaker:notebook-name", "Value": notebook_name},
        {"Key": "sagemaker:is-scheduling-notebook-job", "Value": "true"},
        {"Key": "sagemaker:is-studio-archived", "Value": "false"},
        {
            "Key": "sagemaker:headless-execution-version",
            "Value": headless_driver_version,
        },
    ]


async def get_resource_create_tags(
    job_name: str,
    notebook_name: str,
    headless_driver_version: str,
    logger: logging.Logger,
) -> List[Dict[str, str]]:
    tags = _get_base_tags(job_name, notebook_name, headless_driver_version)
    if (
        get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_STUDIO
        or get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB
    ):
        user_details = get_user_details()
        user_tags = await _get_studio_tags(user_details, logger)
        tags += user_tags

    logger.info(f"resource create tags - {tags}")

    return tags


def get_common_resource_tag_filters() -> List[Dict[str, str]]:
    return [
        {
            "Name": f"Tags.{JobTag.IS_STUDIO_ARCHIVED}",
            "Operator": "Equals",
            "Value": "false",
        },
    ]


def get_sub_expressions_filters() -> List[Dict[str, str]]:
    sub_expressions = [
        {
            "Filters": [
                {
                    "Name": f"Tags.{JobTag.IS_SCHEDULING_NOTEBOOK_JOB}",
                    "Operator": "Equals",
                    "Value": "true",
                },
                {
                    "Name": f"Tags.{JobTag.NOTEBOOK_JOB_ORIGIN}",
                    "Operator": "Equals",
                    "Value": "PIPELINE_STEP",
                },
            ],
            "Operator": "Or",
        },
    ]

    if (
        get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_STUDIO
        or get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB
    ):
        user_details = get_user_details()
        domain_id = get_domain_id()

        domain_tag_filters = [
            {
                "Filters": [
                    {
                        "Name": "Tags.sagemaker:domain-arn",
                        "Operator": "Contains",
                        "Value": domain_id,
                    },
                    {
                        "Name": "Tags.sagemaker:domain-name",
                        "Operator": "Equals",
                        "Value": domain_id,
                    },
                ],
                "Operator": "Or",
            },
        ]

        user_details_tag_filters = [
            {
                "SubExpressions": [
                    {
                        "Filters": [
                            {
                                "Name": f"Tags.sagemaker:user-profile-name",
                                "Operator": "NotExists",
                            },
                            {
                                "Name": f"Tags.sagemaker:shared-space-name",
                                "Operator": "NotExists",
                            }
                        ]
                    },
                    {
                        "Filters": [
                            {
                                "Name": f"Tags.sagemaker:{user_details.user_id_key}-name",
                                "Operator": "Equals",
                                "Value": user_details.user_id_value,
                            },
                        ]
                    },
                ],
                "Operator": "Or",
            },
        ]

        sub_expressions += domain_tag_filters + user_details_tag_filters

    return sub_expressions
