import json
import pytz
import logging
from sagemaker_studio_jupyter_scheduler.tests.test_advanced_environments import MOCK_CALLER_IDENTITY
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
)

from traitlets.config import Config
from sagemaker_studio_jupyter_scheduler.util.aws_clients import (
    EventBridgeAsyncBotoClient,
    STSAsyncBotoClient,
    SageMakerAsyncBoto3Client,
)

from sagemaker_studio_jupyter_scheduler.scheduler import SagemakerEnvironmentManager
from sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter import (
    InternalMetadataAdapter,
)
from sagemaker_studio_jupyter_scheduler.model.model_converter import ModelConverter
from sagemaker_studio_jupyter_scheduler.model.models import (
    JobEnvironmentVariableName,
    JobTag,
    SageMakerTrainingJobStatus,
    UserDetails,
    UserTypes,
)
from jupyter_scheduler.exceptions import SchedulerError

from sagemaker_studio_jupyter_scheduler.util.error_util import (
    ACCESS_DENIED_ERROR_MESSAGE,
    ErrorConverter,
    SageMakerSchedulerError,
)
import pytest
from datetime import datetime
import botocore
from unittest.mock import AsyncMock, MagicMock, Mock, patch, mock_open
from jupyter_scheduler.models import (
    DescribeJob,
    ListJobDefinitionsQuery,
    DescribeJobDefinition,
    ListJobDefinitionsResponse,
    UpdateJobDefinition,
    Status,
    DEFAULT_SORT,
    CreateJob,
)
from tornado import web

from jupyter_scheduler.exceptions import SchedulerError

from sagemaker_studio_jupyter_scheduler.tests.helpers.utils import (
    compare_tag_list,
    future_with_result,
    future_with_exception,
)
from sagemaker_studio_jupyter_scheduler.scheduler import SageMakerScheduler
from jupyter_scheduler.models import CreateJobFromDefinition
from aws_embedded_metrics.logger.metrics_context import MetricsContext
from sagemaker_studio_jupyter_scheduler.scheduler.scheduler import EVENT_BRIDGE_RULE_TARGET_ID
from sagemaker_studio_jupyter_scheduler.tests.test_logging import MOCK_NETWORK_ACCESS_TYPE


@pytest.fixture(autouse=True)
def mock_get_aws_account_id():
    with patch(
        "sagemaker_studio_jupyter_scheduler.logging.get_aws_account_id",
        return_value="us-west-2",
    ), patch(
        "sagemaker_studio_jupyter_scheduler.scheduler.environments.get_region_name",
        return_value="us-west-2",
    ), patch(
        "os.path.getmtime",
    ):
        yield


def create_scheduler_with_mocked_dependencies():
    return SageMakerScheduler(
        root_dir="mock-root-dir",
        environments_manager=SagemakerEnvironmentManager(),
        config=Config(),
        sagemaker_client=Mock(),
        event_bridge_client=Mock(),
        s3_client=Mock(),
        converter=Mock(),
        error_matcher=Mock(),
        error_converter=Mock(),
        error_factory=Mock(),
        log = Mock(),
    )


MOCK_RESOURCE_METADATA = """
{
  "ResourceArn": "arn:aws:sagemaker:us-west-2:112233445566:app/d-1a2b3c4d5e6f/fake-user/JupyterServer/default",
  "UserProfileName": "sunp",
  "DomainId": "d-1a2b3c4d5e6f"
}
"""

