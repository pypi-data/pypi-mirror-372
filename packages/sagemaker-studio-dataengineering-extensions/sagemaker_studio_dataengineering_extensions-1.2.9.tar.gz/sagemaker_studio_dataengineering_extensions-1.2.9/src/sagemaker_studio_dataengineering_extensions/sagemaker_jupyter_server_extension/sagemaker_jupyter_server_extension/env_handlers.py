import json
import logging
import os

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin

logger = logging.getLogger(__name__)

class SageMakerEnvHandler(ExtensionHandlerMixin, APIHandler):
    @tornado.web.authenticated
    def get(self):
        try:
            response = self.read_metadata()

            self.finish(json.dumps(response))

        except Exception as e:
            logger.exception("An error occurred:", e)

    @classmethod
    def read_metadata(cls):
        home = os.environ.get('HOME', '')
        # Initialize default response structure with empty values
        response = {
            "project_id": "",
            "domain_id": "",
            "user_id": "",
            "environment_id": "",
            "project_s3_path": "",
            "subnets": "",
            "security_group": "",
            "dz_endpoint": "",
            "dz_stage": "",
            "dz_region": "",
            "aws_region": "",
            "sm_domain_id": "",
            "sm_space_name": "",
            "sm_user_profile_name": "",
            "sm_project_path": "",
            "enabled_features": []
        }

        # Get AWS region first as it's used as fallback for dz_region
        aws_region = os.getenv('AWS_REGION', "")
        response["aws_region"] = aws_region
        response["dz_region"] = aws_region  # Default fallback

        # Try to read metadata from file first (preferred source)
        data = cls.read_metadata_file()

        # Retrieve project path
        project_path = None
        # Attempt to retrieve the project path from the metadata
        if data and 'AdditionalMetadata' in data and 'ProjectSharedDirectory' in data['AdditionalMetadata']:
            project_path = data['AdditionalMetadata']['ProjectSharedDirectory']

        # If project_path is still None, try to retrieve the project path from the storage metadata file
        if not project_path:
            storage_data = cls.read_storage_metadata_file()
            project_path = storage_data["smusProjectDirectory"] if storage_data and 'smusProjectDirectory' in storage_data else None

        # Create a relative path by removing the home directory prefix, if project_path exists
        # If project_path is None, relative_path will also be None
        relative_path = project_path.replace(f"{home}/", "") if project_path else None

        response["sm_project_path"] = relative_path

        if data and data.get('AdditionalMetadata'):
            additional_metadata = data['AdditionalMetadata']
            response.update({
                "project_id": additional_metadata.get('DataZoneProjectId', ""),
                "domain_id": additional_metadata.get('DataZoneDomainId', ""),
                "user_id": additional_metadata.get('DataZoneUserId', ""),
                "environment_id": additional_metadata.get('DataZoneEnvironmentId', ""),
                "project_s3_path": additional_metadata.get('ProjectS3Path', ""),
                "subnets": additional_metadata.get('PrivateSubnets', ""),
                "security_group": additional_metadata.get('SecurityGroup', ""),
                "dz_endpoint": additional_metadata.get('DataZoneEndpoint', ""),
                "dz_stage": additional_metadata.get('DataZoneStage', ""),
                "sm_domain_id": data.get('DomainId', ""),
                "sm_space_name": data.get('SpaceName', ""),
                "sm_user_profile_name": additional_metadata.get('DataZoneUserId', "")
            })
            
            # Override dz_region if available in metadata
            if 'DataZoneDomainRegion' in additional_metadata:
                response["dz_region"] = additional_metadata['DataZoneDomainRegion']
        else:
            # Fallback to environment variables if metadata file is not available
            response.update({
                "project_id": os.environ.get("DataZoneProjectId", ""),
                "domain_id": os.environ.get("DataZoneDomainId", ""),
                "user_id": os.environ.get("DataZoneUserId", ""),
                "environment_id": os.environ.get("DataZoneEnvironmentId", ""),
                "dz_endpoint": os.environ.get("DataZoneEndpoint", ""),
                "dz_stage": os.environ.get("DataZoneStage", "")
            })

        # Load enabled features if available
        enabled_features_path = os.path.expanduser('~/.aws/enabled_features/enabled_features.json')
        if os.path.isfile(enabled_features_path):
            try:
                with open(enabled_features_path) as features_file:
                    features_data = json.load(features_file)
                    response['enabled_features'] = features_data.get('enabled_features', [])
            except Exception as e:
                logger.exception("An error occurred loading enabled_features:", e)
                response['enabled_features'] = []

        return response

    @classmethod
    def read_metadata_file(cls):
        try:
            with open('/opt/ml/metadata/resource-metadata.json') as json_file:
                data = json.load(json_file)
            return data
        except Exception as e:
            logger.exception("An error occurred reading metadata file:", e)
            return None

    @classmethod
    def read_storage_metadata_file(cls):
        try:
            with open('/home/sagemaker-user/.config/smus-storage-metadata.json') as json_file:
                data = json.load(json_file)
            return data
        except Exception as e:
            logger.exception("An error occurred reading metadata file:", e)
            return None


