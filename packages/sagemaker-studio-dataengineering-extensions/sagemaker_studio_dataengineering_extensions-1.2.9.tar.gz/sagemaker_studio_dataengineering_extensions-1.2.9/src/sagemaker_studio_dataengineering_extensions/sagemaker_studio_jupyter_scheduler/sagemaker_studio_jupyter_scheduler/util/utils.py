import re
import uuid
import datetime
from typing import Dict, Union
from datetime import datetime
from sagemaker_jupyter_server_extension.env_handlers import SageMakerEnvHandler


def sanitize_string(name: str, length: int):
    return re.sub(r"[^a-zA-Z0-9]", "", name)[:length]


def get_pipeline_expression_output_name(
    job_name: str, notebook_name: str, notebook_extension: str
) -> Dict:
    return {
        "Std:Join": {
            "On": "-",
            "Values": [
                f"{sanitize_string(job_name, 10)}",
                f"{sanitize_string(notebook_name,10)}",
                {"Get": "Execution.StartDateTime"},
                f"{notebook_extension}",
            ],
        }
    }


def get_eventbridge_output_name(
    job_name: str, notebook_name: str, notebook_extension: str
) -> str:
    values = [
        f"{sanitize_string(job_name, 10)}",
        f"{sanitize_string(notebook_name,10)}",
        "<aws.scheduler.scheduled-time>",
        f"{notebook_extension}",
    ]
    return "-".join(values)


def generate_job_identifier(name: str, notebook_name: str):
    # accepted pattern - https://github.com/jupyter-server/jupyter-scheduler/commit/ee1e2be9cb630ebb2d4dcd7febb2b98ba119a14b
    # JOB_DEFINITION_ID_REGEX = r"(?P<job_definition_id>\w+(?:-\w+)+)"
    # JOB_ID_REGEX = r"(?P<job_id>\w+(?:-\w+)+)"
    # \w: Matches any word character (alphanumeric & underscore).
    # Only matches low-ascii characters (no accented or non-roman characters).
    # Equivalent to [A-Za-z0-9_]

    # Pipeline name: 256 chars
    # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreatePipeline.html#sagemaker-CreatePipeline-request-PipelineName
    # Pattern: ^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,255}
    # Even though it supports 256, going to reduce it to 63

    # Event Bridge Rule: 64
    # https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_PutRule.html#eventbridge-PutRule-request-Name
    # [\.\-_A-Za-z0-9]+

    # Training name: 63 chars
    # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html#sagemaker-CreateTrainingJob-request-TrainingJobName
    # ^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}
    # Pipeline created Training jobs uses 20 chars from the field Name of the Training Step
    # We will split this between notebook name & job/job definition name
    # need to make sure these character also fits OSS requirement also.
    # pipelines-kbexktydy93v-<20 chars of Name>-aRjXdJ39fV
    # we will take 10 chars of job definition name and 10 chars of notebook name

    # Any customer given field will be sanitized to only include [A-Za-z0-9],
    # remove all other special chars
    # 19 chars - 2020-07-10-15-00-01
    # 8 chars - random id uuid4
    # 3 chars - delimiter (-)
    # max 33 chars - <job_name>-<notebook_name>
    # example - hourly-reportgenerator-ef21b9ad-2020-07-10-15-00-01
    sanitized_name = sanitize_string(name, 17)
    sanitized_notebook_name = sanitize_string(notebook_name, 16)
    random_id = str(uuid.uuid4())[:8]
    formatted_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    return (
        f"{sanitized_name}-{sanitized_notebook_name}-{random_id}-{formatted_timestamp}"
    )

def generate_dynamic_job_name_for_eventbridge(name: str, notebook_name: str):
    # accepted pattern - https://github.com/jupyter-server/jupyter-scheduler/commit/ee1e2be9cb630ebb2d4dcd7febb2b98ba119a14b
    # JOB_DEFINITION_ID_REGEX = r"(?P<job_definition_id>\w+(?:-\w+)+)"
    # JOB_ID_REGEX = r"(?P<job_id>\w+(?:-\w+)+)"
    # \w: Matches any word character (alphanumeric & underscore).
    # Only matches low-ascii characters (no accented or non-roman characters).
    # Equivalent to [A-Za-z0-9_]

    # Pipeline name: 256 chars
    # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreatePipeline.html#sagemaker-CreatePipeline-request-PipelineName
    # Pattern: ^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,255}
    # Even though it supports 256, going to reduce it to 63

    # Event Bridge Rule: 64
    # https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_PutRule.html#eventbridge-PutRule-request-Name
    # [\.\-_A-Za-z0-9]+

    # Training name: 63 chars
    # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html#sagemaker-CreateTrainingJob-request-TrainingJobName
    # ^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}
    # Pipeline created Training jobs uses 20 chars from the field Name of the Training Step
    # We will split this between notebook name & job/job definition name
    # need to make sure these character also fits OSS requirement also.
    # pipelines-kbexktydy93v-<20 chars of Name>-aRjXdJ39fV
    # we will take 10 chars of job definition name and 10 chars of notebook name

    # Any customer given field will be sanitized to only include [A-Za-z0-9],
    # remove all other special chars
    # 36 chars - c2687052-d4e5-4ed3-b40f-16a80375d767
    # 2 chars - delimiter (-)
    # max 29 chars - <job_name>-<notebook_name>
    # example - hourly-reportgenerator-ef21b9ad-2020-07-10-15-00-01
    sanitized_name = sanitize_string(name, 12)
    sanitized_notebook_name = sanitize_string(notebook_name, 11)
    execution_id = "<aws.scheduler.execution-id>"

    return (
        f"{sanitized_name}-{sanitized_notebook_name}-{execution_id}"
    )

def safe_env_get(env_config: dict, key: str, default: str) -> str:
    """Safely get value from env_config, treating empty strings as missing values"""
    value = env_config.get(key, default)
    return default if not value else value


def load_env():
    """Load environment configuration from SageMaker Env Handler"""
    return SageMakerEnvHandler.read_metadata()


def should_use_jupyter_scheduler(input_or_job_id: Union[str, object]) -> bool:
    """
    Helper function to determine if we should use jupyter scheduler implementation
    
    Parameters:
    - input_or_job_id: Either a job_id string or CreateJob input object
    
    Returns:
    - True if should use jupyter scheduler, False otherwise
    """
    if isinstance(input_or_job_id, str):
        # For job_id string, check if it's a valid UUID
        try:
            from uuid import UUID
            UUID(input_or_job_id)
            return True
        except (ValueError, ImportError):
            return False
    elif hasattr(input_or_job_id, 'runtime_environment_name'):
        # For CreateJob input, check runtime_environment_name
        return input_or_job_id.runtime_environment_name == 'conda'
    else:
        return False
