import pytest
from typing import Dict
from unittest.mock import AsyncMock, Mock, MagicMock, patch

from sagemaker_studio_jupyter_scheduler.util.aws_clients import (
    S3AsyncBoto3Client,
    SageMakerAsyncBoto3Client,
    get_s3_client,
)
from sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter import (
    InternalMetadataAdapter,
)
from sagemaker_studio_jupyter_scheduler.tests.helpers.utils import (
    future_with_result,
    create_mock_open,
)


# Mock credentials for profile testing
MOCK_CREDENTIALS = Mock()
MOCK_CREDENTIALS.access_key = "mock_access_key"
MOCK_CREDENTIALS.secret_key = "mock_secret_key"
MOCK_CREDENTIALS.token = "mock_session_token"

# Mock boto3 session for profile testing
MOCK_BOTO3_SESSION = Mock()
MOCK_BOTO3_SESSION.get_credentials.return_value = MOCK_CREDENTIALS
MOCK_BOTO3_SESSION.available_profiles = ["default", "DomainExecutionRoleCreds"]


# TODO: cleanup the classes to remove these fixtures
@pytest.fixture(autouse=True)
def mock_os_getmtime():
    metadata_mock = MagicMock()
    metadata_mock.return_value.metadata = {}
    with patch(
        "os.path.getmtime",
    ), patch.object(
        InternalMetadataAdapter, "__init__", return_value=None
    ), patch.object(InternalMetadataAdapter, "get_stage", return_value="prod"), patch(
        "boto3.Session", return_value=MOCK_BOTO3_SESSION
    ):
        yield


def mock_sagemaker_client(method_mock: Dict) -> (Mock, Mock):
    sagemaker_client = SageMakerAsyncBoto3Client("aws", "us-west-2")
    inner_client = Mock(**method_mock)
    sagemaker_client.sess = Mock(
        **{
            "create_client.return_value": MagicMock(
                **{"__aenter__.return_value": inner_client}
            )
        }
    )
    return sagemaker_client, inner_client


MOCK_INTERNAL_METADATA = """{
    "Stage": "prod"
}
"""

MOCK_INTERNAL_METADATA_GAMMA = """{
    "Stage": "loadtest"
}
"""

mock_open_metadata = create_mock_open(
    {"/opt/.sagemakerinternal/internal-metadata.json": MOCK_INTERNAL_METADATA}
)

mock_open_gamma_metadata = create_mock_open(
    {"/opt/.sagemakerinternal/internal-metadata.json": MOCK_INTERNAL_METADATA_GAMMA}
)


@pytest.mark.asyncio
@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_describe_training_job_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {
            "describe_training_job.return_value": future_with_result(
                # TODO: Mock the full response.
                {"job_name": "a-b-c-d"}
            )
        }
    )

    # When
    result = await sagemaker_client.describe_training_job(job_name="a-b-c-d")

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.describe_training_job.assert_called_with(TrainingJobName="a-b-c-d")
    assert result == {"job_name": "a-b-c-d"}


@pytest.mark.asyncio
@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_create_training_job_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {
            "create_training_job.return_value": future_with_result(
                {
                    "TrainingJobArn": "arn:aws:sagemaker:us-west-2:112233445566:training-job/a-b-c-d"
                }
            )
        }
    )

    # When
    result = await sagemaker_client.create_training_job({"job_name": "a-b-c-d"})

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.create_training_job.assert_called_with(**{"job_name": "a-b-c-d"})
    assert result == {
        "TrainingJobArn": "arn:aws:sagemaker:us-west-2:112233445566:training-job/a-b-c-d"
    }


