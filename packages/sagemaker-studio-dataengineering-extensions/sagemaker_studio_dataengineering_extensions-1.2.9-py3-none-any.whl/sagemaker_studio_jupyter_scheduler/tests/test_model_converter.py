import os
import pytest
import json
from datetime import datetime
from dateutil import parser
from unittest.mock import patch, Mock
from jupyter_scheduler.models import (
    SortDirection,
    Status,
    CreateJob,
    ListJobDefinitionsQuery,
)
from botocore.session import Session
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
)
from sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter import (
    InternalMetadataAdapter,
)

from sagemaker_studio_jupyter_scheduler.model.models import EventBridgeRuleStatus, RuntimeEnvironmentParameterName
from sagemaker_studio_jupyter_scheduler.model.model_converter import ModelConverter
from sagemaker_studio_jupyter_scheduler.tests.data.mock_files import (
    MOCK_INTERNAL_METADATA,
    MOCK_RESOURCE_METADATA,
    MOCK_STORAGE_METADATA,
    MOCK_VANILLA_METADATA,
)
from sagemaker_studio_jupyter_scheduler.tests.helpers.utils import (
    create_mock_open,
    MockConfig,
)


custom_mock_open = create_mock_open(
    {
        "/opt/.sagemakerinternal/internal-metadata.json": MOCK_INTERNAL_METADATA,
        "/opt/ml/metadata/resource-metadata.json": MOCK_RESOURCE_METADATA,
        "/home/sagemaker-user/.config/smus-storage-metadata.json": MOCK_STORAGE_METADATA,
    }
)


@patch("builtins.open", custom_mock_open)
def test_to_jupyter_job_status():
    converter = ModelConverter(Mock())
    assert converter.to_jupyter_job_status("InProgress").value == "IN_PROGRESS"
    assert converter.to_jupyter_job_status("Completed").value == "COMPLETED"
    assert converter.to_jupyter_job_status("Failed").value == "FAILED"
    assert converter.to_jupyter_job_status("Stopping").value == "STOPPING"
    assert converter.to_jupyter_job_status("Stopped").value == "STOPPED"


@patch("builtins.open", custom_mock_open)
def test_to_training_job_status():
    converter = ModelConverter(Mock())
    assert converter.to_training_job_status(Status.IN_PROGRESS).value == "InProgress"
    assert converter.to_training_job_status(Status.COMPLETED).value == "Completed"
    assert converter.to_training_job_status(Status.FAILED).value == "Failed"
    assert converter.to_training_job_status(Status.STOPPING).value == "Stopping"
    assert converter.to_training_job_status(Status.STOPPED).value == "Stopped"


@patch("builtins.open", custom_mock_open)
def test_to_sagemaker_sort_order():
    converter = ModelConverter(Mock())
    assert converter.to_sagemaker_sort_order(SortDirection.asc).value == "Ascending"
    assert converter.to_sagemaker_sort_order(SortDirection.desc).value == "Descending"


@patch("builtins.open", custom_mock_open)
def test_to_tag_dict():
    assert ModelConverter(Mock()).to_tag_dict(
        [
            {
                "Key": "tag 1 key",
                "Value": "tag 1 value",
            },
            {
                "Key": "tag 2 key",
                "Value": "tag 2 value",
            },
        ]
    ) == {
        "tag 1 key": "tag 1 value",
        "tag 2 key": "tag 2 value",
    }


@patch("builtins.open", custom_mock_open)
def test_to_tag_list():
    assert ModelConverter(Mock()).to_tag_list(
        {"tag 1 key": "tag 1 value", "tag 2 key": "tag 2 value"}
    ) == [
        {
            "Key": "tag 1 key",
            "Value": "tag 1 value",
        },
        {
            "Key": "tag 2 key",
            "Value": "tag 2 value",
        },
    ]


