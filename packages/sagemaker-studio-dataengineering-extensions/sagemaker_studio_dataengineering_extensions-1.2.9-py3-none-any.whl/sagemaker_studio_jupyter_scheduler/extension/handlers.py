from sagemaker_studio_jupyter_scheduler.logging import init_api_operation_logger
from sagemaker_studio_jupyter_scheduler.extension.advanced_environments.sagemaker_unified_studio_advanced_environment import SageMakerUnifiedStudioAdvancedEnvironments
from jupyter_scheduler.exceptions import SchedulerError
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
import os
import tornado
import json
import time
import urllib
import botocore
import boto3
import re
import asyncio
import aiohttp
from async_timeout import timeout

from sagemaker_studio_jupyter_scheduler.extension.advanced_environments.sagemaker_advanced_environments import (
    SageMakerAdvancedEnvironments,
)
from sagemaker_studio_jupyter_scheduler.extension.advanced_environments.sagemaker_studio_advanced_environment import (
    SageMakerStudioAdvancedEnvironments,
)
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironmentDetector,
    JupyterLabEnvironment,
)
from sagemaker_studio_jupyter_scheduler.util.app_metadata import (
    get_region_name,
    get_sagemaker_environment,
)

from sagemaker_studio_jupyter_scheduler.extension.ecr_account_mapping import (
    build_sagemaker_distribution_uri,
)


from sagemaker_studio_jupyter_scheduler.providers.jupyterlab_image_metadata import (
    get_image_metadata_jupyterlab
)

from sagemaker_studio_jupyter_scheduler.util.error_util import NoCredentialsSchedulerError, BotoClientSchedulerError, BotoEndpointConnectionSchedulerError

WEBAPP_SETTINGS_URL = "https://studiolab.sagemaker.aws/settings.json"
MAX_WAIT_TIME_FOR_API_CALL_SECS = 8.0


class AdvancedEnvironmentsHandler(ExtensionHandlerMixin, JupyterHandler):
    @tornado.web.authenticated
    async def get(self):
        try:
            async with timeout(MAX_WAIT_TIME_FOR_API_CALL_SECS):
                if (
                    get_sagemaker_environment()
                    == JupyterLabEnvironment.SAGEMAKER_STUDIO
                    or get_sagemaker_environment()
                    == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB
                ):
                    self.log.info(f"[AdvancedEnviornmentsHandler] SageMaker Studio environment detected")
                    envs = await SageMakerStudioAdvancedEnvironments().get_advanced_environments(
                        self.log
                    )
                elif (get_sagemaker_environment()
                    == JupyterLabEnvironment.SAGEMAKER_UNIFIED_STUDIO):
                    envs = await SageMakerUnifiedStudioAdvancedEnvironments().get_advanced_environments(
                        self.log
                    )
                else:
                    self.log.info(f"[AdvancedEnviornmentsHandler] Vanilla JupyterLab environment detected")
                    envs = (
                        await SageMakerAdvancedEnvironments().get_advanced_environments(
                            self.log
                        )
                    )
                self.finish(envs.json())
        except BotoClientSchedulerError as error:
            self.log.exception(f"[AdvancedEnvironmentsHandler] BotoClientSchedulerError error detected: {error}")
            self.set_status(error.status_code)
            self.finish({"error_code": error.error_code, "message": str(error.error_message)})
        except NoCredentialsSchedulerError as error:
            self.log.exception(f"[AdvancedEnvironmentsHandler] NoCredentialsSchedulerError error detected: {error}")
            self.set_status(error.status_code)
            self.finish({"error_code": error.error_code, "message": str(error.error_message)})
        except BotoEndpointConnectionSchedulerError as error:
            self.log.exception(f"[AdvancedEnvironmentsHandler] EndpointConnectionError error detected: {error}")
            self.set_status(error.status_code)
            self.finish({"error_code": error.error_code, "message": str(error.error_message)})
        except SchedulerError as error:
            self.set_status(403)
            self.finish(
                json.dumps({"error_code": "NoCredentials", "message": str(error)})
            )
        except Exception as error:
            self.log.exception(f"[AdvancedEnviornmentsHandler] Generic exception detected: {error}")
            self.set_status(500)
            self.finish(json.dumps({"error": str(error)}))