# TODO: Reintroduce this unit test with some refactoring
# @pytest.mark.asyncio
# async def test_create_job_success():
#     # Given
#     scheduler = create_scheduler_with_mocked_dependencies()
#
#     create_training_job_input = {"TrainingJobName": "a-b-c-d"}
#     scheduler.converter.to_create_training_job_input.return_value = future_with_result(
#         create_training_job_input
#     )
#
#     scheduler.sagemaker_client.create_training_job.return_value = future_with_result(
#         create_training_job_input
#     )
#
#     # When
#     create_job_input = CreateJob(
#         input_filename="mock-input-uri",
#         runtime_environment_name="mock-environment-name",
#         runtime_environment_parameters={"s3_input": "s3://mock-bucket/mock-path"},
#     )
#     result = await scheduler.create_job(create_job_input)
#
#     # Then
#     scheduler.converter.to_create_training_job_input.assert_called_with(
#         upstream_model=create_job_input
#     )
#     scheduler.sagemaker_client.create_training_job.assert_called_with(
#         create_training_job_input
#     )
#     assert result == {"job_id": "a-b-c-d"}


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
async def test_get_job_success(mock_open):
    # Given
    scheduler = create_scheduler_with_mocked_dependencies()

    scheduler._sagemaker_client.describe_training_job.return_value = future_with_result(
        {
            "TrainingJobArn": "mock-training-job-arn",
        }
    )
    scheduler._sagemaker_client.list_tags.return_value = future_with_result(
        {
            "Tags": [
                {"Key": "tag 1 key", "Value": "tag 1 value"},
            ]
        }
    )

    get_job_response = DescribeJob(
        name="my-job",
        input_filename="mock-input-filename",
        runtime_environment_name="mock-runtime-environment-name",
        job_id="a-b-c-d",
        url="mock-url",
        create_time=123,
        update_time=456,
    )
    scheduler.converter.to_tag_dict.return_value = {
        "tag 1 key": "tag 1 value",
    }
    scheduler.converter.to_jupyter_describe_job_output.return_value = get_job_response

    # When
    result = await scheduler.get_job("a-b-c-d")

    # Then
    scheduler._sagemaker_client.describe_training_job.assert_called_with(
        job_name="a-b-c-d"
    )
    scheduler._sagemaker_client.list_tags.assert_called_with(
        resource_arn="mock-training-job-arn"
    )
    scheduler.converter.to_jupyter_describe_job_output.assert_called_with(
        scheduler=scheduler,
        outputs=True,
        training_job_response={
            "TrainingJobArn": "mock-training-job-arn",
        },
        tag_dict={
            "tag 1 key": "tag 1 value",
        },
    )
    scheduler.converter.to_tag_dict.assert_called_with(
        [
            {"Key": "tag 1 key", "Value": "tag 1 value"},
        ]
    )
    assert result == get_job_response


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
async def test_get_job_definition_exception(mock_open):
    scheduler = create_scheduler_with_mocked_dependencies()
    scheduler.error_converter = ErrorConverter()
    scheduler._sagemaker_client.describe_pipeline.return_value = future_with_exception(
        botocore.exceptions.ClientError(
            {
                "Error": {"Code": "400", "Message": "No resource found"},
                "ResponseMetadata": {
                    "RequestId": "1234567890ABCDEF",
                    "HostId": "host ID data will appear here as a hash",
                    "HTTPStatusCode": 400,
                    "HTTPHeaders": {"header metadata key/values will appear here"},
                    "RetryAttempts": 0,
                },
            },
            "describe_pipeline",
        )
    )

    scheduler._event_bridge_client.describe_rule.return_value = future_with_result(
        {
            "Name": "string",
            "Arn": "string",
            "EventPattern": "string",
            "ScheduleExpression": "string",
            "State": "ENABLED",
            "Description": "string",
            "RoleArn": "string",
            "ManagedBy": "string",
            "EventBusName": "string",
            "CreatedBy": "string",
        }
    )

    scheduler._sagemaker_client.list_tags.return_value = future_with_result(
        {"Tags": [{"Key": "foo", "Value": "bar"}]}
    )

    with pytest.raises(SageMakerSchedulerError):
        await scheduler.get_job_definition("mock_id")


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
async def test_delete_job_definition_happy_path(mock_open):
    scheduler = create_scheduler_with_mocked_dependencies()
    job_definition_id = "a-b-c-d"

    scheduler._event_bridge_client.disable_rule.return_value = future_with_result({})
    scheduler._sagemaker_client.delete_pipeline.return_value = future_with_result(
        {"PipelineArn": "string"}
    )
    scheduler._event_bridge_client.remove_targets.return_value = future_with_result(
        {"FailedEntryCount": 0}
    )
    scheduler._event_bridge_client.delete_rule.return_value = future_with_result({})

    result = await scheduler.delete_job_definition(job_definition_id)

    assert result is None
    # EB calls
    scheduler._event_bridge_client.disable_rule.assert_called_with(job_definition_id)
    scheduler._event_bridge_client.remove_targets.assert_called_with(
        job_definition_id, [EVENT_BRIDGE_RULE_TARGET_ID]
    )
    scheduler._event_bridge_client.delete_rule.assert_called_with(job_definition_id)

    # SM Pipeline calls
    scheduler._sagemaker_client.delete_pipeline.assert_called_with(job_definition_id)


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
async def test_update_job_definition_happy_path(mock_open):
    scheduler = create_scheduler_with_mocked_dependencies()
    job_definition_id = "a-b-c-d"

    scheduler._event_bridge_client.put_rule.return_value = future_with_result(None)

    result = await scheduler.update_job_definition(
        job_definition_id, UpdateJobDefinition(schedule="30 12 * 1-12 MON-FRI")
    )

    assert result is None

    scheduler._event_bridge_client.put_rule.assert_called_with(
        name="a-b-c-d",
        description="Created for Notebook execution from notebook scheduler",
        schedule_expression="cron(30 12 ? 1-12 MON-FRI *)",
        state="ENABLED",
    )


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
async def test_pause_job_definition_happy_path(mock_open):
    scheduler = create_scheduler_with_mocked_dependencies()
    job_definition_id = "a-b-c-d"

    scheduler._event_bridge_client.disable_rule.return_value = future_with_result(None)

    result = await scheduler.update_job_definition(
        job_definition_id, UpdateJobDefinition(active=False)
    )

    assert result is None

    scheduler._event_bridge_client.disable_rule.assert_called_with(job_definition_id)


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
async def test_resume_job_definition_happy_path(mock_open):
    scheduler = create_scheduler_with_mocked_dependencies()
    job_definition_id = "a-b-c-d"

    scheduler._event_bridge_client.enable_rule.return_value = future_with_result(None)

    result = await scheduler.update_job_definition(
        job_definition_id, UpdateJobDefinition(active=True)
    )

    assert result is None

    scheduler._event_bridge_client.enable_rule.assert_called_with(job_definition_id)


def _create_mock_describe_job_definition(name, job_definition_id, status):
    return DescribeJobDefinition(
        input_filename="INPUT_FILENAME_STUB",
        # TODO: add this env to CreateJob
        runtime_environment_name="sagemaker-default-env",
        runtime_environment_parameters={},
        output_formats=["ipynb"],
        parameters={},
        tags=[],
        name=name,
        compute_type="m4.xl.large",
        schedule="cron()",
        timezone="UTC",
        job_definition_id=job_definition_id,
        create_time=1665485984,
        update_time=1665485984,
        active=status,
    )