@patch("builtins.open", custom_mock_open)
def test_to_jupyter_describe_job_output():
    mock_scheduler = Mock()
    mock_scheduler.environments_manager.output_formats_mapping.return_value = {
        "ipynb": "Notebook",
    }
    describe_jupyter_job_output = ModelConverter(Mock()).to_jupyter_describe_job_output(
        scheduler=mock_scheduler,
        outputs=True,
        training_job_response={
            "TrainingJobName": "a-b-c-d",
            "InputDataConfig": [
                {"DataSource": {"S3DataSource": {"S3Uri": "s3://data-source-uri"}}}
            ],
            "OutputDataConfig": {
                "S3OutputPath": "s3://output-path",
                "KmsKeyId": "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-8741-038652abcf94",
            },
            "HyperParameters": {
                "hyper param 1": "hyper param 1 value",
                "hyper param 2": "hyper param 2 value",
            },
            "Environment": {
                "SM_ENV_NAME": "sagemaker-default-env",
                "SM_OUTPUT_FORMATS": "ipynb",
                "environment property 1": "environment property 1 value",
                "environment property 2": "environment property 2 value",
            },
            "RoleArn": "arn:aws:iam::177118115371:role/service-role/AmazonSageMaker-ExecutionRole-20220125T140052",
            "StoppingCondition": {"MaxRuntimeInSeconds": 300},
            "RetryStrategy": {"MaximumRetryAttempts": 3},
            "ResourceConfig": {
                "InstanceType": "ml.m5.2xlarge",
                "VolumeKmsKeyId": "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-038652abcf94",
            },
            "TrainingJobStatus": "Failed",
            "CreationTime": datetime.fromisoformat("2022-09-29T10:24:26-07:00"),
            "TrainingStartTime": datetime.fromisoformat("2022-09-29T10:26:12-07:00"),
            "TrainingEndTime": datetime.fromisoformat("2022-09-29T10:28:19-07:00"),
            "LastModifiedTime": datetime.fromisoformat("2022-09-29T10:28:21-07:00"),
            "FailureReason": "Algorithm error: [SM-111] 123",
        },
        tag_dict={
            "sagemaker:name": "My Training Job",
            "sagemaker:job-definition-id": "my-job-definition",
        },
    )

    assert describe_jupyter_job_output.job_id == "a-b-c-d"
    assert describe_jupyter_job_output.output_formats == ["ipynb", "log"]
    assert describe_jupyter_job_output.input_filename == ""
    assert (
        describe_jupyter_job_output.runtime_environment_name == "sagemaker-default-env"
    )
    assert describe_jupyter_job_output.name == "My Training Job"
    assert describe_jupyter_job_output.job_definition_id == "my-job-definition"
    assert describe_jupyter_job_output.parameters == {
        "hyper param 1": "hyper param 1 value",
        "hyper param 2": "hyper param 2 value",
    }
    assert describe_jupyter_job_output.runtime_environment_parameters == {
        "enable_network_isolation": 0,
        "environment property 1": "environment property 1 value",
        "environment property 2": "environment property 2 value",
        "role_arn": "arn:aws:iam::177118115371:role/service-role/AmazonSageMaker-ExecutionRole-20220125T140052",
        "s3_input": "s3://data-source-uri",
        "s3_output": "s3://output-path",
        # TODO: Mock these values in the input, and update the assertion here.
        "sm_image": "",
        "sm_init_script": "",
        "sm_kernel": "",
        "sm_lcc_init_script_arn": "",
        "vpc_security_group_ids": "",
        "vpc_subnets": "",
        "sm_output_kms_key": "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-8741-038652abcf94",
        "sm_volume_kms_key": "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-038652abcf94",
        'max_retry_attempts': 3,
        'max_run_time_in_seconds': 300,
    }
    assert describe_jupyter_job_output.compute_type == "ml.m5.2xlarge"
    assert describe_jupyter_job_output.status.value == "FAILED"
    assert describe_jupyter_job_output.create_time == 1664472266000
    assert describe_jupyter_job_output.start_time == 1664472372000
    assert describe_jupyter_job_output.end_time == 1664472499000
    assert describe_jupyter_job_output.update_time == 1664472501000
    assert describe_jupyter_job_output.status_message == "Algorithm error: 123"

