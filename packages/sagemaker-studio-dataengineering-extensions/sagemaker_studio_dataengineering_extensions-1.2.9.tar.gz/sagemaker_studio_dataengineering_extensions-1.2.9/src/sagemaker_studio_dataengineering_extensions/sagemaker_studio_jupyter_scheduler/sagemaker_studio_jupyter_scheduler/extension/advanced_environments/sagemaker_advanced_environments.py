import asyncio
import botocore.exceptions

from sagemaker_studio_jupyter_scheduler.extension.advanced_environments.base_advanced_environments import (
    BaseAdvancedEnvironments,
)
from sagemaker_studio_jupyter_scheduler.util.aws_clients import (
    get_s3_client,
    get_iam_client,
)
from sagemaker_studio_jupyter_scheduler.logging import async_with_metrics
from sagemaker_studio_jupyter_scheduler.model.models import (
    AdvancedEnvironment,
    AdvancedEnvironmentResponse,
)
from sagemaker_studio_jupyter_scheduler.util.app_metadata import get_region_name
from sagemaker_studio_jupyter_scheduler.util.aws_config import get_aws_account_id
from sagemaker_studio_jupyter_scheduler.providers.standalone_image_metadata import (
    get_default_image_arn_standalone,
    get_default_image_kernel_name_standalone,
)

ERROR_CODE = "404"
BUCKET_NOT_EXISTED_MSG = "Not Found"

class SageMakerAdvancedEnvironments(BaseAdvancedEnvironments):
    SAGEMAKER_DEFAULT_S3_PREFIX = "sagemaker-automated-execution"
    SAGEMAKER_ROLE_PREFIX = "SagemakerJupyterScheduler"
    DEFAULT_IMAGE_NAME = "sagemaker-base-python-38"

    async def _create_s3_buckets(self, s3_bucket_name, s3_uri, logger):
        try:
            bucket_existed = await get_s3_client().head_bucket(s3_bucket_name)
            logger.info(f"S3 bucket already exists {s3_uri} - {bucket_existed}")
        except botocore.exceptions.ClientError as error:
            error_code = error.response["Error"]["Code"]
            error_message = error.response["Error"]["Message"]
            if error_code == ERROR_CODE and error_message == BUCKET_NOT_EXISTED_MSG:
                try:
                    response = await get_s3_client().create_bucket(
                        s3_bucket_name, get_region_name()
                    )
                    logger.info(f"S3 bucket created succesfully {s3_uri} - {response}")
                    # If the bucket already exists, the versioning & encryption calls is not needed
                    logger.info(f"Enable default server side encryption for {s3_uri}")
                    await get_s3_client().enable_server_side_encryption_with_s3_keys(
                        bucket_name=s3_bucket_name
                    )
                    logger.info(f"Enable versioning for {s3_uri}")
                    await get_s3_client().enable_versioning(bucket_name=s3_bucket_name)

                    logger.info(f"S3 bucket created succesfully {s3_uri} - {response}")
                except botocore.exceptions.ClientError as error:
                    # TODO: Discuss with PM on the desired fail safe mechanism, what if the bucket creation failed due to permission issue
                    # ideally we need the UI to prompt the user to create the bucket
                    # some issue with bucket creation
                    logger.error(
                        f"error when calling S3 bucket creation - {s3_bucket_name} - {error}"
                    )

    @async_with_metrics("GetAdvancedEnvironment")
    async def get_advanced_environments(self, logger):
        iam_client = get_iam_client()

        # empty values if api calls fail
        aws_account_id = None
        all_compatible_subnets = []
        security_group_ids = []
        role_arns = []  # TODO: sync with UI to modify this to a single value

        aws_account_id = await get_aws_account_id()
        logger.info(f"fetched aws_account_id: {aws_account_id}")

        list_role_arns_with_matching_prefix_response = (
            await iam_client.list_role_arns_with_matching_prefix_timeout_wrapper(
                self.SAGEMAKER_ROLE_PREFIX, logger
            )
        )
        # log list_role_arns_with_matching_prefix_response
        logger.info(
            f"list_role_arns_with_matching_prefix_response - {list_role_arns_with_matching_prefix_response}"
        )

        if isinstance(aws_account_id, Exception):
            raise aws_account_id

        if isinstance(list_role_arns_with_matching_prefix_response, Exception):
            logger.error(
                f"Unable to retrieve available SageMaker roles from IAM - {list_role_arns_with_matching_prefix_response}"
            )
        else:
            if list_role_arns_with_matching_prefix_response is not None:
                role_arns = list_role_arns_with_matching_prefix_response

        s3_bucket_name = (
            f"{self.SAGEMAKER_DEFAULT_S3_PREFIX}-{aws_account_id}-{get_region_name()}"
        )
        s3_uri = f"s3://{s3_bucket_name}/"

        [create_s3_bucket_response] = await asyncio.gather(
            self._create_s3_buckets(s3_bucket_name, s3_uri, logger),
            return_exceptions=True,
        )

        default_image_arn = get_default_image_arn_standalone(get_region_name())
        default_kernel = get_default_image_kernel_name_standalone()

        default_envs = [
            AdvancedEnvironment(
                name="s3_input",
                label="Input S3",
                description="S3 location to store all notebook related files",
                value=s3_uri,
            ),
            AdvancedEnvironment(
                name="s3_output",
                label="Output S3",
                description="S3 location to store all output artifacts",
                value=s3_uri,
            ),
            AdvancedEnvironment(
                name="role_arn",
                label="Execution Role ARN",
                description="IAM Role to be used by the Notebook Execution Engine",
                value=role_arns,
            ),
            AdvancedEnvironment(
                name="image",
                label="SageMaker Image",
                description="SageMaker Image to execute the notebook in",
                value=default_image_arn,
            ),
            AdvancedEnvironment(
                name="kernel",
                label="Python Kernel",
                description="Python Kernel to execute the notebook in",
                value=default_kernel,
            ),
            AdvancedEnvironment(
                name="vpc_security_group_ids",
                label="VPC Config Security Group IDs",
                description="List of Security GroupIDs for the notebook to be executed",
                value=security_group_ids,
            ),
            AdvancedEnvironment(
                name="vpc_subnets",
                label="VPC Config Subnets",
                description="List of Subnets for the notebook to be executed in",
                value=all_compatible_subnets,
            ),
            AdvancedEnvironment(
                name="app_network_access_type",
                label="App Network Access Type",
                description="Access type for the network",
                value="VpcOnly", # always enabled, this is used to enter vpc information in Advanced Option form
            ),
        ]
        logger.info(f"auto-detected env values - {default_envs}")
        return AdvancedEnvironmentResponse(auto_detected_config=default_envs)
