from dataclasses import dataclass
from enum import Enum
from typing import List, Union, Optional
from pydantic import BaseModel


class SageMakerSearchSortOrder(Enum):
    ASCENDING = "Ascending"
    DESCENDING = "Descending"

    def __str__(self):
        return self.value


class SageMakerTrainingJobStatus(Enum):
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    STOPPING = "Stopping"
    STOPPED = "Stopped"

    def __str__(self):
        return self.value


class EventBridgeRuleStatus(Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"

    def __str__(self):
        return self.value


class JobTag(str, Enum):
    IS_SCHEDULING_NOTEBOOK_JOB = "sagemaker:is-scheduling-notebook-job"
    IS_STUDIO_ARCHIVED = "sagemaker:is-studio-archived"
    JOB_DEFINITION_ID = "sagemaker:job-definition-id"
    NAME = "sagemaker:name"
    NOTEBOOK_NAME = "sagemaker:notebook-name"
    USER_PROFILE_NAME = "sagemaker:user-profile-name"
    NOTEBOOK_JOB_ORIGIN = "sagemaker:notebook-job-origin"
    AmazonDataZoneProject = "AmazonDataZoneProject"
    ONE_TIME_SCHEDULE = "sagemaker-studio:one-time"
    SMUS_USER_ID = "sagemaker-studio:user-id"

    def __str__(self):
        return self.value


class RuntimeEnvironmentParameterName(Enum):
    SM_IMAGE = "sm_image"
    SM_KERNEL = "sm_kernel"
    SM_INIT_SCRIPT = "sm_init_script"
    SM_LCC_INIT_SCRIPT_ARN = "sm_lcc_init_script_arn"
    S3_INPUT = "s3_input"
    S3_INPUT_ACCOUNT_ID = "s3_input_account_id"
    S3_OUTPUT = "s3_output"
    S3_OUTPUT_ACCOUNT_ID = "s3_output_account_id"
    ROLE_ARN = "role_arn"
    VPC_SECURITY_GROUP_IDS = "vpc_security_group_ids"
    VPC_SUBNETS = "vpc_subnets"
    SM_OUTPUT_KMS_KEY = "sm_output_kms_key"
    SM_VOLUME_KMS_KEY = "sm_volume_kms_key"
    MAX_RETRY_ATTEMPTS = "max_retry_attempts"
    MAX_RUN_TIME_IN_SECONDS = "max_run_time_in_seconds"
    SM_SKIP_EFS_SIMULATION = "sm_skip_efs_simulation"
    ENABLE_NETWORK_ISOLATION = "enable_network_isolation"

    def __str__(self):
        return self.value


class JobEnvironmentVariableName(Enum):
    SM_JOB_DEF_VERSION = "SM_JOB_DEF_VERSION"
    SM_FIRST_PARTY_IMAGEOWNER = "SM_FIRST_PARTY_IMAGEOWNER"
    SM_FIRST_PARTY_IMAGE_ARN = "SM_FIRST_PARTY_IMAGE_ARN"
    SM_KERNEL_NAME = "SM_KERNEL_NAME"
    SM_SKIP_EFS_SIMULATION = "SM_SKIP_EFS_SIMULATION"
    SM_EFS_MOUNT_PATH = "SM_EFS_MOUNT_PATH"
    SM_EFS_MOUNT_UID = "SM_EFS_MOUNT_UID"
    SM_EFS_MOUNT_GID = "SM_EFS_MOUNT_GID"
    SM_INPUT_NOTEBOOK_NAME = "SM_INPUT_NOTEBOOK_NAME"
    SM_OUTPUT_NOTEBOOK_NAME = "SM_OUTPUT_NOTEBOOK_NAME"
    AWS_DEFAULT_REGION = "AWS_DEFAULT_REGION"
    SM_ENV_NAME = "SM_ENV_NAME"
    SM_INIT_SCRIPT = "SM_INIT_SCRIPT"
    # This is for our ExecutionDriver(https://tiny.amazon.com/35pd6980)
    SM_LCC_INIT_SCRIPT = "SM_LCC_INIT_SCRIPT"
    # This is for our displaying get job details
    SM_LCC_INIT_SCRIPT_ARN = "SM_LCC_INIT_SCRIPT_ARN"
    SM_OUTPUT_FORMATS = "SM_OUTPUT_FORMATS"
    # we need to change the channe name to attribute revenue for vanilla project
    SM_EXECUTION_INPUT_PATH = "SM_EXECUTION_INPUT_PATH"
    SM_PACKAGE_INPUT_FOLDER = "SM_PACKAGE_INPUT_FOLDER"

    def __str__(self):
        return self.value


class AdvancedEnvironment(BaseModel):
    name: str
    label: str
    description: str
    value: Union[str, List]

    def __str__(self):
        return self.json()


AdvancedEnvironments = List[AdvancedEnvironment]


class AdvancedEnvironmentConfig(BaseModel):
    name: str
    value: AdvancedEnvironments

    def __str__(self):
        return self.json()


AdvancedEnvironmentConfigs = List[AdvancedEnvironmentConfig]


class AdvancedEnvironmentResponse(BaseModel):
    environment_configs: Optional[AdvancedEnvironmentConfigs] = None
    auto_detected_config: AdvancedEnvironments

    def __str__(self):
        return self.json()


class UserTypes(Enum):
    SHARED_SPACE_USER = "shared-space"
    PROFILE_USER = "user-profile"

    def __str__(self):
        return self.value


class UserDetails(BaseModel):
    user_id_key: UserTypes
    user_id_value: str

    def __str__(self):
        return self.json()


DEFAULT_UID = "0"
DEFAULT_GUID = "0"
DEFAULT_IMAGE_OWNER = "Customer Owned"
DEFAULT_MOUNT_PATH = "/root"


@dataclass
class ImageMetadata:
    ecr_uri: str
    image_arn: str
    image_display_name: str = None
    image_owner: str = DEFAULT_IMAGE_OWNER
    mount_path: str = DEFAULT_MOUNT_PATH
    uid: str = DEFAULT_UID
    gid: str = DEFAULT_GUID
