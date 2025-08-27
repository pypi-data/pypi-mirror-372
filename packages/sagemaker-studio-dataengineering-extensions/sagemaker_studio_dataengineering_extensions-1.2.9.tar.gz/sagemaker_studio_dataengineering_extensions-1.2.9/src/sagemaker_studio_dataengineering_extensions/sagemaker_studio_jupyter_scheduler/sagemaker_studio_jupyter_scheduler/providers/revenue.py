from sagemaker_studio_jupyter_scheduler.util.app_metadata import get_sagemaker_environment
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
)


def get_revenue_attribution_string():
    # This can be used to identify training jobs submitted by different libraries
    revenue_string = "sagemaker_headless_execution_vanilla"
    if get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_STUDIO:
        revenue_string = "sagemaker_headless_execution"
    elif get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB:
        revenue_string = "sagemaker_headless_execution_jupyterlab"
    elif get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_UNIFIED_STUDIO:
        revenue_string = "smus_jupyterlab_schedules"

    return revenue_string