def _create_mock_search_results(name, job_definition_id):
    return {
        "Pipeline": {
            "PipelineArn": "string",
            "PipelineName": job_definition_id,
            "PipelineDisplayName": "string",
            "PipelineDescription": "string",
            "RoleArn": "string",
            "PipelineStatus": "Active",
            "CreationTime": datetime(2015, 1, 1),
            "LastModifiedTime": datetime(2015, 1, 1),
            "LastRunTime": datetime(2015, 1, 1),
            "CreatedBy": {
                "UserProfileArn": "string",
                "UserProfileName": "string",
                "DomainId": "string",
            },
            "LastModifiedBy": {
                "UserProfileArn": "string",
                "UserProfileName": "string",
                "DomainId": "string",
            },
            "Tags": [
                {"Key": JobTag.NOTEBOOK_NAME.value, "Value": name},
            ],
        }
    }


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
async def test_list_job_definition_happy_path(mock_open):
    scheduler = create_scheduler_with_mocked_dependencies()
    expected_results = [
        _create_mock_describe_job_definition("definition-1", "a-b-c-d", True),
        _create_mock_describe_job_definition("definition-2", "a1-b2-c3-d4", True),
        _create_mock_describe_job_definition("definition-3", "e1-f2-g3-h4", True),
    ]

    scheduler._sagemaker_client.search.return_value = future_with_result(
        {
            "Results": [
                _create_mock_search_results("definition-1", "a-b-c-d"),
                _create_mock_search_results("definition-2", "a1-b2-c3-d4"),
                _create_mock_search_results("definition-3", "e1-f2-g3-h4"),
            ],
            "NextToken": "token-1",
        }
    )

    scheduler.get_job_definition = Mock()
    scheduler.get_job_definition.side_effect = [
        future_with_result(
            _create_mock_describe_job_definition("definition-1", "a-b-c-d", True)
        ),
        future_with_result(
            _create_mock_describe_job_definition("definition-2", "a1-b2-c3-d4", True)
        ),
        future_with_result(
            _create_mock_describe_job_definition("definition-3", "e1-f2-g3-h4", True)
        ),
    ]

    query = ListJobDefinitionsQuery(name="definition", create_time=1665443057000)

    result = await scheduler.list_job_definitions(query)

    assert result == ListJobDefinitionsResponse(
        job_definitions=expected_results, next_token="token-1", total_count=-1
    )


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
async def test_get_staging_paths__job_completed__allows_downloading_all_outputs(
    mock_open,
):
    # Given
    scheduler = create_scheduler_with_mocked_dependencies()
    scheduler._sagemaker_client.describe_training_job.return_value = future_with_result(
        {
            "TrainingJobArn": "arn:aws:sagemaker:us-west-2:112233445566:training-job/example-job-id",
            "TrainingJobStatus": "Completed",
            "Environment": {"SM_OUTPUT_NOTEBOOK_NAME": "output-HelloWorld.ipynb"},
        }
    )

    # When
    result = await scheduler.get_staging_paths(
        DescribeJob(
            name="my-job",
            status=Status.COMPLETED,
            input_filename="HelloWorld.ipynb",
            runtime_environment_name="sagemaker-default-env",
            runtime_environment_parameters={
                "s3_input": "s3://sagemaker-us-east-1-177118115371",
                "s3_output": "s3://sagemaker-us-east-1-177118115371",
            },
            job_id="example-job-id",
            url="",
            create_time=123,
            update_time=456,
            package_input_folder=False,
            packaged_files=[]
        )
    )

    # Then
    assert result == {
        "tar.gz": "s3://sagemaker-us-east-1-177118115371/example-job-id/output/output.tar.gz",
        "input": "HelloWorld.ipynb",
        "ipynb": "output-HelloWorld.ipynb",
        "log": "sagemaker_job_execution.log",
        "files": []
    }


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
async def test_get_staging_paths__job_failed_with_all_outputs__allows_downloading_all_outputs(
    mock_open,
):
    # Given
    scheduler = create_scheduler_with_mocked_dependencies()
    scheduler._sagemaker_client.describe_training_job.return_value = future_with_result(
        {
            "TrainingJobArn": "arn:aws:sagemaker:us-west-2:112233445566:training-job/example-job-id",
            "TrainingJobStatus": "Failed",
            "Environment": {"SM_OUTPUT_NOTEBOOK_NAME": "output-HelloWorld.ipynb"},
            "FailureReason": "AlgorithmError: [SM-111] An error occurred",
        }
    )
    scheduler.converter.determine_available_output_formats_and_failure_reason.return_value = (
        ["input", "ipynb", "log"],
        "AlgorithmError: An error occurred",
    )

    # When
    result = await scheduler.get_staging_paths(
        DescribeJob(
            name="my-job",
            status=Status.FAILED,
            input_filename="HelloWorld.ipynb",
            runtime_environment_name="sagemaker-default-env",
            runtime_environment_parameters={
                "s3_input": "s3://sagemaker-us-east-1-177118115371",
                "s3_output": "s3://sagemaker-us-east-1-177118115371",
            },
            job_id="example-job-id",
            url="",
            create_time=123,
            update_time=456,
        )
    )

    # Then
    scheduler.converter.determine_available_output_formats_and_failure_reason.assert_called_with(
        Status.FAILED, "AlgorithmError: [SM-111] An error occurred"
    )
    assert result == {
        "tar.gz": "s3://sagemaker-us-east-1-177118115371/example-job-id/output/output.tar.gz",
        "input": "HelloWorld.ipynb",
        "ipynb": "output-HelloWorld.ipynb",
        "log": "sagemaker_job_execution.log",
    }


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
async def test_get_staging_paths__job_failed_with_no_notebook__allows_downloading_only_input_and_log(
    mock_open,
):
    # Given
    scheduler = create_scheduler_with_mocked_dependencies()
    scheduler._sagemaker_client.describe_training_job.return_value = future_with_result(
        {
            "TrainingJobArn": "arn:aws:sagemaker:us-west-2:112233445566:training-job/example-job-id",
            "TrainingJobStatus": "Failed",
            "Environment": {"SM_OUTPUT_NOTEBOOK_NAME": "output-HelloWorld.ipynb"},
            "FailureReason": "AlgorithmError: [SM-101] An error occurred",
        }
    )
    scheduler.converter.determine_available_output_formats_and_failure_reason.return_value = (
        ["input", "log"],
        None,
    )

    # When
    result = await scheduler.get_staging_paths(
        DescribeJob(
            name="my-job",
            status=Status.FAILED,
            input_filename="HelloWorld.ipynb",
            runtime_environment_name="sagemaker-default-env",
            runtime_environment_parameters={
                "s3_input": "s3://sagemaker-us-east-1-177118115371",
                "s3_output": "s3://sagemaker-us-east-1-177118115371",
            },
            job_id="example-job-id",
            url="",
            create_time=123,
            update_time=456,
        )
    )

    # Then
    scheduler.converter.determine_available_output_formats_and_failure_reason.assert_called_with(
        Status.FAILED, "AlgorithmError: [SM-101] An error occurred"
    )
    assert result == {
        "tar.gz": "s3://sagemaker-us-east-1-177118115371/example-job-id/output/output.tar.gz",
        "input": "HelloWorld.ipynb",
        "log": "sagemaker_job_execution.log",
    }


