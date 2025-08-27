import asyncio
import botocore.exceptions
import os

from typing import List
from aws_embedded_metrics.logger.metrics_context import MetricsContext

from sagemaker_studio_jupyter_scheduler.util.utils import safe_env_get, load_env
from sagemaker_studio_jupyter_scheduler.extension.advanced_environments.base_advanced_environments import (
    BaseAdvancedEnvironments,
)
from sagemaker_studio_jupyter_scheduler.util.app_metadata import (
    get_region_name,
    get_domain_id,
    get_user_profile_name,
    get_shared_space_name,
    get_sagemaker_environment,

)
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
)
from sagemaker_studio_jupyter_scheduler.util.aws_config import get_aws_account_id, get_execution_role_arn
from sagemaker_studio_jupyter_scheduler.util.aws_clients import (
    get_ec2_client,
    get_sagemaker_client,
    get_s3_client,
)
from sagemaker_studio_jupyter_scheduler.logging import async_with_metrics
from sagemaker_studio_jupyter_scheduler.model.models import (
    AdvancedEnvironment,
    AdvancedEnvironmentResponse,
)

ERROR_CODE = "404"
BUCKET_NOT_EXISTED_MSG = "Not Found"


class SageMakerUnifiedStudioAdvancedEnvironments(BaseAdvancedEnvironments):
    @async_with_metrics("GetAdvancedEnvironment")
    async def get_advanced_environments(self, logger, metrics: MetricsContext):
        """Generate advanced environment configurations dynamically from metadata"""
        
        # Load environment metadata
        env_config = load_env()
        
        # Generate S3 paths from metadata
        s3_input_value = await self._generate_s3_input_path(env_config)
        s3_output_value = await self._generate_s3_output_path(env_config)
        
        # Get role ARN from caller identity
        role_arn_value = await self._get_role_arn(env_config)
        
        # Get VPC configuration from metadata
        vpc_security_group_ids = safe_env_get(env_config, "security_group", "").split(",") if safe_env_get(env_config, "security_group", "") else [""]
        vpc_subnets = safe_env_get(env_config, "subnets", "").split(",") if safe_env_get(env_config, "subnets", "") else [""]
        
        # Clean up empty strings from lists
        vpc_security_group_ids = [sg.strip() for sg in vpc_security_group_ids if sg.strip()]
        vpc_subnets = [subnet.strip() for subnet in vpc_subnets if subnet.strip()]


        network_access_type = ['VpcOnly'] if vpc_subnets and len(vpc_subnets) != 0 and vpc_security_group_ids and len(vpc_security_group_ids) != 0 else ['PublicInternetOnly']
        default_envs = [
            AdvancedEnvironment(
                name="s3_input",
                label="Input S3",
                description="S3 location to store all notebook related files",
                value=s3_input_value,
            ),
            AdvancedEnvironment(
                name="s3_output",
                label="Output S3",
                description="S3 location to store all output artifacts",
                value=s3_output_value,
            ),
            AdvancedEnvironment(
                name="role_arn",
                label="Execution Role ARN",
                description="IAM Role to be used by the Notebook Execution Engine",
                value=[role_arn_value] if role_arn_value else [""],
            ),
            AdvancedEnvironment(
                name="image",
                label="SageMaker Image",
                description="SageMaker Image to execute the notebook in",
                value=f"542918446943.dkr.ecr.us-west-2.amazonaws.com/sagemaker-distribution-embargoed-prod:2.2.5-reinvent2024-cpu",  # list
            ),
            AdvancedEnvironment(
                name="kernel",
                label="Python Kernel",
                description="Python Kernel to execute the notebook in",
                value=f"python3",
            ),
            AdvancedEnvironment(
                name="lcc_arn",
                label="LCC ARN",
                description="LCC ARN to be executed before execution",
                value=[''],
            ),
            AdvancedEnvironment(
                name="vpc_security_group_ids",
                label="VPC Config Security Group IDs",
                description="List of Security GroupIDs for the notebook to be executed",
                value=vpc_security_group_ids,
            ),
            AdvancedEnvironment(
                name="vpc_subnets",
                label="VPC Config Subnets",
                description="List of Subnets for the notebook to be executed in",
                value=vpc_subnets,
            ),
            AdvancedEnvironment(
                name="app_network_access_type",
                label="App Network Access Type",
                description="Access type for the network",
                # value=['PublicInternetOnly'],
                value=network_access_type,
            ),
        ]
        logger.info(f"auto-detected env values - {default_envs}")
        return AdvancedEnvironmentResponse(auto_detected_config=default_envs)

    async def _generate_s3_input_path(self, env_config: dict) -> str:
        """Generate S3 input path from ProjectS3Path metadata"""
        project_s3_path = safe_env_get(env_config, "project_s3_path", "")
        if not project_s3_path:
            return ""
        
        # Change "dev" to "sys" in the path and add the suffix
        s3_input_path = project_s3_path.replace("/dev/", "/sys/")
        if not s3_input_path.endswith("/"):
            s3_input_path += "/"
        s3_input_path += "code/dev/datazone-" + safe_env_get(env_config, "project_id", "") + "-dev/main/"
        
        return s3_input_path

    async def _generate_s3_output_path(self, env_config: dict) -> str:
        """Generate S3 output path from ProjectS3Path metadata"""
        project_s3_path = safe_env_get(env_config, "project_s3_path", "")
        user_id = safe_env_get(env_config, "user_id", "")
        
        if not project_s3_path:
            return ""
        
        # Change "dev" to "sys" and add user-specific path
        s3_output_path = project_s3_path.replace("/dev/", "/sys/")
        if not s3_output_path.endswith("/"):
            s3_output_path += "/"

        if not user_id:
            s3_output_path += f"user/{user_id}"
        
        return s3_output_path

    async def _get_role_arn(self, env_config: dict) -> str:
        """Get role ARN from caller identity or construct from metadata"""
        try:
            project_id = safe_env_get(env_config, "project_id", "")
            env_id = safe_env_get(env_config, "environment_id", "")
            
            if project_id and env_id:
                return await get_execution_role_arn(project_id, env_id)
            
            return ""
        except Exception as e:
            # Log the error but don't fail - return empty string
            return ""
