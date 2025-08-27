from unittest.mock import AsyncMock, MagicMock, patch
from sagemaker_studio_jupyter_scheduler.model.models import JobTag

import pytest
from sagemaker_studio_jupyter_scheduler.util.aws_clients import SageMakerAsyncBoto3Client
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
)
from sagemaker_studio_jupyter_scheduler.model.models import UserDetails, UserTypes
from sagemaker_studio_jupyter_scheduler.providers.tags import (
    get_resource_create_tags,
    get_common_resource_tag_filters,
    get_sub_expressions_filters,
)

TEST_JOB_NAME = "merged-code-base-notebook-job"
TEST_NOTEBOOK_NAME = "Analysis.ipynb"
TEST_HEADLESS_DRIVER_VERSION = "0.1.0"
TEST_USER_DETAILS_SHARED_SPACE = UserDetails(
    user_id_key=UserTypes.SHARED_SPACE_USER, user_id_value="collab1"
)
TEST_USER_DETAILS_PROFILE = UserDetails(
    user_id_key=UserTypes.PROFILE_USER, user_id_value="user-profile-1"
)

expected_base_tags = [
    {"Key": "sagemaker:name", "Value": TEST_JOB_NAME},
    {"Key": "sagemaker:notebook-name", "Value": TEST_NOTEBOOK_NAME},
    {"Key": "sagemaker:is-scheduling-notebook-job", "Value": "true"},
    {"Key": "sagemaker:is-studio-archived", "Value": "false"},
    {
        "Key": "sagemaker:headless-execution-version",
        "Value": TEST_HEADLESS_DRIVER_VERSION,
    },
]


@pytest.mark.asyncio
async def test_get_tags_for_standalone_environment():
    actual_tags = await get_resource_create_tags(
        TEST_JOB_NAME,
        TEST_NOTEBOOK_NAME,
        TEST_HEADLESS_DRIVER_VERSION,
        MagicMock(),
    )
    assert len(actual_tags) == len(expected_base_tags)
    pairs = zip(actual_tags, expected_base_tags)
    for x, y in pairs:
        assert x == y


MOCK_DESCRIBE_USER_PROFILE = {
    "UserProfileArn": "arn:aws:sagemaker:us-east-1:177118115371:user-profile/d-fnytsoocmwo1/user-profile-1",
}

TEST_USER_TAGS = [
    {"Key": "Tag 1 key", "Value": "Tag 1 value"},
    {"Key": "Tag 2 key", "Value": "Tag 2 value"},
    {"Key": "aws:stage", "Value": "loadtest"},
]

TEST_SPACE_TAGS = [
    {"Key": "Tag 1 key", "Value": "Tag 1 value"},
    {"Key": "Tag 3 key", "Value": "Tag 3 value"}
]

MOCK_SHARED_SPACE_LIST_TAGS_RESPONSE = {
    "Tags": TEST_SPACE_TAGS,
    "NextToken": "abc",
}

MOCK_LIST_TAGS_RESPONSE = {
    "Tags": TEST_USER_TAGS,
    "NextToken": "abc",
}

MOCK_DESCRIBE_SPACE_RESPONSE = {
    "SpaceArn": "arn:aws:sagemaker:us-east-1:177118115371:space/bhadrinp-scheduling",
    "OwnershipSettings": {
        "OwnerUserProfileName": "user-profile-1"
    }
}

MOCK_DOMAIN_ID_RESPONSE = "d-1a2b3c4d5e6f"

expected_common_resource_tag_filters = [
    {
        "Name": f"Tags.{JobTag.IS_STUDIO_ARCHIVED}",
        "Operator": "Equals",
        "Value": "false",
    },
]