@pytest.mark.asyncio
async def test_get_staging_paths__job_failed_with_no_outputs__allows_downloading_original_input():
    # Given
    scheduler = create_scheduler_with_mocked_dependencies()
    scheduler._sagemaker_client.describe_training_job.return_value = future_with_result(
        {
            "TrainingJobArn": "arn:aws:sagemaker:us-west-2:112233445566:training-job/example-job-id",
            "TrainingJobStatus": "Failed",
            "Environment": {"SM_OUTPUT_NOTEBOOK_NAME": "output-HelloWorld.ipynb"},
            "FailureReason": "AlgorithmError: An error occurred",
        }
    )
    scheduler.converter.determine_available_output_formats_and_failure_reason.return_value = (
        [],
        "AlgorithmError: An error occurred",
    )

    # When
    result = await scheduler.get_staging_paths(
        DescribeJob(
            name="my-job",
            status=Status.FAILED,
            input_filename="HelloWorld.ipynb",
            runtime_environment_name="sagemaker-default-env",
            runtime_environment_parameters={
                "s3_input": "s3://sagemaker-us-east-1-177118115371",
                "s3_output": "s3://sagemaker-us-east-1-177118115371",
            },
            job_id="example-job-id",
            url="",
            create_time=123,
            update_time=456,
        )
    )

    # Then
    scheduler.converter.determine_available_output_formats_and_failure_reason.assert_called_with(
        Status.FAILED, "AlgorithmError: An error occurred"
    )
    assert result == {
        "input": "s3://sagemaker-us-east-1-177118115371/example-job-id/input/HelloWorld.ipynb",
    }


@pytest.mark.asyncio
@patch.object(InternalMetadataAdapter, "__init__", return_value=None)
@patch.object(InternalMetadataAdapter, "get_stage", return_value="us-west-2")
@patch.object(SageMakerScheduler, "get_packaged_file_paths", return_value=[])
async def test_create_job_for_attched_tags_in_standalone(
    mock_packaged_files, mock_adapter_stage, mock_adapter_init
):
    scheduler = create_scheduler_with_mocked_dependencies()
    scheduler.converter = ModelConverter(MagicMock())
    input = MagicMock()
    TEST_JOB_NAME = "JobName"
    TEST_NOTEBOOK_NAME = "HelloWorld.ipynb"
    TEST_INPUT_URI = f"a/b/c/{TEST_NOTEBOOK_NAME}"
    input.name = TEST_JOB_NAME
    input.input_uri = TEST_INPUT_URI
    # to make the create_job call, we need to mock a bunch of things
    # 1. s3 bucket upload, getting dependency, converter create_job input
    # to_job_tags and get_addtion_tags

    mock_s3_file_uploader = MagicMock()
    mock_s3_file_uploader.notebook_name = TEST_NOTEBOOK_NAME
    scheduler._prepare_job_artifacts = AsyncMock(return_value=mock_s3_file_uploader)

    scheduler._get_system_dependencies_version = AsyncMock(
        return_value="s3://sagemakerheadlessexecution-prod-us-west-2/headless_system_dependencies/build_12504958"
    )

    scheduler.converter.to_create_training_job_input = AsyncMock(return_value={})
    mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
    scheduler._sagemaker_client = mock_sagemaker_client
    await scheduler.create_job(input)

    actual_tags = mock_sagemaker_client.create_training_job.call_args_list[0].args[0][
        "Tags"
    ]
    expected_tags = [
        {"Key": "sagemaker:name", "Value": TEST_JOB_NAME},
        {"Key": "sagemaker:notebook-name", "Value": TEST_NOTEBOOK_NAME},
        {"Key": "sagemaker:is-scheduling-notebook-job", "Value": "true"},
        {"Key": "sagemaker:is-studio-archived", "Value": "false"},
        {
            "Key": "sagemaker:headless-execution-version",
            "Value": "false",
        },
    ]

    compare_tag_list(actual_tags, expected_tags)