@patch("builtins.open", custom_mock_open)
def test_to_jupyter_describe_job_output_status_message():
    mock_scheduler = Mock()
    mock_scheduler.environments_manager.output_formats_mapping.return_value = {
        "ipynb": "Notebook",
    }
    describe_jupyter_job_output = ModelConverter(Mock()).to_jupyter_describe_job_output(
        scheduler=mock_scheduler,
        outputs=True,
        training_job_response={
            "TrainingJobName": "a-b-c-d",
            "InputDataConfig": [
                {"DataSource": {"S3DataSource": {"S3Uri": "s3://data-source-uri"}}}
            ],
            "OutputDataConfig": {
                "S3OutputPath": "s3://output-path",
                "KmsKeyId": "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-8741-038652abcf94",
            },
            "HyperParameters": {
                "hyper param 1": "hyper param 1 value",
                "hyper param 2": "hyper param 2 value",
            },
            "Environment": {
                "SM_ENV_NAME": "sagemaker-default-env",
                "SM_OUTPUT_FORMATS": "ipynb",
                "environment property 1": "environment property 1 value",
                "environment property 2": "environment property 2 value",
            },
            "RoleArn": "arn:aws:iam::177118115371:role/service-role/AmazonSageMaker-ExecutionRole-20220125T140052",
            "StoppingCondition": {"MaxRuntimeInSeconds": 300},
            "RetryStrategy": {"MaximumRetryAttempts": 3},
            "ResourceConfig": {
                "InstanceType": "ml.m5.2xlarge",
                "VolumeKmsKeyId": "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-038652abcf94",
            },
            "TrainingJobStatus": "Stopped",
            "SecondaryStatus": "MaxRuntimeExceeded",
            "CreationTime": datetime.fromisoformat("2022-09-29T10:24:26-07:00"),
            "TrainingStartTime": datetime.fromisoformat("2022-09-29T10:26:12-07:00"),
            "TrainingEndTime": datetime.fromisoformat("2022-09-29T10:28:19-07:00"),
            "LastModifiedTime": datetime.fromisoformat("2022-09-29T10:28:21-07:00"),
            "FailureReason": "Algorithm error: [SM-111] 123",
        },
        tag_dict={
            "sagemaker:name": "My Training Job",
            "sagemaker:job-definition-id": "my-job-definition",
        },
    )

    assert describe_jupyter_job_output.job_id == "a-b-c-d"
    assert describe_jupyter_job_output.output_formats == ["ipynb", "log"]
    assert describe_jupyter_job_output.input_filename == ""
    assert (
        describe_jupyter_job_output.runtime_environment_name == "sagemaker-default-env"
    )
    assert describe_jupyter_job_output.name == "My Training Job"
    assert describe_jupyter_job_output.job_definition_id == "my-job-definition"
    assert describe_jupyter_job_output.parameters == {
        "hyper param 1": "hyper param 1 value",
        "hyper param 2": "hyper param 2 value",
    }
    assert describe_jupyter_job_output.runtime_environment_parameters == {
        "enable_network_isolation": 0,
        "environment property 1": "environment property 1 value",
        "environment property 2": "environment property 2 value",
        "role_arn": "arn:aws:iam::177118115371:role/service-role/AmazonSageMaker-ExecutionRole-20220125T140052",
        "s3_input": "s3://data-source-uri",
        "s3_output": "s3://output-path",
        # TODO: Mock these values in the input, and update the assertion here.
        "sm_image": "",
        "sm_init_script": "",
        "sm_kernel": "",
        "sm_lcc_init_script_arn": "",
        "vpc_security_group_ids": "",
        "vpc_subnets": "",
        "sm_output_kms_key": "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-8741-038652abcf94",
        "sm_volume_kms_key": "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-038652abcf94",
        'max_retry_attempts': 3,
        'max_run_time_in_seconds': 300,
    }
    assert describe_jupyter_job_output.compute_type == "ml.m5.2xlarge"
    assert describe_jupyter_job_output.status.value == "FAILED"
    assert describe_jupyter_job_output.create_time == 1664472266000
    assert describe_jupyter_job_output.start_time == 1664472372000
    assert describe_jupyter_job_output.end_time == 1664472499000
    assert describe_jupyter_job_output.update_time == 1664472501000
    assert describe_jupyter_job_output.status_message == "MaxRuntimeExceeded"

def generate_mock_create_job(image_arn):
    return CreateJob(
        input_uri="Untitled.ipynb",
        output_formats=["ipynb"],
        runtime_environment_name="sagemaker-default-env",
        runtime_environment_parameters={
            "sm_lcc_init_script_arn": "No script",
            "role_arn": "arn:aws:iam::748478975813:role/service-role/AmazonSageMaker-ExecutionRole-20220409T160852",
            "vpc_security_group_ids": "sg-0b674de38a404b2f8",
            "vpc_subnets": "subnet-026130d572cbc21d5,subnet-026130d5723cbwesd21sd5",
            "s3_input": "s3://sagemaker-notebook-execution-748478975813/",
            "s3_output": "s3://sagemaker-notebook-execution-748478975813/",
            "sm_kernel": "python3",
            "sm_image": image_arn,
            "executionEnvironment": "",
            "sm_init_script": "",
            "sm_output_kms_key": "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-8741-038652abcf94",
            "sm_volume_kms_key": "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-8741-038652abcf94",
            "max_retry_attempts": 1,
            "max_run_time_in_seconds": 172800,
            "NonStringEnvironmentVariable": 1234567890,
        },
        name="NotebookA.ipynb",
        compute_type="ml.m4.xlarge",
    )

mock_create_job = generate_mock_create_job("arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0")

