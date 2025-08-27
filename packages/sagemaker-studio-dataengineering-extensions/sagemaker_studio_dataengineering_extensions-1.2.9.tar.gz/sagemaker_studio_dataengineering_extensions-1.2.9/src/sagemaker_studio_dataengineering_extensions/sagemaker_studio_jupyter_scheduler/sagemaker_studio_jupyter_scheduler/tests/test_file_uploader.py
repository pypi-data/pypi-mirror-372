from unittest.mock import patch, mock_open, call, Mock
import uuid
import botocore
from sagemaker_studio_jupyter_scheduler.s3_uri import S3URI
import pytest
import os
from sagemaker_studio_jupyter_scheduler.util.file_uploader import S3FileUploader
from sagemaker_studio_jupyter_scheduler.util.aws_clients import (
    S3AsyncBoto3Client,
    STSAsyncBotoClient,
    SageMakerAsyncBoto3Client,
)
from botocore.session import Session

os.environ["REGION_NAME"] = "us-east-1"

MOCK_RESOURCE_METADATA = """
{
  "ResourceArn": "arn:aws:sagemaker:us-west-2:112233445566:app/d-1a2b3c4d5e6f/fake-user/JupyterServer/default"
}
"""

MOCK_LCC_CONTENT = {
    "StudioLifecycleConfigArn": "arn:aws:sagemaker:us-east-1:177118115371:studio-lifecycle-config/junlyu-test-lcc-init",
    "StudioLifecycleConfigName": "junlyu-test-lcc-init",
    "CreationTime": "2022-09-27T22:57:20.786000-07:00",
    "LastModifiedTime": "2022-09-27T22:57:20.814000-07:00",
    "StudioLifecycleConfigContent": "IyEvYmluL2Jhc2gKCnRvdWNoIC9vcHQvbWwvb3V0cHV0L2RhdGEvaGVsbG8tZnJvbS1sY2MtaW5pdC1zY3JpcHQ=",
    "StudioLifecycleConfigAppType": "JupyterServer",
}

MOCK_REGION = "us-east-1"
MOCK_PARTITION = "aws"
MOCK_CALLER_IDENTITY = {"Account": "123456789012"}
MOCK_ACCOUNT_ID = "123456789012"