TEST_CREATE_JOB_IDENTIFIER = "test-job-id"


@pytest.mark.asyncio
@patch(
    "sagemaker_studio_jupyter_scheduler.scheduler.scheduler.generate_job_identifier",
    return_value=TEST_CREATE_JOB_IDENTIFIER,
)
@patch.object(InternalMetadataAdapter, "__init__", return_value=None)
@patch.object(InternalMetadataAdapter, "get_stage", return_value="us-west-2")
@patch.object(SageMakerScheduler, "get_packaged_file_paths", return_value=[])
async def test_create_jobdefinition_for_attched_tags_in_standalone(
    mock_packaged_files,
    mock_adapter_stage,
    mock_metadata_adapter,
    mock_jod_id_generator,
):
    scheduler = create_scheduler_with_mocked_dependencies()
    scheduler.converter = ModelConverter(MagicMock())
    input = MagicMock()
    TEST_JOB_NAME = "JobName"
    TEST_NOTEBOOK_NAME = "HelloWorld.ipynb"
    TEST_INPUT_URI = f"a/b/c/{TEST_NOTEBOOK_NAME}"
    input.name = TEST_JOB_NAME
    input.input_uri = TEST_INPUT_URI
    input.schedule = "0 0 * * MON-FRI"
    # TODO Fix this unit tests
    # input.runtime_environment_parameters.max_retry_attempts = 3
    # to make the create_job call, we need to mock a bunch of things
    # 1. s3 bucket upload, getting dependency, converter create_job input
    # to_job_tags and get_addtion_tags

    mock_s3_file_uploader = MagicMock()
    mock_s3_file_uploader.notebook_name = TEST_NOTEBOOK_NAME
    scheduler._prepare_job_artifacts = AsyncMock(return_value=mock_s3_file_uploader)

    scheduler._get_system_dependencies_version = AsyncMock()

    mock_training_job = {
        "Environment": {JobEnvironmentVariableName.SM_OUTPUT_NOTEBOOK_NAME.value: ""},
        "RetryStrategy": { "MaximumRetryAttempts" : 1 }
    }
    scheduler.converter.to_create_training_job_input = AsyncMock(
        return_value=mock_training_job
    )

    mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
    scheduler._sagemaker_client = mock_sagemaker_client

    mock_eventbridge_client = AsyncMock(spec=EventBridgeAsyncBotoClient)
    scheduler._event_bridge_client = mock_eventbridge_client

    await scheduler.create_job_definition(input)

    expected_tags = [
        {"Key": "sagemaker:name", "Value": TEST_JOB_NAME},
        {"Key": "sagemaker:notebook-name", "Value": TEST_NOTEBOOK_NAME},
        {"Key": "sagemaker:is-scheduling-notebook-job", "Value": "true"},
        {"Key": "sagemaker:is-studio-archived", "Value": "false"},
        {
            "Key": "sagemaker:headless-execution-version",
            "Value": "false",
        },
    ]
    pipeline_tags = mock_sagemaker_client.create_pipeline.call_args_list[0].kwargs[
        "tags"
    ]
    training_job = json.loads(
        mock_sagemaker_client.create_pipeline.call_args_list[0].kwargs[
            "pipeline_definition"
        ]
    )
    training_job_tags = training_job["Steps"][0]["Arguments"]["Tags"]
    assert training_job["Steps"][0]["RetryPolicies"][0]["ExceptionType"] == ["Step.SERVICE_FAULT", "Step.THROTTLING", "SageMaker.JOB_INTERNAL_ERROR", "SageMaker.CAPACITY_ERROR", "SageMaker.RESOURCE_LIMIT"]
    # TODO Fix this unit tests
    # assert training_job["Steps"][0]["RetryPolicies"][0]["MaxAttempts"] == 3
    event_bridge_rule_tags = mock_eventbridge_client.put_rule.call_args_list[0].kwargs[
        "tags"
    ]

    compare_tag_list(pipeline_tags, expected_tags)
    compare_tag_list(
        training_job_tags,
        expected_tags
        + [{"Key": "sagemaker:job-definition-id", "Value": TEST_CREATE_JOB_IDENTIFIER}],
    )
    compare_tag_list(event_bridge_rule_tags, expected_tags)


