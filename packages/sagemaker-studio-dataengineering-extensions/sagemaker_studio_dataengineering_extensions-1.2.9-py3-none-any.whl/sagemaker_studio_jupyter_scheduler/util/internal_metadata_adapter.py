import json
import os
from sagemaker_studio_jupyter_scheduler.util.app_metadata import get_sagemaker_environment

from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
    JupyterLabEnvironmentDetector,
)

SAGEMAKER_INTERNAL_METADATA_FILE = "/opt/.sagemakerinternal/internal-metadata.json"

# TODO: We just need stage from this metadata file rest are handled in provider.intenal_metadata.py module.
# Find a better way to get stage in Studio


class InternalMetadataAdapter:
    def __init__(
        self,
    ):
        self.metadata = {}
        if (
            get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_STUDIO
            or get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB
            or get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_UNIFIED_STUDIO
        ):
            self.config_file = SAGEMAKER_INTERNAL_METADATA_FILE
            self._load_metadata()

    def get_stage(self) -> str:
        return self.metadata.get("Stage", "prod")

    def get_first_party_images(self):
        if self._is_config_file_mtime_changed():
            self._load_metadata()
        return self.metadata.get("FirstPartyImages", [])

    def get_custom_images(self):
        if self._is_config_file_mtime_changed():
            self._load_metadata()
        return self.metadata.get("CustomImages", [])

    def get_app_network_access_type(self):
        if self._is_config_file_mtime_changed():
            self._load_metadata()
        return self.metadata.get("AppNetworkAccessType", "UNKNOWN")

    def _load_metadata(self):
        self.modification_time = os.path.getmtime(self.config_file)
        self.metadata = {}
        with open(self.config_file, "r") as file:
            self.metadata = json.load(file)

    def _is_config_file_mtime_changed(self):
        return self.modification_time != os.path.getmtime(self.config_file)