@pytest.mark.asyncio
@patch("builtins.open", custom_mock_open)
@patch.object(Session, "get_scoped_config")
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.image_metadata.get_sagemaker_environment",
    return_value=JupyterLabEnvironment.SAGEMAKER_STUDIO,
)
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.revenue.get_sagemaker_environment",
    return_value=JupyterLabEnvironment.SAGEMAKER_STUDIO,
)
async def test_training_job_container__first_party_image__success(
    mock_detector,
    mock_detector_2,
    mock_get_scoped_config,
):
    mock_get_scoped_config.return_value = MockConfig
    mock_s3_uploader = Mock()
    mock_s3_uploader.notebook_name = "my-notebook.ipynb"
    MOCK_TRAINING_JOB_NAME = "mock-training-job-name"
    output = await ModelConverter(Mock()).to_create_training_job_input(
        MOCK_TRAINING_JOB_NAME,
        mock_create_job,
        mock_s3_uploader,
    )
    assert output["AlgorithmSpecification"] == {
        "TrainingImage": "236514542706.dkr.ecr.us-west-2.amazonaws.com/sagemaker-data-science-environment:1.0",
        "TrainingInputMode": "File",
        "ContainerEntrypoint": ["amazon_sagemaker_scheduler"],
    }

    assert (
        output["OutputDataConfig"]["KmsKeyId"]
        == "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-8741-038652abcf94"
    )

    assert (
        output["ResourceConfig"]["VolumeKmsKeyId"]
        == "arn:aws:kms:us-west-2:344324978117:key/e5cdae90-20db-4e1c-8741-038652abcf94"
    )

    assert (
        output["InputDataConfig"][0]["DataSource"]["S3DataSource"]["S3Uri"]
        == f"s3://sagemaker-notebook-execution-748478975813/{MOCK_TRAINING_JOB_NAME}/input"
    )

    assert (
        output["InputDataConfig"][0]["ChannelName"]
        == f"sagemaker_headless_execution"
    )

    assert (
        output["Environment"]["SM_EXECUTION_INPUT_PATH"]
        == f"/opt/ml/input/data/sagemaker_headless_execution"
    )

    assert output["VpcConfig"] == {
        "SecurityGroupIds": ["sg-0b674de38a404b2f8"],
        "Subnets": ["subnet-026130d572cbc21d5", "subnet-026130d5723cbwesd21sd5"],
    }

    assert output["EnableInterContainerTrafficEncryption"] == True


@pytest.mark.asyncio
@patch("builtins.open", custom_mock_open)
@patch.object(Session, "get_scoped_config")
@patch(
    "sagemaker_studio_jupyter_scheduler.providers.image_metadata.get_sagemaker_environment",
    return_value=JupyterLabEnvironment.SAGEMAKER_STUDIO,
)
async def test_training_job_container__first_party_image_without_root__success(
    mock_detector,
    mock_get_scoped_config,
):
    mock_get_scoped_config.return_value = MockConfig
    mock_s3_uploader = Mock()
    mock_s3_uploader.notebook_name = "my-notebook.ipynb"
    MOCK_TRAINING_JOB_NAME = "mock-training-job-name"
    output = await ModelConverter(Mock()).to_create_training_job_input(
        MOCK_TRAINING_JOB_NAME,
        generate_mock_create_job("arn:aws:sagemaker:us-west-2:123456789012:image/sagemaker-distribution-gpu-v0"),
        mock_s3_uploader,
    )
    assert output["AlgorithmSpecification"] == {
        "TrainingImage": "123456789012.dkr.ecr.us-west-2.amazonaws.com/sagemaker-distribution-prod:0.4.1-gpu",
        "TrainingInputMode": "File",
        "ContainerEntrypoint": ["amazon_sagemaker_scheduler"],
    }

    assert output["Environment"]["NonStringEnvironmentVariable"] == "1234567890"