@pytest.mark.asyncio
@patch.object(InternalMetadataAdapter, "__init__", return_value=None)
@patch.object(InternalMetadataAdapter, "get_stage", return_value="us-west-2")
@patch.object(SageMakerScheduler, "get_packaged_file_paths", return_value=[])
async def test_create_job_from_definition_job_id_contains_job_name(
    mock_packaged_files,
    mock_adapter_stage,
    mock_metadata_adapter,
):
    # Arrange
    scheduler = create_scheduler_with_mocked_dependencies()
    scheduler.converter = ModelConverter(MagicMock())

    job_definition_id = "test-pipeline-id"
    job_name = "testjobname"
    notebook_name = "test-notebook.ipynb"

    # Mock SageMaker client
    mock_sagemaker_client = AsyncMock()
    mock_sagemaker_client.describe_pipeline.return_value = {
        "PipelineDefinition": json.dumps({
            "Steps": [{
                "Arguments": {
                    "Environment": {
                        JobEnvironmentVariableName.SM_INPUT_NOTEBOOK_NAME.value: notebook_name
                    },
                    "Tags": [
                        {"Key": JobTag.NAME.value, "Value": job_name}
                    ]
                }
            }]
        })
    }
    scheduler._sagemaker_client = mock_sagemaker_client

    # Mock converter methods
    scheduler.converter.to_tag_dict = MagicMock(return_value={JobTag.NAME.value: job_name})
    scheduler.converter.generate_training_job_name = MagicMock(
        return_value=f"{job_name}-{notebook_name}"
    )

    # Create model and metrics
    model = CreateJobFromDefinition( )
    metrics = MetricsContext()

    # Act
    result_job_id = await scheduler.create_job_from_definition(
        job_definition_id=job_definition_id,
        model=model,
        metrics=metrics
    )

    # Assert
    assert job_name in result_job_id, f"Expected job_id '{result_job_id}' to contain job_name '{job_name}'"


query = MagicMock()
query.status = Status.IN_PROGRESS
query.job_definition_id = "test-jod-definition-id"
query.start_time = datetime(2023, 5, 10).timestamp()
query.max_items = 25
query.sort_by = None
query.name = "test-job-name"

expected_common_filters = [
    {
        "Name": "Tags.sagemaker:is-studio-archived",
        "Operator": "Equals",
        "Value": "false",
    },
    # TODO: This should be ideally a string, not sure why we are receiving this, need to test it in prod studio for list jobs
    {
        "Name": "TrainingJobStatus",
        "Operator": "Equals",
        "Value": SageMakerTrainingJobStatus.IN_PROGRESS,
    },
    {
        "Name": "TrainingStartTime",
        "Operator": "GreaterThanOrEqualTo",
        "Value": datetime.fromtimestamp(query.start_time, pytz.utc),
    },
    {"Name": "Tags.sagemaker:name", "Operator": "Contains", "Value": query.name},
    {
        "Name": "Tags.sagemaker:job-definition-id",
        "Operator": "Equals",
        "Value": query.job_definition_id,
    },
]


@pytest.mark.asyncio
@patch(
     "sagemaker_studio_jupyter_scheduler.providers.image_metadata.get_sagemaker_environment",
     return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
)
@patch(
     "sagemaker_studio_jupyter_scheduler.model.model_converter.get_sagemaker_environment",
     return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
)
@patch.object(InternalMetadataAdapter, "__init__", return_value=None)
async def test_search_list_jobs_filters_standalone(mock_get_sagemaker_environment2, mock_get_sagemaker_environment, mock_adapter):
    scheduler = create_scheduler_with_mocked_dependencies()
    scheduler.converter = ModelConverter(MagicMock())

    mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
    scheduler._sagemaker_client = mock_sagemaker_client

    scheduler.converter.to_jupyter_list_jobs_response = MagicMock()

    await scheduler.list_jobs(query)
    actual_filters = mock_sagemaker_client.search.call_args_list[0].args[0][
        "SearchExpression"
    ]["Filters"]
    compare_tag_list(actual_filters, expected_common_filters, key_name="Name")


TEST_USER_DETAILS_PROFILE = UserDetails(
    user_id_key=UserTypes.PROFILE_USER, user_id_value="user-profile-1"
)


@pytest.mark.asyncio
@patch(
     "sagemaker_studio_jupyter_scheduler.model.model_converter.get_sagemaker_environment",
     return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
)
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_sagemaker_environment")
@patch("sagemaker_studio_jupyter_scheduler.providers.tags.get_user_details")
@patch.object(InternalMetadataAdapter, "__init__", return_value=None)
async def test_search_list_jobs_filters_studio(
    mock_adapter, mock_user_details, mock_get_environment, mock_get_sagemaker_environment
):
    mock_get_environment.return_value = JupyterLabEnvironment.SAGEMAKER_STUDIO
    mock_user_details.return_value = TEST_USER_DETAILS_PROFILE
    scheduler = create_scheduler_with_mocked_dependencies()
    scheduler.converter = ModelConverter(MagicMock())
    query = MagicMock()
    query.status = Status.IN_PROGRESS
    query.job_definition_id = "test-jod-definition-id"
    query.start_time = datetime(2023, 5, 10).timestamp()
    query.max_items = 25
    query.sort_by = None
    query.name = "test-job-name"

    mock_sagemaker_client = AsyncMock(spec=SageMakerAsyncBoto3Client)
    scheduler._sagemaker_client = mock_sagemaker_client

    scheduler.converter.to_jupyter_list_jobs_response = MagicMock()

    # mock_get_environment.

    await scheduler.list_jobs(query)
    actual_filters = mock_sagemaker_client.search.call_args_list[0].args[0][
        "SearchExpression"
    ]["Filters"]
    compare_tag_list(
        actual_filters,
        expected_common_filters,
        key_name="Name",
    )


