LOG_FILE_NAME = "sagemaker-scheduler.api.log"
LOGGER_NAME = "sagemaker-scheduler-api-operations"

STUDIO_LOG_FILE_PATH = "/var/log/studio/scheduled_notebooks"
STUDIO_LOG_FILE_NAME = "sagemaker_scheduling_extension_api.log"

UNIFIED_STUDIO_LOG_FILE_PATH = "/var/log/apps"


# Regex pattern for stack trace filters
email_regex = "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"
# credit to https://uibakery.io/regex-library/phone-number-python
phone_number_regex = (
    "\+?\d{1,4}?[-.\s]?\(?(\d{1,3}?)\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
)

password_regex = "(?i)password\s*[:=]\s*\S+"
api_key_regex = "(?i)apikey\s*[:= ]\s*\S+"
aws_secretkey_regex = "(?i)aws_secret_access_key\s*[:=]\s*\S+"

IAM_TIMEOUT = 3

DEFAULT_JOB_DEFINITION_RETRY_VALUE = 1

USE_DUALSTACK_ENDPOINT = False

# DataZone Asset constants
ASSET_COMMON_DETAILS_FORM_NAME = 'AssetCommonDetailsForm'
ASSET_COMMON_DETAILS_FORM_TYPE = 'amazon.datazone.AssetCommonDetailsFormType'
SAGEMAKER_SCHEDULE_FORM_TYPE_NAME = 'SageMakerUnifiedStudioScheduleFormType'
SAGEMAKER_SCHEDULE_FORM_NAME = 'SageMakerUnifiedStudioScheduleForm'
SAGEMAKER_SCHEDULE_ASSET_TYPE = 'SageMakerUnifiedStudioScheduleAssetType'
EVENTBRIDGE = 'EventBridge'

# This is a public contract - https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks-run-and-manage-metadata.html#notebooks-run-and-manage-metadata-app
SAGEMAKER_RESOURCE_METADATA_FILE = "/opt/ml/metadata/resource-metadata.json"