def test_to_jupyter_describe_job_definition_output():
    pipeline_training_definition_string = '{\"Version\": \"2020-12-01\", \"Parameters\": [], \"Steps\": [{\"Name\": \"retrybug-Untitled\", \"Type\": \"Training\", \"Arguments\": {\"AlgorithmSpecification\": {\"TrainingImage\": \"542918446943.dkr.ecr.us-west-2.amazonaws.com/sagemaker-distribution-prod@sha256:43bf7d7d74cdde53367bf3e93e040d93fca845ce61fbdb7cc7dec0385baed205\", \"TrainingInputMode\": \"File\", \"ContainerEntrypoint\": [\"amazon_sagemaker_scheduler\"]},"HyperParameters": {"company": "amazon", "user": "sunp"}, \"Environment\": {\"SM_JOB_DEF_VERSION\": \"1.0\", \"SM_FIRST_PARTY_IMAGEOWNER\": \"jupyterlab\", \"SM_FIRST_PARTY_IMAGE_ARN\": \"542918446943.dkr.ecr.us-west-2.amazonaws.com/sagemaker-distribution-prod@sha256:43bf7d7d74cdde53367bf3e93e040d93fca845ce61fbdb7cc7dec0385baed205\", \"SM_KERNEL_NAME\": \"python3\", \"SM_SKIP_EFS_SIMULATION\": \"\", \"SM_EFS_MOUNT_PATH\": \"/home/sagemaker-user\", \"SM_EFS_MOUNT_UID\": \"1000\", \"SM_EFS_MOUNT_GID\": \"100\", \"SM_INPUT_NOTEBOOK_NAME\": \"Untitled.ipynb\", \"SM_OUTPUT_NOTEBOOK_NAME\": {\"Std:Join\": {\"On\": \"-\", \"Values\": [\"retrybug\", \"Untitled\", {\"Get\": \"Execution.StartDateTime\"}, \".ipynb\"]}}, \"AWS_DEFAULT_REGION\": \"us-west-2\", \"SM_ENV_NAME\": \"sagemaker-default-env\", \"SM_OUTPUT_FORMATS\": \"\", \"SM_EXECUTION_INPUT_PATH\": \"/opt/ml/input/data/sagemaker_headless_execution_jupyterlab\"}, \"InputDataConfig\": [{\"ChannelName\": \"sagemaker_headless_execution_jupyterlab\", \"DataSource\": {\"S3DataSource\": {\"S3DataType\": \"S3Prefix\", \"S3Uri\": \"s3://sagemaker-automated-execution-239533537436-us-west-2/retrybug-Untitled-07880322-2024-03-28-20-55-03/input\", \"S3DataDistributionType\": \"FullyReplicated\"}}}], \"OutputDataConfig\": {\"S3OutputPath\": \"s3://sagemaker-automated-execution-239533537436-us-west-2/retrybug-Untitled-07880322-2024-03-28-20-55-03\"}, \"ResourceConfig\": {\"InstanceCount\": 1, \"InstanceType\": \"ml.m5.large\", \"VolumeSizeInGB\": 30}, \"RetryStrategy\": {\"MaximumRetryAttempts\": 1}, \"RoleArn\": \"arn:aws:iam::239533537436:role/service-role/SageMaker-ExecutionRole-20240103T125832\", \"StoppingCondition\": {\"MaxRuntimeInSeconds\": 172800}, \"EnableInterContainerTrafficEncryption\": true, \"Tags\": [{\"Key\": \"sagemaker:name\", \"Value\": \"retrybug\"}, {\"Key\": \"sagemaker:notebook-name\", \"Value\": \"Untitled.ipynb\"}, {\"Key\": \"sagemaker:is-scheduling-notebook-job\", \"Value\": \"true\"}, {\"Key\": \"sagemaker:is-studio-archived\", \"Value\": \"false\"}, {\"Key\": \"sagemaker:headless-execution-version\", \"Value\": \"false\"}, {\"Key\": \"sagemaker:shared-space-name\", \"Value\": \"htmllatest\"}, {\"Key\": \"sagemaker:user-profile-arn\", \"Value\": \"arn:aws:sagemaker:us-west-2:239533537436:user-profile/d-8j0xsamcdc5e/default-1705689164798\"}, {\"Key\": \"sagemaker:domain-arn\", \"Value\": \"arn:aws:sagemaker:us-west-2:239533537436:domain/d-8j0xsamcdc5e\"}, {\"Key\": \"sagemaker:job-definition-id\", \"Value\": \"retrybug-Untitled-07880322-2024-03-28-20-55-03\"}]}, \"RetryPolicies\": [{\"ExceptionType\": [\"Step.SERVICE_FAULT\", \"Step.THROTTLING\", \"SageMaker.JOB_INTERNAL_ERROR\", \"SageMaker.CAPACITY_ERROR\", \"SageMaker.RESOURCE_LIMIT\"], \"MaxAttempts\": 4}]}]}'
    pipeline_training_definition = json.loads(pipeline_training_definition_string)

    mock_describe_job_definition = {
        "PipelineArn": "arn:aws:sagemaker:us-east-1:177118115371:pipeline/17d4a035-6416-4f00-95f3-ca6c193a98b5",
        "PipelineName": "17d4a035-6416-4f00-95f3-ca6c193a98b5",
        "PipelineDisplayName": "NotebookAJobDefinition",
        "PipelineDefinition": pipeline_training_definition_string,
        "PipelineDescription": "First pipeline job",
        "RoleArn": "arn:aws:iam::177118115371:role/service-role/AmazonSageMaker-ExecutionRole-20220125T140052",
        "PipelineStatus": "Active",
        "CreationTime": parser.parse("2022-10-07T13:45:07.314000-07:00"),
        "LastModifiedTime": parser.parse("2022-10-07T13:45:07.314000-07:00"),
        "CreatedBy": {},
        "LastModifiedBy": {},
    }

    mock_describe_event_rule = {
        "Name": "ceab2bbb-5bd7-44e4-aaf9-3a554aa5b9a1",
        "Arn": "arn:aws:events:us-east-1:177118115371:rule/ceab2bbb-5bd7-44e4-aaf9-3a554aa5b9a1",
        "ScheduleExpression": "cron(0 20 * * ? *)",
        "State": "ENABLED",
        "Description": "Notebook A EB rule",
        "EventBusName": "default",
        "CreatedBy": "177118115371",
    }

    mock_list_tags = {
        "Tags": [
            {"Key": "sagemaker:name", "Value": "notebook-execution-a"},
            {
                "Key": "sagemaker:user-profile-name",
                "Value": "bhadrinp",
            },
            {"Key": "sagemaker:is-scheduling-notebook-job", "Value": "true"},
            {
                "Key": "sagemaker:notebook-name",
                "Value": "Notebook-a.ipynb",
            },
            {
                "Key": "sagemaker:job-definition-id",
                "Value": "8540227b-14b1-41b4-a8e9-6daa6efb8c62",
            },
            {"Key": "sagemaker:is-studio-archived", "Value": "false"},
            {"Key": "sagemaker:headless-execution-version", "Value": "false"},
            {"Key": "User Profile Tag1", "Value": "TagValue1"},
            {"Key": "User Profile Tag2", "Value": "TagValue2"},
            {"Key": "User Profile Tag3", "Value": "TagValue3"},
            {"Key": "User Profile Tag4", "Value": "TagValue4"},
        ]
    }

    output = ModelConverter(Mock()).to_jupyter_describe_job_definition_output(
        "17d4a035-6416-4f00-95f3-ca6c193a98b5",
        mock_describe_job_definition,
        mock_describe_event_rule,
        mock_list_tags,
    )

    expected_environment = pipeline_training_definition["Steps"][0]["Arguments"][
        "Environment"
    ]
    # TODO: need to fix the ordering of union for pydantic to read all of them as strings
    # assert output.runtime_environment_parameters == pipeline_training_definition["Steps"][0]["Arguments"]["Environment"]
    assert output.runtime_environment_name == expected_environment["SM_ENV_NAME"]
    assert (
        output.parameters
        == pipeline_training_definition["Steps"][0]["Arguments"]["HyperParameters"]
    )
    assert (
        output.compute_type
        == pipeline_training_definition["Steps"][0]["Arguments"]["ResourceConfig"][
            "InstanceType"
        ]
    )
    assert output.job_definition_id == mock_describe_job_definition["PipelineName"]
    assert (
        output.create_time
        == mock_describe_job_definition["CreationTime"].timestamp() * 1000
    )
    assert (
        output.update_time
        == mock_describe_job_definition["LastModifiedTime"].timestamp() * 1000
    )

    # IN PROGRESS - Tag & EB rule
    for tag in mock_list_tags["Tags"]:
        if tag["Key"] == "sagemaker:name":
            job_definition_name_from_customer = tag["Value"]

    assert output.tags == ModelConverter(
        Mock()
    ).extract_customer_tags_in_jupyter_format(mock_list_tags["Tags"])
    assert output.name == job_definition_name_from_customer
    assert output.schedule == "0 20 * * ?"
    assert output.timezone == "UTC"
    assert output.active == (
        mock_describe_event_rule["State"] == EventBridgeRuleStatus.ENABLED.value
    )
    assert output.input_filename == pipeline_training_definition['Steps'][0]['Arguments']['Environment']['SM_INPUT_NOTEBOOK_NAME']
    assert output.runtime_environment_parameters[RuntimeEnvironmentParameterName.MAX_RETRY_ATTEMPTS.value] == pipeline_training_definition["Steps"][0]["RetryPolicies"][0]["MaxAttempts"]