@pytest.mark.asyncio
async def test_list_job_with_max_items_as_zero():
    scheduler = create_scheduler_with_mocked_dependencies()
    query = MagicMock()
    query.max_items = 0

    response = await scheduler.list_jobs(query)
    assert response.jobs == []


@pytest.mark.asyncio
async def test_prepare_job_artifacts_region_check_same_bucket():
    BUCKET_REGION = "us-west-2"
    AWS_REGION = "us-east-1"
    scheduler = create_scheduler_with_mocked_dependencies()
    mock_runtime_envs = MagicMock()
    TEST_S3_BUCKET_NAME = "customer-bucket"
    TEST_S3_INPUT = f"s3://{TEST_S3_BUCKET_NAME}/scheduling"
    mock_runtime_envs.s3_input = TEST_S3_INPUT
    mock_runtime_envs.s3_output = TEST_S3_INPUT

    mock_s3_client = AsyncMock()
    mock_s3_client.get_bucket_location.return_value = {
        "LocationConstraint": BUCKET_REGION
    }
    scheduler._s3_client = mock_s3_client
    with patch(
        "sagemaker_studio_jupyter_scheduler.scheduler.scheduler.get_region_name",
        return_value=AWS_REGION,
    ):
        try:
            await scheduler._prepare_job_artifacts(
                AsyncMock(), "test-training", AsyncMock(), mock_runtime_envs, "/home", []
            )
        except Exception as ex:
            assert isinstance(ex, SchedulerError)
            assert (
                str(ex)
                == f"S3 bucket {TEST_S3_BUCKET_NAME} must be in region '{AWS_REGION}', but found in '{BUCKET_REGION}'"
            )


@pytest.mark.asyncio
async def test_prepare_job_artifacts_region_check_different_bucket():
    INPUT_BUCKET_REGION = "us-east-1"
    OUTPUT_BUCKET_REGION = "us-west-2"
    AWS_REGION = "us-east-1"
    scheduler = create_scheduler_with_mocked_dependencies()
    mock_runtime_envs = MagicMock()
    TEST_INPUT_S3_BUCKET_NAME = "customer-bucket-input"
    TEST_OUTPUT_S3_BUCKET_NAME = "customer-bucket-output"
    mock_runtime_envs.s3_input = f"s3://{TEST_INPUT_S3_BUCKET_NAME}/input"
    mock_runtime_envs.s3_output = f"s3://{TEST_OUTPUT_S3_BUCKET_NAME}/output"

    mock_s3_client = AsyncMock()

    mock_s3_client.get_bucket_location.side_effect = [
        {"LocationConstraint": INPUT_BUCKET_REGION},
        {"LocationConstraint": OUTPUT_BUCKET_REGION},
    ]
    scheduler._s3_client = mock_s3_client
    with patch(
        "sagemaker_studio_jupyter_scheduler.scheduler.scheduler.get_region_name",
        return_value=AWS_REGION,
    ):
        try:
            await scheduler._prepare_job_artifacts(
                AsyncMock(), "test-training", AsyncMock(), mock_runtime_envs, "/home", []
            )
        except Exception as ex:
            assert isinstance(ex, SchedulerError)
            assert (
                str(ex)
                == f"S3 bucket {TEST_OUTPUT_S3_BUCKET_NAME} must be in region '{AWS_REGION}', but found in '{OUTPUT_BUCKET_REGION}'"
            )

@patch.object(STSAsyncBotoClient, "get_caller_identity")
@pytest.mark.asyncio
async def test_meaningful_error_message_create_job_getbucketlocation(mock_get_caller_identity):
    mock_get_caller_identity.return_value = MOCK_CALLER_IDENTITY
    scheduler = create_scheduler_with_mocked_dependencies()

    scheduler._s3_client.get_bucket_location.return_value = future_with_exception(
        botocore.exceptions.ClientError(
            {
                "Error": {"Code": "AccessDenied", "Message": "Access Denied"},
            },
            "GetBucketLocation",
        )
    )

    create_job_input = CreateJob(
        input_uri="mock-input-uri",
        name="mock-job-1",
        runtime_environment_name="mock-environment-name",
        runtime_environment_parameters={
            "s3_input": "s3://mock-bucket/mock-path",
            "s3_output": "s3://mock-bucket/mock-path",
        }
    )
    with pytest.raises(SchedulerError) as error:
        await scheduler.create_job(create_job_input)

    assert (
        str(error.value)
        == f"AccessDenied: Access Denied, operation: GetBucketLocation. Failed to verify bucket location and owner for {{'mock-bucket'}}, {ACCESS_DENIED_ERROR_MESSAGE}"
    )