class TestFileUploader:
    @pytest.mark.asyncio
    @patch.object(S3AsyncBoto3Client, "get_bucket_encryption")
    @patch.object(S3AsyncBoto3Client, "upload_file")
    @patch.object(SageMakerAsyncBoto3Client, "describe_lcc")
    @patch.object(Session, "get_scoped_config")
    @patch.object(Session, "get_partition_for_region")
    @patch.object(STSAsyncBotoClient, "get_caller_identity")
    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
    async def test_upload__no_script_lcc__happy_path(
        self,
        mock_open_file,
        mock_get_caller_identity,
        mock_get_partition_for_region,
        mock_get_scoped_config,
        mock_describe_lcc,
        mock_upload_file,
        mock_get_bucket_encryption,
    ):
        assert S3AsyncBoto3Client.get_bucket_encryption is mock_get_bucket_encryption
        assert S3AsyncBoto3Client.upload_file is mock_upload_file
        assert SageMakerAsyncBoto3Client.describe_lcc is mock_describe_lcc
        assert STSAsyncBotoClient.get_caller_identity is mock_get_caller_identity
        # No error indicates the bucket has default encryption
        mock_get_bucket_encryption.return_value = {}
        mock_describe_lcc.return_value = MOCK_LCC_CONTENT

        mock_get_scoped_config.return_value.get.return_value = MOCK_REGION
        mock_get_partition_for_region.return_value = MOCK_PARTITION
        mock_get_caller_identity.return_value = MOCK_CALLER_IDENTITY

        TEST_NOTEBOOK_WITH_FILE_PATH = "milestone-1a/test-m1-notebook.ipynb"
        TEST_TRAINING_JOB_NAME = str(uuid.uuid4())
        TEST_S3_URI = "s3://sagemaker-us-east-1-177118115371/sunp-headless/test"

        uploader = S3FileUploader(
            deletable_resources=Mock(),
            s3_uri=TEST_S3_URI,
            file_upload_account_id=MOCK_ACCOUNT_ID,
            training_job_name=TEST_TRAINING_JOB_NAME,
            notebook_file_path=TEST_NOTEBOOK_WITH_FILE_PATH,
            sm_init_script="",
            sm_lcc_init_script_arn="No script",
            root_dir=os.getcwd(),
            packaged_file_paths=[]
        )
        await uploader.upload()

        mock_upload_file.assert_has_calls(
            [
                call(
                    os.path.join(os.getcwd(), TEST_NOTEBOOK_WITH_FILE_PATH),
                    S3URI(TEST_S3_URI).bucket,
                    os.path.join(
                        S3URI(TEST_S3_URI).key,
                        TEST_TRAINING_JOB_NAME,
                        "input",
                        "test-m1-notebook.ipynb",
                    ),
                    "123456789012",
                    encrypt=False,
                )
            ]
        )

    @pytest.mark.asyncio
    @patch.object(S3AsyncBoto3Client, "get_bucket_encryption")
    @patch.object(S3AsyncBoto3Client, "upload_file")
    @patch.object(SageMakerAsyncBoto3Client, "describe_lcc")
    @patch.object(Session, "get_scoped_config")
    @patch.object(Session, "get_partition_for_region")
    @patch.object(STSAsyncBotoClient, "get_caller_identity")
    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
    async def test_upload__bucket_default_unencrypted__encrypt_objects(
        self,
        mock_open_file,
        mock_get_caller_identity,
        mock_get_partition_for_region,
        mock_get_scoped_config,
        mock_describe_lcc,
        mock_upload_file,
        mock_get_bucket_encryption,
    ):
        assert S3AsyncBoto3Client.get_bucket_encryption is mock_get_bucket_encryption
        assert S3AsyncBoto3Client.upload_file is mock_upload_file
        assert SageMakerAsyncBoto3Client.describe_lcc is mock_describe_lcc
        assert STSAsyncBotoClient.get_caller_identity is mock_get_caller_identity
        mock_get_bucket_encryption.side_effect = botocore.client.ClientError(
            {
                "Error": {
                    "Code": "ServerSideEncryptionConfigurationNotFoundError",
                    "Message": "An error occurred (ServerSideEncryptionConfigurationNotFoundError) when calling the GetBucketEncryption operation: The server side encryption configuration was not found",
                }
            },
            "GetBucketEncryption",
        )
        mock_describe_lcc.return_value = MOCK_LCC_CONTENT
        mock_get_scoped_config.return_value.get.return_value = MOCK_REGION
        mock_get_partition_for_region.return_value = MOCK_PARTITION
        mock_get_caller_identity.return_value = MOCK_CALLER_IDENTITY

        TEST_NOTEBOOK_WITH_FILE_PATH = "milestone-1a/test-m1-notebook.ipynb"
        TEST_TRAINING_JOB_NAME = str(uuid.uuid4())
        TEST_S3_URI = "s3://sagemaker-us-east-1-177118115371/sunp-headless/test"
        TEST_ROOT_DIR = "/home/ec2-user"

        uploader = S3FileUploader(
            deletable_resources=Mock(),
            s3_uri=TEST_S3_URI,
            file_upload_account_id=MOCK_ACCOUNT_ID,
            training_job_name=TEST_TRAINING_JOB_NAME,
            notebook_file_path=TEST_NOTEBOOK_WITH_FILE_PATH,
            sm_init_script="",
            sm_lcc_init_script_arn="No script",
            root_dir=TEST_ROOT_DIR,
            packaged_file_paths=[]
        )
        await uploader.upload()

        mock_upload_file.assert_has_calls(
            [
                call(
                    os.path.join(TEST_ROOT_DIR, TEST_NOTEBOOK_WITH_FILE_PATH),
                    S3URI(TEST_S3_URI).bucket,
                    os.path.join(
                        S3URI(TEST_S3_URI).key,
                        TEST_TRAINING_JOB_NAME,
                        "input",
                        "test-m1-notebook.ipynb",
                    ),
                    "123456789012",
                    encrypt=True,
                )
            ]
        )
