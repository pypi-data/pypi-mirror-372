import os.path
import shutil
from base64 import b64decode
from typing import List

from sagemaker_studio_jupyter_scheduler.util.app_metadata import get_region_name
from sagemaker_studio_jupyter_scheduler.util.aws_clients import (
    get_s3_client,
    get_sagemaker_client,
)
from sagemaker_studio_jupyter_scheduler.util.aws_config import get_aws_account_id
from sagemaker_studio_jupyter_scheduler.util.deletable_resource import (
    DeletableResourceContainer,
    DeletableResource,
)
from sagemaker_studio_jupyter_scheduler.s3_uri import S3URI

import botocore
from jupyter_scheduler.exceptions import SchedulerError

# SM UI will provide "No script" if customer did select any.
SM_UI_EMPTY_FILE_STRING = "No script"

TEMP_LOCAL_LCC_SCRIPT_FILE_NAME = "lcc-init-script.sh"


class S3FileUploader:
    def __init__(
        self,
        deletable_resources: DeletableResourceContainer,
        s3_uri: str,
        file_upload_account_id: str,
        training_job_name: str,
        notebook_file_path: str,
        sm_init_script: str,
        sm_lcc_init_script_arn: str,
        root_dir: str,
        packaged_file_paths: List[str]
    ):
        self.deletable_resources = deletable_resources
        self.s3_uri = S3URI(s3_uri)
        self.file_upload_account_id = file_upload_account_id
        self.training_job_name = training_job_name
        self.notebook_file_path = notebook_file_path
        self.sm_init_script = sm_init_script
        self.sm_lcc_init_script_arn = (
            sm_lcc_init_script_arn
            if sm_lcc_init_script_arn != SM_UI_EMPTY_FILE_STRING
            else ""
        )
        self.packaged_file_paths = packaged_file_paths

        if not self.notebook_file_path:
            raise RuntimeError("Notebook file path must not be empty.")

        self.root_dir = root_dir

        self.tmp_dir = f"/tmp/{self.training_job_name}"
        self.sagemaker_client = get_sagemaker_client()
        self.s3_client = get_s3_client()

    @property
    def notebook_name(self):
        return os.path.basename(self.notebook_file_path)

    @property
    def sm_init_script_name(self):
        return os.path.basename(self.sm_init_script)

    @property
    def sm_lcc_init_script_name(self):
        return TEMP_LOCAL_LCC_SCRIPT_FILE_NAME

    async def _get_is_bucket_default_encrypted(self):
        try:
            await self.s3_client.get_bucket_encryption(bucket_name=self.s3_uri.bucket)
            return True
        except botocore.exceptions.ClientError:
            # GetBucketEncryption raises an error when the bucket is unencrypted.
            # If receiving another error such as permission error, assume the bucket is unencrypted.
            return False

    async def upload(self):
        # 1. upload notebook file to s3
        aws_account_id = self.file_upload_account_id if self.file_upload_account_id else await get_aws_account_id()
        explicitly_encrypt = not await self._get_is_bucket_default_encrypted()
        notebook_s3_key = os.path.join(
            self.s3_uri.key,
            self.training_job_name,
            "input",
            self.notebook_name,
        )
        await self.s3_client.upload_file(
            os.path.join(self.root_dir, self.notebook_file_path),
            self.s3_uri.bucket,
            notebook_s3_key,
            aws_account_id,
            encrypt=explicitly_encrypt,
        )
        self.deletable_resources.add_resource(
            DeletableResource(
                os.path.join(self.s3_uri.url, notebook_s3_key),
                lambda: self.s3_client.delete_object(
                    self.s3_uri.bucket, notebook_s3_key
                ),
            )
        )

        # 2. download LCC and upload to s3
        if self.sm_lcc_init_script_arn:
            lcc_script_s3_path = os.path.join(
                self.s3_uri.key,
                self.training_job_name,
                "input",
                self.sm_lcc_init_script_name,
            )
            os.makedirs(self.tmp_dir, exist_ok=False)
            describe_lcc_response = await self.sagemaker_client.describe_lcc(
                self.sm_lcc_init_script_arn
            )
            lcc_path = os.path.join(self.tmp_dir, self.sm_lcc_init_script_name)
            with open(lcc_path, "w") as lcc_file:
                lcc_file.write(
                    str(
                        b64decode(
                            describe_lcc_response["StudioLifecycleConfigContent"]
                        ),
                        "utf-8",
                    )
                )
            await self.s3_client.upload_file(
                lcc_path,
                self.s3_uri.bucket,
                lcc_script_s3_path,
                aws_account_id,
                encrypt=explicitly_encrypt,
            )
            self.deletable_resources.add_resource(
                DeletableResource(
                    os.path.join(self.s3_uri.url, lcc_script_s3_path),
                    lambda: self.s3_client.delete_object(
                        self.s3_uri.bucket, lcc_script_s3_path
                    ),
                )
            )
            shutil.rmtree(self.tmp_dir)

        # 3. upload to init script to s3
        if self.sm_init_script:
            init_script_s3_key = os.path.join(
                self.s3_uri.key,
                self.training_job_name,
                "input",
                self.sm_init_script_name,
            )
            await self.s3_client.upload_file(
                os.path.join(self.root_dir, self.sm_init_script),
                self.s3_uri.bucket,
                init_script_s3_key,
                aws_account_id,
                encrypt=explicitly_encrypt,
            )
            self.deletable_resources.add_resource(
                DeletableResource(
                    os.path.join(self.s3_uri.url, init_script_s3_key),
                    lambda: self.s3_client.delete_object(
                        self.s3_uri.bucket, init_script_s3_key
                    ),
                )
            )

        # 4. upload additional packaging files to S3
        if self.packaged_file_paths:
            for path in self.packaged_file_paths:
                source_dir = os.path.dirname(os.path.join(self.root_dir, self.notebook_file_path))
                file_path = os.path.join(source_dir, path)
                package_file_s3_key = os.path.join(
                    self.s3_uri.key,
                    self.training_job_name,
                    "input",
                    path,
                )
                await self.s3_client.upload_file(
                    file_path,
                    self.s3_uri.bucket,
                    package_file_s3_key,
                    aws_account_id,
                    encrypt=explicitly_encrypt,
                )
                self.deletable_resources.add_resource(
                    DeletableResource(
                        os.path.join(self.s3_uri.url, package_file_s3_key),
                        lambda: self.s3_client.delete_object(
                            self.s3_uri.bucket, package_file_s3_key
                        ),
                    )
                )
