import os
import json
from typing import List, Dict
from jupyter_scheduler.models import RuntimeEnvironment
from jupyter_scheduler.environments import EnvironmentManager
from sagemaker_studio_jupyter_scheduler.util.app_metadata import get_region_name, get_sagemaker_environment
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironmentDetector,
)

default_instance_types = [
    "ml.m4.xlarge",
    "ml.m4.2xlarge",
    "ml.m4.4xlarge",
    "ml.m4.10xlarge",
    "ml.m4.16xlarge",
    "ml.g4dn.xlarge",
    "ml.g4dn.2xlarge",
    "ml.g4dn.4xlarge",
    "ml.g4dn.8xlarge",
    "ml.g4dn.12xlarge",
    "ml.g4dn.16xlarge",
    "ml.m5.large",
    "ml.m5.xlarge",
    "ml.m5.2xlarge",
    "ml.m5.4xlarge",
    "ml.m5.12xlarge",
    "ml.m5.24xlarge",
    "ml.c4.xlarge",
    "ml.c4.2xlarge",
    "ml.c4.4xlarge",
    "ml.c4.8xlarge",
    "ml.p2.xlarge",
    "ml.p2.8xlarge",
    "ml.p2.16xlarge",
    "ml.p3.2xlarge",
    "ml.p3.8xlarge",
    "ml.p3.16xlarge",
    "ml.p3dn.24xlarge",
    "ml.p4d.24xlarge",
    "ml.c5.xlarge",
    "ml.c5.2xlarge",
    "ml.c5.4xlarge",
    "ml.c5.9xlarge",
    "ml.c5.18xlarge",
    "ml.c5n.xlarge",
    "ml.c5n.2xlarge",
    "ml.c5n.4xlarge",
    "ml.c5n.9xlarge",
    "ml.c5n.18xlarge",
    "ml.g5.xlarge",
    "ml.g5.2xlarge",
    "ml.g5.4xlarge",
    "ml.g5.8xlarge",
    "ml.g5.16xlarge",
    "ml.g5.12xlarge",
    "ml.g5.24xlarge",
    "ml.g5.48xlarge",
]

# From Product Manger: “Choose the cheapest compute type by default: ml.m5.large”
# The problem with instances on Free tier is that those instances are more expensive than the ml.m5.large.
# So, I’m worried that we’ll end up charging the vast majority of the customers more with the default option by choosing
# a more expensive option.
# A Free Tier user can always choose to select the instances on their Free Tier.
# So, In summary, I think choosing the cheapest instance is a customer-first decision that will protect cusotmers from
# unintentional over-charges
# This instance is available in all regions
DEFAULT_COMPUTE_TYPE = "ml.m5.large"


class SagemakerEnvironmentManager(EnvironmentManager):
    """Provides a static list of environments, for demo purpose only"""

    def __init__(self):
        self.supported_compute_types = self._get_supported_instance_types()

    def _get_supported_instance_types(self):
        self.current_environment = get_sagemaker_environment()
        
        # We are dependent on the host_region_mapping.json file to calculate supported regions. 
        # If the training job API does not support a particular region, we cannot run notebook jobs in that region.
        PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
        region_mapping_file = os.path.join(PACKAGE_ROOT, "host_region_mapping.json")
        with open(region_mapping_file) as file:
            region_mapping = json.load(file)
            instance_details = region_mapping.get(get_region_name(), {})

            if instance_details:
                return instance_details
            else:
                return default_instance_types

    def list_environments(self) -> List[RuntimeEnvironment]:
        name = "sagemaker-default-env"
        path = os.path.join(os.environ["HOME"], name)

        return [
            RuntimeEnvironment(
                name=name,
                label=name,
                description=f"Virtual environment: {name}",
                file_extensions=["ipynb"],
                output_formats=[],
                compute_types=self.supported_compute_types,
                default_compute_type=DEFAULT_COMPUTE_TYPE,
                metadata={"path": path},
                # UTC Only because Event Bridge Rules only support UTC cron expressions.
                utc_only=True,
            )
        ]

    def manage_environments_command(self) -> str:
        return ""

    def output_formats_mapping(self) -> Dict[str, str]:
        return {"ipynb": "Notebook", "log": "Output Log"}