def test_to_pipeline_seach_input_happy_path():
    TEST_CREATE_TIME = 1665443057
    query = ListJobDefinitionsQuery(
        name="customer-provided-name",
        create_time=TEST_CREATE_TIME * 1000,
        max_items=1000,
        # tags=["key1", "key2"], TODO: decide the format from OSS UI
    )

    expected_filter = [
        {
            "Name": "Tags.sagemaker:is-studio-archived",
            "Operator": "Equals",
            "Value": "false",
        },
        {
            "Name": "Tags.sagemaker:name",
            "Operator": "Contains",
            "Value": "customer-provided-name",
        },
        {
            "Name": "CreationTime",
            "Operator": "GreaterThanOrEqualTo",
            "Value": datetime.fromtimestamp(TEST_CREATE_TIME).isoformat(),
        },
    ]
    output = ModelConverter(Mock()).to_pipeline_seach_input(query)
    print(output)

    assert output["MaxResults"] == 50
    assert output["Resource"] == "Pipeline"
    assert output["SearchExpression"]["Filters"] == expected_filter


def test_to_sagemaker_search_training_job_sort_field__known_fields__returns_converted_fields():
    converter = ModelConverter(Mock())
    assert converter.to_sagemaker_search_training_job_sort_field("") == "CreationTime"
    assert (
        converter.to_sagemaker_search_training_job_sort_field("name")
        == "Tags.sagemaker:name"
    )
    assert (
        converter.to_sagemaker_search_training_job_sort_field("input_filename")
        == "Environment.SM_INPUT_NOTEBOOK_NAME"
    )
    assert (
        converter.to_sagemaker_search_training_job_sort_field("create_time")
        == "CreationTime"
    )
    assert (
        converter.to_sagemaker_search_training_job_sort_field("status")
        == "TrainingJobStatus"
    )