expected_base_sub_expressions = [
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

expected_domain_tag_filters = [
    {
        "Filters": [
            {
                "Name": "Tags.sagemaker:domain-arn",
                "Operator": "Contains",
                "Value": MOCK_DOMAIN_ID_RESPONSE,
            },
            {
                "Name": "Tags.sagemaker:domain-name",
                "Operator": "Equals",
                "Value": MOCK_DOMAIN_ID_RESPONSE,
            },
        ],
        "Operator": "Or",
    },
]


@pytest.mark.asyncio
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_sagemaker_client")
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_sagemaker_environment")
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_user_details")
async def test_get_tags_for_studio_environment_profile(
        mock_user_details, mock_sagemaker_environment, mock_get_sagemaker_client
):
    mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
    mock_sagemaker_client.describe_user_profile.return_value = (
        MOCK_DESCRIBE_USER_PROFILE
    )
    mock_sagemaker_client.list_tags.return_value = MOCK_LIST_TAGS_RESPONSE
    mock_get_sagemaker_client.return_value = mock_sagemaker_client
    mock_user_details.return_value = TEST_USER_DETAILS_PROFILE
    mock_sagemaker_environment.return_value = JupyterLabEnvironment.SAGEMAKER_STUDIO
    actual_tags = await get_resource_create_tags(
        TEST_JOB_NAME,
        TEST_NOTEBOOK_NAME,
        TEST_HEADLESS_DRIVER_VERSION,
        MagicMock(),
    )

    expected_studio_tags = [
        {
            "Key": f"sagemaker:{TEST_USER_DETAILS_PROFILE.user_id_key}-name",
            "Value": TEST_USER_DETAILS_PROFILE.user_id_value,
        }
    ]
    expected_tags = (
            expected_base_tags + expected_studio_tags + TEST_USER_TAGS[:-1]
    )  # tag with aws: prefix should not  be included in the tags

    assert len(actual_tags) == len(expected_tags)

    pairs = zip(actual_tags, expected_tags)
    for x, y in pairs:
        assert x == y


@pytest.mark.asyncio
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_sagemaker_client")
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_sagemaker_environment")
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_user_details")
async def test_get_tags_for_studio_environment_shared_space(
        mock_user_details, mock_sagemaker_environment, mock_get_sagemaker_client
):
    mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
    mock_sagemaker_client.describe_space.return_value = MOCK_DESCRIBE_SPACE_RESPONSE
    # mock_sagemaker_client.list_tags.return_value = MOCK_SHARED_SPACE_LIST_TAGS_RESPONSE
    mock_sagemaker_client.describe_user_profile.return_value = MOCK_DESCRIBE_USER_PROFILE
    mock_sagemaker_client.list_tags.side_effect = [MOCK_SHARED_SPACE_LIST_TAGS_RESPONSE, MOCK_LIST_TAGS_RESPONSE]
    mock_get_sagemaker_client.return_value = mock_sagemaker_client
    mock_user_details.side_effect = [TEST_USER_DETAILS_SHARED_SPACE, TEST_USER_DETAILS_PROFILE]
    mock_sagemaker_environment.return_value = JupyterLabEnvironment.SAGEMAKER_STUDIO
    actual_tags = await get_resource_create_tags(
        TEST_JOB_NAME,
        TEST_NOTEBOOK_NAME,
        TEST_HEADLESS_DRIVER_VERSION,
        MagicMock(),
    )

    expected_studio_tags = [
        {
            "Key": f"sagemaker:{TEST_USER_DETAILS_SHARED_SPACE.user_id_key}-name",
            "Value": TEST_USER_DETAILS_SHARED_SPACE.user_id_value,
        },
        {
            "Key": f"sagemaker:{TEST_USER_DETAILS_PROFILE.user_id_key}-name",
            "Value": TEST_USER_DETAILS_PROFILE.user_id_value,
        }
    ]
    expected_tags = (
        expected_base_tags + expected_studio_tags + [
            {'Key': 'Tag 1 key', 'Value': 'Tag 1 value'},
            {'Key': 'Tag 3 key', 'Value': 'Tag 3 value'},
            {'Key': 'Tag 2 key', 'Value': 'Tag 2 value'}
    ]
    )  # tag with aws: prefix should not  be included in the tags

    assert len(actual_tags) == len(expected_tags)

    pairs = zip(actual_tags, expected_tags)
    for x, y in pairs:
        assert x == y


def test_get_common_resource_tag_filters():
    actual_tags = get_common_resource_tag_filters()
    assert len(actual_tags) == len(expected_common_resource_tag_filters)
    pairs = zip(actual_tags, expected_common_resource_tag_filters)
    for x, y in pairs:
        assert x == y


@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_sagemaker_environment")
def test_sub_expressions_filters_standalone(mock_sagemaker_environment):
    mock_sagemaker_environment.return_value = JupyterLabEnvironment.VANILLA_JUPYTERLAB

    assert expected_base_sub_expressions == get_sub_expressions_filters()


@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_domain_id")
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_user_details")
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_sagemaker_environment")
def test_sub_expressions_filters_shared_space(
        mock_sagemaker_environment, mock_user_details, mock_domain_id
):
    mock_sagemaker_environment.return_value = JupyterLabEnvironment.SAGEMAKER_STUDIO
    mock_user_details.return_value = TEST_USER_DETAILS_SHARED_SPACE
    mock_domain_id.return_value = MOCK_DOMAIN_ID_RESPONSE

    expected_sub_expressions = []

    expected_user_details_tag_filters = [
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
                            "Name": f"Tags.sagemaker:{TEST_USER_DETAILS_SHARED_SPACE.user_id_key}-name",
                            "Operator": "Equals",
                            "Value": TEST_USER_DETAILS_SHARED_SPACE.user_id_value,
                        },
                    ]
                },
            ],
            "Operator": "Or",
        },
    ]

    expected_sub_expressions += (
            expected_base_sub_expressions
            + expected_domain_tag_filters
            + expected_user_details_tag_filters
    )

    assert expected_sub_expressions == get_sub_expressions_filters()


@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_domain_id")
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_user_details")
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_sagemaker_environment")
def test_sub_expressions_filters_user_profile(
        mock_sagemaker_environment, mock_user_details, mock_domain_id
):
    mock_sagemaker_environment.return_value = JupyterLabEnvironment.SAGEMAKER_STUDIO
    mock_user_details.return_value = TEST_USER_DETAILS_PROFILE
    mock_domain_id.return_value = MOCK_DOMAIN_ID_RESPONSE

    expected_sub_expressions = []

    expected_user_details_tag_filters = [
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
                            "Name": f"Tags.sagemaker:{TEST_USER_DETAILS_PROFILE.user_id_key}-name",
                            "Operator": "Equals",
                            "Value": TEST_USER_DETAILS_PROFILE.user_id_value,
                        },
                    ]
                },
            ],
            "Operator": "Or",
        },
    ]

    expected_sub_expressions += (
            expected_base_sub_expressions
            + expected_domain_tag_filters
            + expected_user_details_tag_filters
    )

    assert expected_sub_expressions == get_sub_expressions_filters()