@pytest.mark.asyncio
@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_list_tags_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {
            "list_tags.return_value": future_with_result(
                {
                    "Tags": [
                        {"Key": "Tag 1 key", "Value": "Tag 1 value"},
                        {"Key": "Tag 2 key", "Value": "Tag 2 value"},
                    ],
                    "NextToken": "abc",
                }
            )
        }
    )

    # When
    result = await sagemaker_client.list_tags(
        "arn:aws:sagemaker:us-west-2:112233445566:training-job/a-b-c-d"
    )

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.list_tags.assert_called_with(
        ResourceArn="arn:aws:sagemaker:us-west-2:112233445566:training-job/a-b-c-d"
    )
    assert result == {
        "Tags": [
            {"Key": "Tag 1 key", "Value": "Tag 1 value"},
            {"Key": "Tag 2 key", "Value": "Tag 2 value"},
        ],
        "NextToken": "abc",
    }


@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_search_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {
            "search.return_value": future_with_result(
                [
                    # TODO: Mock the full response.
                    {"TrainingJobName": "a-b-c-d"},
                    {"TrainingJobName": "e-f-g-h"},
                ]
            )
        }
    )

    # When
    result = await sagemaker_client.search({"Resource": "TrainingJob"})

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.search.assert_called_with(**{"Resource": "TrainingJob"})
    assert result == [
        {"TrainingJobName": "a-b-c-d"},
        {"TrainingJobName": "e-f-g-h"},
    ]


@pytest.mark.asyncio
@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_stop_training_job_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {"stop_training_job.return_value": future_with_result({})}
    )

    # When
    result = await sagemaker_client.stop_training_job(training_job_name="a-b-c-d")

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.stop_training_job.assert_called_with(TrainingJobName="a-b-c-d")
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_add_tags_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {"add_tags.return_value": future_with_result({})}
    )

    # When
    result = await sagemaker_client.add_tags(
        resource_arn="arn:aws:sagemaker:us-west-2:112233445566:training-job/a-b-c-d",
        tag_list=[
            {"Key": "Tag 1 key", "Value": "Tag 1 value"},
            {"Key": "Tag 2 key", "Value": "Tag 2 value"},
        ],
    )

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.add_tags.assert_called_with(
        ResourceArn="arn:aws:sagemaker:us-west-2:112233445566:training-job/a-b-c-d",
        Tags=[
            {"Key": "Tag 1 key", "Value": "Tag 1 value"},
            {"Key": "Tag 2 key", "Value": "Tag 2 value"},
        ],
    )
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_describe_lcc_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {
            "describe_studio_lifecycle_config.return_value": future_with_result(
                {
                    # TODO: Mock the response accurately (base64-encoded).
                    "StudioLifecycleConfigContent": "lcc-content"
                }
            )
        }
    )

    # When
    result = await sagemaker_client.describe_lcc(
        lcc_arn="arn:aws:sagemaker:us-west-2:112233445566:studio-lifecycle-config/my-lcc"
    )

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.describe_studio_lifecycle_config.assert_called_with(
        StudioLifecycleConfigName="my-lcc"
    )
    assert result == {"StudioLifecycleConfigContent": "lcc-content"}


@pytest.mark.asyncio
@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_describe_domain_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {
            "describe_domain.return_value": future_with_result(
                {
                    # TODO: Mock the full response.
                    "SubnetIds": ["subnet-1", "subnet-2"],
                    "DefaultUserSettings": {
                        "ExecutionRole": "arn:aws:iam::112233445566:role/service-role/AmazonSageMaker-ExecutionRole-20220125T140052"
                    },
                }
            )
        }
    )

    # When
    result = await sagemaker_client.describe_domain(domain_id="d-1a2b3c4d5e6f")

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.describe_domain.assert_called_with(DomainId="d-1a2b3c4d5e6f")
    assert result == {
        "SubnetIds": ["subnet-1", "subnet-2"],
        "DefaultUserSettings": {
            "ExecutionRole": "arn:aws:iam::112233445566:role/service-role/AmazonSageMaker-ExecutionRole-20220125T140052"
        },
    }