def test_to_sagemaker_search_training_job_sort_field__unknown_field__raises_error():
    converter = ModelConverter(Mock())
    with pytest.raises(RuntimeError):
        converter.to_sagemaker_search_training_job_sort_field("unknown_field")


def test_to_sagemaker_search_pipeline_sort_field__known_fields__returns_converted_fields():
    converter = ModelConverter(Mock())
    assert converter.to_sagemaker_search_pipeline_sort_field("") == "LastModifiedTime"
    assert (
        converter.to_sagemaker_search_pipeline_sort_field("name")
        == "Tags.sagemaker:name"
    )
    assert (
        converter.to_sagemaker_search_pipeline_sort_field("input_filename")
        == "LastModifiedTime"
    )
    assert (
        converter.to_sagemaker_search_pipeline_sort_field("create_time")
        == "CreationTime"
    )


def test_to_sagemaker_search_pipeline_sort_field__unknown_fields__raises_error():
    converter = ModelConverter(Mock())
    with pytest.raises(RuntimeError):
        converter.to_sagemaker_search_pipeline_sort_field("unknown_field")


def test_determine_available_output_formats_and_failure_reason__completed_job__outputs_all_known_formats():
    assert ModelConverter(Mock()).determine_available_output_formats_and_failure_reason(
        Status.COMPLETED, None
    ) == (
        ["input", "ipynb", "log", "files"],
        None,
    )


def test_determine_available_output_formats_and_failure_reason__failed_job_unrecognized_error__no_outputs():
    assert ModelConverter(Mock()).determine_available_output_formats_and_failure_reason(
        Status.FAILED, "AlgorithmError: An error occurred"
    ) == (
        [],
        "AlgorithmError: An error occurred",
    )


def test_determine_available_output_formats_and_failure_reason__failed_job_with_no_notebook__outputs_only_input_and_log():
    assert ModelConverter(Mock()).determine_available_output_formats_and_failure_reason(
        Status.FAILED, "AlgorithmError: [SM-101] An error occurred"
    ) == (
        ["input", "log"],
        "AlgorithmError: An error occurred",
    )