class TestHandleAwsClientError:
    @pytest.fixture
    def scheduler(self):
        # Create a mock scheduler instance with a mock logger
        scheduler = create_scheduler_with_mocked_dependencies()
        return scheduler

    @pytest.fixture
    def sample_boto_error(self):
        return botocore.exceptions.ClientError(
            error_response={
                'Error': {
                    'Code': 'ValidationError',
                    'Message': 'Sample boto error'
                }
            },
            operation_name='TestOperation'
        )

    def test_scheduler_error_handling(self, scheduler):
        """Test handling of SchedulerError"""
        scheduler_error = SchedulerError("Test scheduler error")

        with pytest.raises(SchedulerError) as exc_info:
            scheduler.handle_aws_client_error(scheduler_error)

        assert exc_info.value == scheduler_error
        # Verify no logging occurred
        scheduler.log.error.assert_not_called()

    @pytest.mark.parametrize("log_message", [
        None,
        "Custom error message",
        "Error during SageMaker operation"
    ])
    def test_boto_client_error_handling(self, scheduler, sample_boto_error, log_message):
        """Test handling of boto ClientError with different log messages"""
        with pytest.raises(SageMakerSchedulerError) as exc_info:
            scheduler.handle_aws_client_error(sample_boto_error, log_message)

        if log_message is not None:
            scheduler.log.error.assert_called_once_with(
                f"[SageMakerScheduler] Boto client Error: {log_message}"
            )
        else:
            scheduler.log.error.assert_not_called()

        assert isinstance(exc_info.value, SageMakerSchedulerError)

    @pytest.mark.parametrize("error_code,error_message", [
        ("ResourceNotFound", "Resource not found"),
        ("ValidationError", "Invalid parameter value"),
        ("AccessDenied", "Access denied"),
        ("ThrottlingException", "Request was throttled")
    ])
    def test_different_boto_error_types(self, scheduler, error_code, error_message):
        """Test handling of different types of boto ClientErrors"""
        boto_error = botocore.exceptions.ClientError(
            error_response={
                'Error': {
                    'Code': error_code,
                    'Message': error_message
                }
            },
            operation_name='TestOperation'
        )

        with pytest.raises(SageMakerSchedulerError) as exc_info:
            scheduler.handle_aws_client_error(boto_error, f"Error: {error_code}")

        scheduler.log.error.assert_called_once()
        assert error_code in str(boto_error)

    @pytest.mark.parametrize("runtime_error_msg", [
        "Generic runtime error",
        "Operation timeout",
        "Invalid operation"
    ])
    def test_runtime_error_handling(self, scheduler, runtime_error_msg):
        """Test handling of RuntimeError with different messages"""
        runtime_error = RuntimeError(runtime_error_msg)

        with pytest.raises(SageMakerSchedulerError) as exc_info:
            scheduler.handle_aws_client_error(runtime_error, "Runtime error occurred")

        scheduler.log.error.assert_called_once_with(
            "[SageMakerScheduler] Runtime Error: Runtime error occurred"
        )
        assert isinstance(exc_info.value, SageMakerSchedulerError)

    def test_runtime_error_without_message(self, scheduler):
        """Test handling of RuntimeError without log message"""
        runtime_error = RuntimeError("Test runtime error")

        with pytest.raises(SageMakerSchedulerError):
            scheduler.handle_aws_client_error(runtime_error)

        scheduler.log.error.assert_not_called()

    @patch.object(InternalMetadataAdapter, "__init__", return_value=None)
    @patch.object(InternalMetadataAdapter, "get_app_network_access_type", return_value=MOCK_NETWORK_ACCESS_TYPE)
    def test_connection_related_errors(self, mock_adapter_network_access_type, mock_adapter_init, scheduler):
        """Test handling of connection-related boto errors"""
        # Set up the return value directly on the method chain

        connection_errors = [
            botocore.exceptions.ConnectTimeoutError(endpoint_url="https://test-endpoint"),
            botocore.exceptions.EndpointConnectionError(endpoint_url="https://test-endpoint"),
            botocore.exceptions.ConnectionError(error="Connection refused")
        ]

        for error in connection_errors:
            with pytest.raises(SageMakerSchedulerError):
                scheduler.handle_aws_client_error(error, "Connection error occurred")

            print (f"Testing error: {error.__class__.__name__}")
            if isinstance(error, botocore.exceptions.EndpointConnectionError):
                scheduler.log.error.assert_called_with(
                    f"[SageMakerScheduler] Endpoint Connection Error: Connection error occurred"
                )
            else:
                scheduler.log.error.assert_called_with(
                    f"[SageMakerScheduler] {error.__class__.__name__}: Connection error occurred"
                )
            scheduler.log.error.reset_mock()

    def test_error_with_empty_log_message(self, scheduler, sample_boto_error):
        """Test handling errors with empty log message"""
        with pytest.raises(SageMakerSchedulerError):
            scheduler.handle_aws_client_error(sample_boto_error, "")

        scheduler.log.error.assert_called_once_with(
            "[SageMakerScheduler] Boto client Error: "
        )

    @pytest.mark.parametrize("error_instance", [
        ValueError("Invalid value"),
        TypeError("Invalid type"),
        KeyError("Missing key"),
        IndexError("Index out of range")
    ])
    def test_unhandled_error_types(self, scheduler, error_instance):
        """Test handling of error types not explicitly handled"""
        with pytest.raises(Exception):
            scheduler.handle_aws_client_error(error_instance, "Unexpected error")

    def test_nested_boto_errors(self, scheduler):
        """Test handling of nested boto errors"""
        nested_error = botocore.exceptions.ClientError(
            error_response={
                'Error': {
                    'Code': 'ValidationError',
                    'Message': 'Outer error',
                    'Details': {
                        'InnerError': {
                            'Code': 'ResourceNotFound',
                            'Message': 'Inner error'
                        }
                    }
                }
            },
            operation_name='TestOperation'
        )

        with pytest.raises(SageMakerSchedulerError) as exc_info:
            scheduler.handle_aws_client_error(nested_error, "Nested error occurred")

        scheduler.log.error.assert_called_once()
        assert isinstance(exc_info.value, SageMakerSchedulerError)