@pytest.mark.asyncio
@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_describe_user_profile_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {
            "describe_user_profile.return_value": future_with_result(
                {
                    # TODO: Mock the full response.
                    "UserSettings": {
                        "ExecutionRole": "arn:aws:iam::112233445566:role/service-role/AmazonSageMaker-ExecutionRole-20220125T140052"
                    }
                }
            )
        }
    )

    # When
    result = await sagemaker_client.describe_user_profile(
        domain_id="d-1a2b3c4d5e6f", user_profile_name="fake-user"
    )

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.describe_user_profile.assert_called_with(
        DomainId="d-1a2b3c4d5e6f", UserProfileName="fake-user"
    )
    assert result == {
        "UserSettings": {
            "ExecutionRole": "arn:aws:iam::112233445566:role/service-role/AmazonSageMaker-ExecutionRole-20220125T140052"
        }
    }


@pytest.mark.asyncio
@patch.object(InternalMetadataAdapter, "get_stage", return_value="loadtest")
async def test_create_sagemaker_client_with_gamma_stage(mock_stage):
    sagemaker_client = SageMakerAsyncBoto3Client("aws", "us-west-2")
    sagemaker_client.sess = MagicMock()

    # any call to sagemaker should use the correct endpoint
    await sagemaker_client.describe_domain(domain_id="d-1a2b3c4d5e6f")

    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )


@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_describe_image_version_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {
            "describe_image_version.return_value": future_with_result(
                {
                    "BaseImage": "177118115371.dkr.ecr.us-east-1.amazonaws.com/multi-py-conda-image:0.0.1",
                    "ContainerImage": "177118115371.dkr.ecr.us-east-1.amazonaws.com/multi-py-conda-image@sha256:947aec5e04638b43db188fd51ab8e850ac31bf83281c5b61f2e2f4d5e0f06477",
                    "CreationTime": 1666064247.19,
                    "ImageArn": "arn:aws:sagemaker:us-east-1:177118115371:image/multi-py-conda-image",
                    "ImageVersionArn": "arn:aws:sagemaker:us-east-1:177118115371:image-version/multi-py-conda-image/2",
                    "ImageVersionStatus": "CREATED",
                    "LastModifiedTime": 1666064247.561,
                    "Version": 2,
                    "Horovod": "false",
                }
            )
        }
    )

    # When
    result = await sagemaker_client.describe_image_version(
        image_name="multi-py-conda-image"
    )

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.describe_image_version.assert_called_with(
        ImageName="multi-py-conda-image"
    )
    assert result == {
        "BaseImage": "177118115371.dkr.ecr.us-east-1.amazonaws.com/multi-py-conda-image:0.0.1",
        "ContainerImage": "177118115371.dkr.ecr.us-east-1.amazonaws.com/multi-py-conda-image@sha256:947aec5e04638b43db188fd51ab8e850ac31bf83281c5b61f2e2f4d5e0f06477",
        "CreationTime": 1666064247.19,
        "ImageArn": "arn:aws:sagemaker:us-east-1:177118115371:image/multi-py-conda-image",
        "ImageVersionArn": "arn:aws:sagemaker:us-east-1:177118115371:image-version/multi-py-conda-image/2",
        "ImageVersionStatus": "CREATED",
        "LastModifiedTime": 1666064247.561,
        "Version": 2,
        "Horovod": "false",
    }