class ValidateVolumePathHandler(ExtensionHandlerMixin, JupyterHandler):
    @tornado.web.authenticated
    async def post(self):
        try:
            body = self.get_json_body()
            if "file_path" in body:
                file_exist = os.path.exists(body["file_path"])
                self.set_status(200)
                self.finish(json.dumps({"file_path_exist": file_exist}))
            else:
                self.set_status(400)
                self.finish(json.dumps({"error": "invalid input"}))
        except Exception as e:
            self.log.exception(f"[ValidateVolumePathHandler] Encountered error when validating file path: {e}")
            self.set_status(500)
            self.finish(json.dumps({"error": e.msg}))


class SageMakerImagesListHandler(ExtensionHandlerMixin, JupyterHandler):
    @tornado.web.authenticated
    async def get(self):
        if get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_UNIFIED_STUDIO:
            image_metadata = await get_image_metadata_jupyterlab()
            
            # Get version info and append to display name
            version_info = self._get_image_version_display()
            display_name = image_metadata.image_display_name
            if version_info:
                display_name = f"{display_name} {version_info}"
            
            # Extract current version to filter out from other lists
            current_version = None
            if version_info:
                # Extract version number from version_info like "(2.2)" or "(3.1 CPU)"
                version_match = re.search(r'\((\d+\.\d+)', version_info)
                if version_match:
                    current_version = version_match.group(1)
            
            # Start with the current image as the first (default) option
            images_list = [
                {
                    "image_arn": image_metadata.image_arn,
                    "image_display_name": display_name,
                }
            ]
            
            # Add available public images from ECR (2.6+ and 3.1+)
            try:
                public_images = await self._get_available_public_images(exclude_version=current_version)
                images_list.extend(public_images)
            except Exception as e:
                self.log.error(f"Failed to retrieve public images: {e}")
            
            # Add available private images (2.2 and 3.0 CPU)
            try:
                private_images = await self._get_available_private_images(exclude_version=current_version)
                images_list.extend(private_images)
            except Exception as e:
                self.log.error(f"Failed to retrieve private images: {e}")
            
            # Sort all non-current images by version number (descending, latest first)
            # Keep the current version as first, sort the rest
            if len(images_list) > 1:
                current_image = images_list[0]
                other_images = images_list[1:]
                
                def version_sort_key(image):
                    # Extract version number for sorting
                    version_match = re.search(r'\((\d+\.\d+)', image['image_display_name'])
                    if version_match:
                        return float(version_match.group(1))
                    return 0
                
                other_images.sort(key=version_sort_key, reverse=True)
                images_list = [current_image] + other_images
            
            self.log.info(f"Total images in final list: {len(images_list)}")
            
            self.finish(json.dumps(images_list))
        elif get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB:
            image_metadata = await get_image_metadata_jupyterlab()
            self.finish(json.dumps(
                [
                    {
                        "image_arn": image_metadata.image_arn,
                        "image_display_name": image_metadata.image_display_name,
                    }
                ])
            )
        else:
            # Image list handler is not implemented for other app types
            self.finish(json.dumps([]))

    def _get_image_version_display(self) -> str:
        """
        Extract image version information based on Python version and environment variables.
        
        Returns:
            Formatted version string to append to image display name, e.g., "(2.2)", "(3.0)", "(3.1 CPU)"
        """
        try:
            # check IMAGE_VERSION environment variable
            image_version = os.environ.get("IMAGE_VERSION", "")
            if image_version:
                # Parse version like "3.1.1-cpu" to "(3.1 CPU)"
                parts = image_version.split("-")
                if len(parts) >= 2:
                    version_number = parts[0]  # e.g., "3.1.1"
                    processor_type = parts[1].upper()  # e.g., "cpu" -> "CPU"
                    
                    # Extract major.minor version (e.g., "3.1.1" -> "3.1")
                    version_parts = version_number.split(".")
                    if len(version_parts) >= 2:
                        major_minor = f"{version_parts[0]}.{version_parts[1]}"
                        return f"({major_minor} {processor_type})"
                    else:
                        return f"({version_number} {processor_type})"
                else:
                    # Just version number without processor type
                    version_parts = image_version.split(".")
                    if len(version_parts) >= 2:
                        major_minor = f"{version_parts[0]}.{version_parts[1]}"
                        return f"({major_minor})"
                    else:
                        return f"({image_version})"
            else:
                import sys
                python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
                
                # For 2.2 image the python version is 3.11
                if python_version == "3.11":
                    return "(2.2)"
                # For 3.0 version image, the python version is 3.12
                elif python_version == "3.12":
                    return "(3.0)"
                else:
                    return ""
                            
        except Exception as e:
            # Log error but don't fail the entire request
            self.log.warning(f"Error determining image version: {e}")
        
        return ""

    async def _fetch_ecr_images(self) -> list:
        """Async function to fetch ECR images using Docker Registry API"""
        try:
            # Step 1: Get the token from ECR Public
            token_url = "https://public.ecr.aws/token/"
            tags_url = "https://public.ecr.aws/v2/sagemaker/sagemaker-distribution/tags/list"
            
            async with aiohttp.ClientSession() as session:
                # Get authentication token
                self.log.info("Fetching ECR token...")
                async with session.get(token_url, ssl=True) as token_response:
                    if token_response.status == 200:
                        token_data = await token_response.json()
                        token = token_data.get('token')
                        if not token:
                            self.log.error("No token found in response")
                            raise Exception("No token found in ECR response")
                    else:
                        self.log.error(f"Failed to get token: {token_response.status}")
                        raise Exception(f"Failed to get token: {token_response.status}")
                
                # Get tags using the token
                self.log.info("Fetching image tags...")
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(tags_url, headers=headers, ssl=True) as tags_response:
                    if tags_response.status == 200:
                        # Read response as text first, then parse as JSON
                        response_text = await tags_response.text()
                        # self.log.info(f"Response content type: {tags_response.headers.get('content-type', '')}")
                        
                        try:
                            # Parse the text as JSON
                            tags_data = json.loads(response_text)
                            # self.log.info(f"ECR Tags Response: {tags_data}")
                        except json.JSONDecodeError as e:
                            self.log.error(f"Failed to parse JSON response: {e}")
                            self.log.error(f"Response text: {response_text}")
                            raise Exception(f"Failed to parse JSON response: {e}")
                    else:
                        # Log the error response content
                        response_text = await tags_response.text()
                        self.log.error(f"Failed to get tags: {tags_response.status}")
                        self.log.error(f"Error response: {response_text}")
                        raise Exception(f"Failed to get tags: {tags_response.status}")
            
            # Process the tags
            images = []
            seen_versions = set()  # To avoid duplicates
            
            for tag in tags_data.get('tags', []):
                # Skip 'latest' and other non-version tags
                if not re.match(r'^\d+\.\d+', tag):
                    continue
                
                # Parse version and processor type from tag (e.g., "2.6-gpu", "3.0-cpu")
                version_match = re.match(r'^(\d+\.\d+)(?:-(\w+))?', tag)
                if version_match:
                    version = version_match.group(1)  # e.g., "2.6"
                    processor = version_match.group(2)  # e.g., "gpu" or "cpu"
                    
                    
                    # Only show versions that explicitly have CPU processor type
                    if processor != 'cpu':
                        # self.log.info(f"Skipping version {tag} (not cpu)")
                        continue
                    
                    # Filter versions: only return 2.6+ for 2.x and 3.1+ for 3.x
                    version_float = float(version)
                    if version.startswith('2.') and version_float < 2.6:
                        # self.log.info(f"Skipping version {version} (below 2.6)")
                        continue
                    elif version.startswith('3.') and version_float < 3.1:
                        # self.log.info(f"Skipping version {version} (below 3.1)")
                        continue

                    # Only allow 2.x and 3.x versions, filter out all others
                    if not (version.startswith('2.') or version.startswith('3.')):
                        # self.log.info(f"Skipping version {version} (not 2.x or 3.x)")
                        continue
                    
                    # Create a unique key to avoid duplicates
                    version_key = f"{version}-{processor}" if processor else version
                    if version_key in seen_versions:
                        continue
                    seen_versions.add(version_key)
                    
                    # Format the full ECR URI using region-specific account mapping
                    # Default to 'prod' stage and 'us-east-1' region if not available
                    region = get_region_name() or 'us-east-1'
                    stage = os.environ.get('STAGE', 'prod')  # Get from environment variable with 'prod' as default
                    image_uri = build_sagemaker_distribution_uri(region, stage, version, processor)
                    
                    # Create display name with version info
                    if processor:
                        display_name = f"SageMaker Distribution ({version} {processor.upper()})"
                    else:
                        display_name = f"SageMaker Distribution ({version})"
                    
                    images.append({
                        "image_arn": image_uri,
                        "image_display_name": display_name,
                    })
            
            # Sort by version number (descending, latest first)
            def version_sort_key(image):
                # Extract version number for sorting
                version_match = re.search(r'\((\d+\.\d+)', image['image_display_name'])
                if version_match:
                    return float(version_match.group(1))
                return 0
            
            images.sort(key=version_sort_key, reverse=True)
            
            self.log.info(f"Final images count: {len(images)}")
            
            # If no images found from ECR, return empty
            if not images:
                self.log.info("No images found from ECR, returning empty")
                return []
            
            return images
            
        except Exception as e:
            self.log.error(f"Error in _fetch_ecr_images: {e}")
            # Return mock data as fallback
            return []


    async def _get_available_public_images(self, exclude_version: str = None) -> list:
        """
        Retrieve available SageMaker Distribution images from AWS ECR Public Gallery.
        
        Args:
            exclude_version: Version to exclude from the list (e.g., "2.2", "3.1")
        
        Returns:
            List of image dictionaries with image_arn and image_display_name
        """
        try:
            # Call the async ECR fetch function directly
            all_images = await self._fetch_ecr_images()
            
            # Filter out the current version if specified
            if exclude_version:
                filtered_images = []
                for image in all_images:
                    # Extract version from display name
                    version_match = re.search(r'\((\d+\.\d+)', image['image_display_name'])
                    if version_match and version_match.group(1) == exclude_version:
                        self.log.info(f"Excluding current version {exclude_version} from public images")
                        continue
                    filtered_images.append(image)
                return filtered_images
            
            return all_images
        except Exception as e:
            self.log.error(f"Error retrieving public images from ECR: {e}")
            return []

    async def _get_available_private_images(self, exclude_version: str = None) -> list:
        """
        Retrieve available private SageMaker Distribution images (versions 2.2 and 3.0 CPU).
        These are embargoed versions that are not available publicly but should be included.
        
        Args:
            exclude_version: Version to exclude from the list (e.g., "2.2", "3.0")
        
        Returns:
            List of image dictionaries with image_arn and image_display_name
        """
        try:
            images = []
            
            # Define private versions to include
            private_versions = [
                {"version": "2.2", "processor": "cpu"},
                {"version": "3.0", "processor": "cpu"}
            ]
            
            # Get region and stage for URI construction
            region = get_region_name() or 'us-east-1'
            stage = os.environ.get('STAGE', 'prod')
            
            for version_info in private_versions:
                version = version_info["version"]
                processor = version_info["processor"]
                
                # Skip if this is the current version
                if exclude_version and version == exclude_version:
                    self.log.info(f"Excluding current version {exclude_version} from private images")
                    continue
                
                # Build the URI for private version
                image_uri = build_sagemaker_distribution_uri(region, stage, version, processor)
                
                # Create display name
                display_name = f"SageMaker Distribution ({version} {processor.upper()})"
                
                images.append({
                    "image_arn": image_uri,
                    "image_display_name": display_name,
                })
                
                self.log.info(f"Added private image: {display_name}")
            
            return images
            
        except Exception as e:
            self.log.error(f"Error creating private images: {e}")
            return []