def test_to_jupyter_describe_job_definition_output_no_retry_set():
    pipeline_training_definition_string = '{\"Version\": \"2020-12-01\", \"Parameters\": [], \"Steps\": [{\"Name\": \"retrybug-Untitled\", \"Type\": \"Training\", \"Arguments\": {\"AlgorithmSpecification\": {\"TrainingImage\": \"542918446943.dkr.ecr.us-west-2.amazonaws.com/sagemaker-distribution-prod@sha256:43bf7d7d74cdde53367bf3e93e040d93fca845ce61fbdb7cc7dec0385baed205\", \"TrainingInputMode\": \"File\", \"ContainerEntrypoint\": [\"amazon_sagemaker_scheduler\"]},"HyperParameters": {"company": "amazon", "user": "sunp"}, \"Environment\": {\"SM_JOB_DEF_VERSION\": \"1.0\", \"SM_FIRST_PARTY_IMAGEOWNER\": \"jupyterlab\", \"SM_FIRST_PARTY_IMAGE_ARN\": \"542918446943.dkr.ecr.us-west-2.amazonaws.com/sagemaker-distribution-prod@sha256:43bf7d7d74cdde53367bf3e93e040d93fca845ce61fbdb7cc7dec0385baed205\", \"SM_KERNEL_NAME\": \"python3\", \"SM_SKIP_EFS_SIMULATION\": \"\", \"SM_EFS_MOUNT_PATH\": \"/home/sagemaker-user\", \"SM_EFS_MOUNT_UID\": \"1000\", \"SM_EFS_MOUNT_GID\": \"100\", \"SM_INPUT_NOTEBOOK_NAME\": \"Untitled.ipynb\", \"SM_OUTPUT_NOTEBOOK_NAME\": {\"Std:Join\": {\"On\": \"-\", \"Values\": [\"retrybug\", \"Untitled\", {\"Get\": \"Execution.StartDateTime\"}, \".ipynb\"]}}, \"AWS_DEFAULT_REGION\": \"us-west-2\", \"SM_ENV_NAME\": \"sagemaker-default-env\", \"SM_OUTPUT_FORMATS\": \"\", \"SM_EXECUTION_INPUT_PATH\": \"/opt/ml/input/data/sagemaker_headless_execution_jupyterlab\"}, \"InputDataConfig\": [{\"ChannelName\": \"sagemaker_headless_execution_jupyterlab\", \"DataSource\": {\"S3DataSource\": {\"S3DataType\": \"S3Prefix\", \"S3Uri\": \"s3://sagemaker-automated-execution-239533537436-us-west-2/retrybug-Untitled-07880322-2024-03-28-20-55-03/input\", \"S3DataDistributionType\": \"FullyReplicated\"}}}], \"OutputDataConfig\": {\"S3OutputPath\": \"s3://sagemaker-automated-execution-239533537436-us-west-2/retrybug-Untitled-07880322-2024-03-28-20-55-03\"}, \"ResourceConfig\": {\"InstanceCount\": 1, \"InstanceType\": \"ml.m5.large\", \"VolumeSizeInGB\": 30}, \"RetryStrategy\": {\"MaximumRetryAttempts\": 1}, \"RoleArn\": \"arn:aws:iam::239533537436:role/service-role/SageMaker-ExecutionRole-20240103T125832\", \"StoppingCondition\": {\"MaxRuntimeInSeconds\": 172800}, \"EnableInterContainerTrafficEncryption\": true, \"Tags\": [{\"Key\": \"sagemaker:name\", \"Value\": \"retrybug\"}, {\"Key\": \"sagemaker:notebook-name\", \"Value\": \"Untitled.ipynb\"}, {\"Key\": \"sagemaker:is-scheduling-notebook-job\", \"Value\": \"true\"}, {\"Key\": \"sagemaker:is-studio-archived\", \"Value\": \"false\"}, {\"Key\": \"sagemaker:headless-execution-version\", \"Value\": \"false\"}, {\"Key\": \"sagemaker:shared-space-name\", \"Value\": \"htmllatest\"}, {\"Key\": \"sagemaker:user-profile-arn\", \"Value\": \"arn:aws:sagemaker:us-west-2:239533537436:user-profile/d-8j0xsamcdc5e/default-1705689164798\"}, {\"Key\": \"sagemaker:domain-arn\", \"Value\": \"arn:aws:sagemaker:us-west-2:239533537436:domain/d-8j0xsamcdc5e\"}, {\"Key\": \"sagemaker:job-definition-id\", \"Value\": \"retrybug-Untitled-07880322-2024-03-28-20-55-03\"}]}}]}'
    pipeline_training_definition = json.loads(pipeline_training_definition_string)

    mock_describe_job_definition = {
        "PipelineArn": "arn:aws:sagemaker:us-east-1:177118115371:pipeline/17d4a035-6416-4f00-95f3-ca6c193a98b5",
        "PipelineName": "17d4a035-6416-4f00-95f3-ca6c193a98b5",
        "PipelineDisplayName": "NotebookAJobDefinition",
        "PipelineDefinition": pipeline_training_definition_string,
        "PipelineDescription": "First pipeline job",
        "RoleArn": "arn:aws:iam::177118115371:role/service-role/AmazonSageMaker-ExecutionRole-20220125T140052",
        "PipelineStatus": "Active",
        "CreationTime": parser.parse("2022-10-07T13:45:07.314000-07:00"),
        "LastModifiedTime": parser.parse("2022-10-07T13:45:07.314000-07:00"),
        "CreatedBy": {},
        "LastModifiedBy": {},
    }

    mock_describe_event_rule = {
        "Name": "ceab2bbb-5bd7-44e4-aaf9-3a554aa5b9a1",
        "Arn": "arn:aws:events:us-east-1:177118115371:rule/ceab2bbb-5bd7-44e4-aaf9-3a554aa5b9a1",
        "ScheduleExpression": "cron(0 20 * * ? *)",
        "State": "ENABLED",
        "Description": "Notebook A EB rule",
        "EventBusName": "default",
        "CreatedBy": "177118115371",
    }

    mock_list_tags = {
        "Tags": [
            {"Key": "sagemaker:name", "Value": "notebook-execution-a"},
            {
                "Key": "sagemaker:user-profile-name",
                "Value": "bhadrinp",
            },
            {"Key": "sagemaker:is-scheduling-notebook-job", "Value": "true"},
            {
                "Key": "sagemaker:notebook-name",
                "Value": "Notebook-a.ipynb",
            },
            {
                "Key": "sagemaker:job-definition-id",
                "Value": "8540227b-14b1-41b4-a8e9-6daa6efb8c62",
            },
            {"Key": "sagemaker:is-studio-archived", "Value": "false"},
            {"Key": "sagemaker:headless-execution-version", "Value": "false"},
            {"Key": "User Profile Tag1", "Value": "TagValue1"},
            {"Key": "User Profile Tag2", "Value": "TagValue2"},
            {"Key": "User Profile Tag3", "Value": "TagValue3"},
            {"Key": "User Profile Tag4", "Value": "TagValue4"},
        ]
    }

    output = ModelConverter(Mock()).to_jupyter_describe_job_definition_output(
        "17d4a035-6416-4f00-95f3-ca6c193a98b5",
        mock_describe_job_definition,
        mock_describe_event_rule,
        mock_list_tags,
    )

    # we set it to 1
    assert output.runtime_environment_parameters[RuntimeEnvironmentParameterName.MAX_RETRY_ATTEMPTS.value] == 1