@pytest.mark.asyncio
@patch("builtins.open", mock_open_metadata)
async def test_describe_app_image_config_success():
    # Given
    sagemaker_client, inner_client = mock_sagemaker_client(
        {
            "describe_app_image_config.return_value": future_with_result(
                {
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
            )
        }
    )

    # When
    result = await sagemaker_client.describe_app_image_config(
        app_image_config_name="multi-py-conda-image-config"
    )

    # Then
    sagemaker_client.sess.create_client.assert_called_with(
        service_name="sagemaker", 
        config=sagemaker_client.cfg, 
        region_name="us-west-2",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_session_token="mock_session_token"
    )
    inner_client.describe_app_image_config.assert_called_with(
        AppImageConfigName="multi-py-conda-image-config"
    )
    assert result == {
        "AppImageConfigArn": "arn:aws:sagemaker:us-east-1:177118115371:app-image-config/multi-py-conda-image-config",
        "AppImageConfigName": "multi-py-conda-image-config",
        "CreationTime": 1666064286.771,
        "LastModifiedTime": 1666064286.776,
        "KernelGatewayImageConfig": {
            "KernelSpecs": [
                {"Name": "conda-env-py310-py", "DisplayName": "conda env py310"},
                {"Name": "conda-env-py39-py", "DisplayName": "conda env py39"},
                {"Name": "conda-env-py37-py", "DisplayName": "conda env py37"},
                {"Name": "conda-env-py38-py", "DisplayName": "conda env py38"},
            ],
            "FileSystemConfig": {
                "MountPath": "/home/sagemaker-user",
                "DefaultUid": 1000,
                "DefaultGid": 100,
            },
        },
    }


@pytest.mark.asyncio
async def test_s3_client_get_bucket_location():
    mock_cm_s3_client = AsyncMock()
    mock_s3_inner_client = AsyncMock()
    # In Python, the __aenter__() method is used in the context management protocol
    # for asynchronous context managers. An asynchronous context manager allows you
    # to define custom behavior for entering and exiting a context in an asynchronous manner.
    mock_s3_inner_client.__aenter__.return_value = mock_cm_s3_client
    TEST_AWS_ACCOUNT = "77777777777"
    with patch.object(
        S3AsyncBoto3Client, "_create_s3_client", return_value=mock_s3_inner_client
    ):
        s3_client = get_s3_client()
        TEST_S3_BUCKET_NAME = "test_bucket_name"
        await s3_client.get_bucket_location(TEST_S3_BUCKET_NAME, TEST_AWS_ACCOUNT)
        mock_cm_s3_client.get_bucket_location.assert_called_with(
            Bucket=TEST_S3_BUCKET_NAME, ExpectedBucketOwner=TEST_AWS_ACCOUNT
        )


@pytest.mark.asyncio
@patch("sagemaker_studio_jupyter_scheduler.util.aws_clients.boto3.Session")
async def test_sagemaker_client_uses_profile_credentials(mock_boto3_session):
    # Given - Patch the specific import in aws_clients module
    mock_credentials = Mock()
    mock_credentials.access_key = "test_access_key"
    mock_credentials.secret_key = "test_secret_key"
    mock_credentials.token = "test_session_token"
    
    mock_session = Mock()
    mock_session.get_credentials.return_value = mock_credentials
    mock_boto3_session.return_value = mock_session
    
    sagemaker_client = SageMakerAsyncBoto3Client("aws", "us-west-2")

    create_client_args = {}
    sagemaker_client._add_profile_credentials(create_client_args)
    
    # Then
    mock_session.get_credentials.assert_called_once()

@pytest.mark.asyncio
@patch("sagemaker_studio_jupyter_scheduler.util.aws_clients.boto3.Session")
async def test_base_client_profile_credentials_method(mock_boto3_session):
    # Given - Test the helper method directly
    mock_credentials = Mock()
    mock_credentials.access_key = "test_access_key"
    mock_credentials.secret_key = "test_secret_key"
    mock_credentials.token = "test_session_token"
    
    mock_session = Mock()
    mock_session.get_credentials.return_value = mock_credentials
    mock_boto3_session.return_value = mock_session
    
    from sagemaker_studio_jupyter_scheduler.util.aws_clients import BaseAsyncBotoClient
    
    # When
    base_client = BaseAsyncBotoClient("aws", "us-west-2")
    create_client_args = {}
    base_client._add_profile_credentials(create_client_args)
    
    # Then
    mock_session.get_credentials.assert_called_once()
    assert create_client_args["aws_access_key_id"] == "test_access_key"
    assert create_client_args["aws_secret_access_key"] == "test_secret_key"
    assert create_client_args["aws_session_token"] == "test_session_token"
