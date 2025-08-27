import os
import asyncio
import json
from datetime import datetime, timezone
from sagemaker_studio_jupyter_scheduler.util.constants import (
    DEFAULT_JOB_DEFINITION_RETRY_VALUE,
    ASSET_COMMON_DETAILS_FORM_NAME,
    ASSET_COMMON_DETAILS_FORM_TYPE,
    SAGEMAKER_SCHEDULE_FORM_NAME,
    SAGEMAKER_SCHEDULE_ASSET_TYPE,
    EVENTBRIDGE,
    SAGEMAKER_SCHEDULE_FORM_TYPE_NAME,
)
from aws_embedded_metrics.logger.metrics_context import MetricsContext

import botocore
from typing import List, Dict, Type, Optional, Union, Tuple


from jupyter_scheduler.environments import EnvironmentManager
from jupyter_scheduler.models import (
    DescribeJob,
    ListJobDefinitionsQuery,
    DescribeJobDefinition,
    UpdateJob,
    ListJobsQuery,
    ListJobsResponse,
    CountJobsQuery,
    CreateJobDefinition,
    CreateJob,
    ListJobDefinitionsResponse,
    UpdateJobDefinition,
    CreateJobFromDefinition,
    Status,
)
from jupyter_scheduler.scheduler import Scheduler
from jupyter_scheduler.scheduler import BaseScheduler
from jupyter_scheduler.exceptions import SchedulerError
from sagemaker_studio_jupyter_scheduler.util.aws_config import get_aws_account_id, get_execution_role_arn
from sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter import (
    InternalMetadataAdapter,
)

from sagemaker_studio_jupyter_scheduler.logging import async_with_metrics

from sagemaker_studio_jupyter_scheduler.util.app_metadata import (
    get_partition,
    get_region_name,
    get_space_type,
)

from sagemaker_studio_jupyter_scheduler.util.aws_clients import (
    get_sagemaker_client,
    SageMakerAsyncBoto3Client,
    EventBridgeAsyncBotoClient,
    S3AsyncBoto3Client,
    DataZoneAsyncBotoClient,
    get_s3_client,
    get_event_bridge_client,
    get_datazone_client,
)
from sagemaker_studio_jupyter_scheduler.util.cron_util import (
    EventBridgeCronExpressionAdapter,
    DEFAULT_CRON_EXPRESSION,
)
from sagemaker_studio_jupyter_scheduler.util.deletable_resource import (
    DeletableResourceContainer,
    DeletableResource,
)
from sagemaker_studio_jupyter_scheduler.providers.tags import get_resource_create_tags
from sagemaker_studio_jupyter_scheduler.s3_uri import S3URI
from sagemaker_studio_jupyter_scheduler.util.utils import (
    generate_dynamic_job_name_for_eventbridge,
    generate_job_identifier,
    get_eventbridge_output_name,
    safe_env_get,
    sanitize_string,
    load_env,
    should_use_jupyter_scheduler,
)
from sagemaker_studio_jupyter_scheduler.util.error_util import (
    SageMakerSchedulerError,
    ErrorMatcher,
    ErrorConverter,
    ErrorFactory,
)
from sagemaker_studio_jupyter_scheduler.util.file_uploader import S3FileUploader
from sagemaker_studio_jupyter_scheduler.model.models import (
    JobTag,
    EventBridgeRuleStatus,
    JobEnvironmentVariableName,
    RuntimeEnvironmentParameterName,
)
from sagemaker_studio_jupyter_scheduler.model.model_converter import ModelConverter
from sagemaker_studio_jupyter_scheduler.model.runtime_environment_parameters import (
    RuntimeEnvironmentParameters,
)

EVENT_BRIDGE_RULE_TARGET_ID = "notebook-execution"
SAGEMAKER_PIPELINE_STEP_NAME = "notebook-execution"
SHARED_SPACE_PREFIX = "RTC:"
SCHEDULE_ENVIRONMENT_CONFIG_NAME = "Scheduling"
SAGEMAKER_TRAINING_JOB_TARGET_ARN = 'arn:aws:scheduler:::aws-sdk:sagemaker:createTrainingJob'


class SageMakerUnifiedStudioScheduler(BaseScheduler):
    """
    This is the template class that will execute logic based on the environment it is being executed in
    """

    task_runner = None

    def __init__(
        self,
        root_dir: str,
        environments_manager: Type[EnvironmentManager],
        config=None,
        converter: ModelConverter = None,
        error_matcher: ErrorMatcher = None,
        error_converter: ErrorConverter = None,
        error_factory: ErrorFactory = None,
        **kwargs,
    ):
        super().__init__(
            root_dir=root_dir,
            environments_manager=environments_manager,
            config=config,
            **kwargs,
        )

        self.current_region = None
        self.root_dir = root_dir
        self.config = config
        self.current_environment = environments_manager.current_environment
        
        # Initialize clients to None - they will be created at runtime via wrapper functions
        self._sagemaker_client = None
        self._event_bridge_client = None
        self._s3_client = None
        self._datazone_client = None
        
        self.converter = converter or ModelConverter(self.log)
        self.error_matcher = error_matcher or ErrorMatcher()
        self.error_converter = error_converter or ErrorConverter()
        self.error_factory = error_factory or ErrorFactory()
        # scheduler implementation for workflow
        self.jupyter_scheduler = Scheduler(
            root_dir=root_dir,
            environments_manager=environments_manager,
            config=config,
            **kwargs,
            )

    def _reset_aws_clients(self):
        # Reset all cached clients, so they will get re-created next time
        # when they are used
        self._s3_client = None
        self._sagemaker_client = None
        self._event_bridge_client = None
        self._datazone_client = None

    def sagemaker_client(self):
        region = get_region_name()

        # If the region we got differs from the region we used when creating
        # boto clients, it is likely customers changed their AWS config.
        # Reset and re-create those clients to avoid cached results.
        if self.current_region != region:
            self._reset_aws_clients()
            self.current_region = region

        if self._sagemaker_client is None:
            self._sagemaker_client = get_sagemaker_client()
        return self._sagemaker_client

    def s3_client(self):
        region = get_region_name()

        # If the region we got differs from the region we used when creating
        # boto clients, it is likely customers changed their AWS config.
        # Reset and re-create those clients to avoid cached results.
        if self.current_region != region:
            self._reset_aws_clients()
            self.current_region = region

        if self._s3_client is None:
            self._s3_client = get_s3_client()
        return self._s3_client

    def event_bridge_client(self):
        region = get_region_name()

        # If the region we got differs from the region we used when creating
        # boto clients, it is likely customers changed their AWS config.
        # Reset and re-create those clients to avoid cached results.
        if self.current_region != region:
            self._reset_aws_clients()
            self.current_region = region

        if self._event_bridge_client is None:
            self._event_bridge_client = get_event_bridge_client()
        return self._event_bridge_client

    def datazone_client(self):
        region = get_region_name()

        # If the region we got differs from the region we used when creating
        # boto clients, it is likely customers changed their AWS config.
        # Reset and re-create those clients to avoid cached results.
        if self.current_region != region:
            self._reset_aws_clients()
            self.current_region = region

        if self._datazone_client is None:
            self._datazone_client = get_datazone_client()
        return self._datazone_client

    def get_schedule_group_name(self, project_identifier: str = None) -> str:
        """Generate schedule group name based on current configuration"""
        if not project_identifier:
            env_config = load_env()
            project_identifier = safe_env_get(env_config, "project_id", "unknown")
        return f"SageMakerUnifiedStudio-{project_identifier}-dev"


    def handle_aws_client_error(self, error, log_message=None):
        if self.error_matcher.is_expired_token_error(error):
            # If we got expired token error, reset all AWS clients to make sure
            # expired token are no longer cached, so clients will get new
            # credentials if customers refresh credentials on their own
            self._reset_aws_clients()
        if isinstance(error, SchedulerError):
            raise error
        elif isinstance(error, botocore.exceptions.ClientError):
            if log_message is not None:
                self.log.error(f"[SageMakerScheduler] Boto client Error: {log_message}")
            raise SageMakerSchedulerError.from_boto_error(error)
        elif isinstance(error, botocore.exceptions.EndpointConnectionError):
            if log_message is not None:
                self.log.error(f"[SageMakerScheduler] Endpoint Connection Error: {log_message}")
            raise SageMakerSchedulerError.from_endpoint_connection_error(error)
        elif isinstance(error, RuntimeError):
            if log_message is not None:
                self.log.error(f"[SageMakerScheduler] Runtime Error: {log_message}")
            raise SageMakerSchedulerError.from_runtime_error(error)
        elif isinstance(error, FileNotFoundError):
            self.log.error(f"[SageMakerScheduler] File not found error: {str(error)}")
            raise SchedulerError(str(error))
        elif isinstance(error, botocore.exceptions.NoCredentialsError):
            self.log.error(f"[SageMakerScheduler] No Credentials Error: {log_message}")
            raise SageMakerSchedulerError.from_no_credentials_error(error)
        elif isinstance(error, botocore.exceptions.ConnectionError):
            # also filters child classes of ConnectionError - ReadTimeoutError, SSLError
            # ConnectTimeoutError, EndpointConnectionError, ProxyConnectionError, ReadTimeoutError
            self.log.error(f"[SageMakerScheduler] {error.__class__.__name__}: {log_message}")
            raise SageMakerSchedulerError.from_connection_error(error)
        else:
            if log_message is None:
                raise error
            else:
                self.log.error(log_message)
                raise self.error_factory.internal_error(error) from error

    async def _verify_bucket_region_and_owner(self, bucket_name: str, cross_account_id: str = ''):
        account_id = cross_account_id if cross_account_id else await get_aws_account_id()

        bucket_location = await self.s3_client().get_bucket_location(
            bucket=bucket_name, accountId=account_id
        )

        # LocationConstraint will be null when bucket is in us-east-1
        bucket_region = bucket_location["LocationConstraint"] or "us-east-1"
        if bucket_region != get_region_name():
            raise SchedulerError(
                f"S3 bucket {bucket_name} must be in region '{get_region_name()}', but found in '{bucket_region}'"
            )

    async def _prepare_job_artifacts(
        self,
        deletable_resources: DeletableResourceContainer,
        training_job_name: str,
        file_name: str,
        runtime_environment_parameters: RuntimeEnvironmentParameters,
        root_dir: str,
        packaged_file_paths: List[str],
    ) -> S3FileUploader:
        input_uri = S3URI(runtime_environment_parameters.s3_input)
        output_uri = S3URI(runtime_environment_parameters.s3_output)

        try:
            await asyncio.gather(
                    self._verify_bucket_region_and_owner(input_uri.bucket, runtime_environment_parameters.s3_input_account_id),
                    self._verify_bucket_region_and_owner(output_uri.bucket, runtime_environment_parameters.s3_output_account_id),
                )
        except botocore.exceptions.ClientError as error:
            raise SageMakerSchedulerError.from_boto_error(
                error,
                f"Failed to verify bucket location and owner for {set([input_uri.bucket, output_uri.bucket])}",
            )

        file_upload_account_id = runtime_environment_parameters.s3_input_account_id

        s3_file_uploader = S3FileUploader(
            deletable_resources,
            runtime_environment_parameters.s3_input,
            file_upload_account_id,
            training_job_name,
            file_name,
            runtime_environment_parameters.sm_init_script,
            runtime_environment_parameters.sm_lcc_init_script_arn,
            root_dir,
            packaged_file_paths
        )

        self.log.info(f"[SageMakerScheduler] Uploading artifacts for job {training_job_name}...")
        try:
            await s3_file_uploader.upload()
        except Exception as error:
            raise SageMakerSchedulerError.from_boto_error(
                error, f"Uploading artifacts to S3 bucket failed - {input_uri.bucket}"
            )

        self.log.info(f"[SageMakerScheduler] Successfully uploaded artifacts for job {training_job_name}.")

        return s3_file_uploader

    def get_packaged_file_paths(self, input_uri: str) -> List[str]:
        packaged_file_paths = []
        input_notebook_path = os.path.join(self.root_dir, input_uri)
        source_dir = os.path.dirname(input_notebook_path)

        for dirpath, dirs, files in os.walk(source_dir):
            dirs[:] = [dir for dir in dirs if not dir.startswith(".")]
            files = [file for file in files if not file.startswith(".")]

            for file in files:
                filepath = os.path.join(dirpath, file)
                if filepath != input_notebook_path:
                    rel_path = os.path.relpath(filepath, source_dir)
                    packaged_file_paths.append(rel_path)

        return packaged_file_paths

    async def get_schedule_type_configuration(self, domain_identifier: str, project_identifier: str) -> Dict[str, str]:
        """
        Get schedule type configuration based on whether managed schedule is enabled
        
        Parameters:
        - domain_identifier: DataZone domain identifier
        - project_identifier: DataZone project identifier
        
        Returns:
        - Dictionary containing scheduleFormName, scheduleFormType, and scheduleAssetType
        """
        is_managed_schedule_enabled = await self.is_managed_schedule_enabled(domain_identifier)
        
        if is_managed_schedule_enabled:
            schedule_form_name = SAGEMAKER_SCHEDULE_FORM_NAME
            schedule_form_type = f"amazon.datazone.{SAGEMAKER_SCHEDULE_FORM_TYPE_NAME}"
            schedule_asset_type = f"amazon.datazone.{SAGEMAKER_SCHEDULE_ASSET_TYPE}"
        else:
            # Use custom schedule form name based on project
            custom_schedule_form_name = f"{SAGEMAKER_SCHEDULE_FORM_TYPE_NAME}_{project_identifier}"
            schedule_form_name = custom_schedule_form_name
            schedule_form_type = f"{domain_identifier}.{custom_schedule_form_name}"
            schedule_asset_type = f"{SAGEMAKER_SCHEDULE_ASSET_TYPE}_{project_identifier}"
        
        return {
            "scheduleFormName": schedule_form_name,
            "scheduleFormType": schedule_form_type,
            "scheduleAssetType": schedule_asset_type
        }

    async def is_managed_schedule_enabled(self, domain_identifier: str) -> bool:
        """
        Check if managed schedule type is enabled for the domain
        
        Parameters:
        - domain_identifier: DataZone domain identifier
        
        Returns:
        - True if managed schedule is enabled, False otherwise
        """
        try:
            # Use GetAssetType to check if managed schedule type is enabled for the domain
            await self.datazone_client().get_asset_type(
                domain_identifier=domain_identifier,
                identifier=f"amazon.datazone.{SAGEMAKER_SCHEDULE_ASSET_TYPE}"
            )
            return True
        except Exception as error:
            # Check if this is a ResourceNotFoundException (asset type not found)
            if hasattr(error, 'response') and error.response.get('Error', {}).get('Code') == 'ResourceNotFoundException':
                return False
            else:
                # Re-raise other errors
                raise error

    async def createDataZoneAsset(self, domain_identifier: str, project_identifier: str, schedule_arn: str, training_job_input: Dict) -> Dict:
        """
        Create a DataZone asset for the scheduled job
        """
        
        # Get schedule type configuration based on managed schedule availability
        schedule_config = await self.get_schedule_type_configuration(domain_identifier, project_identifier)
        schedule_form_name = schedule_config["scheduleFormName"]
        schedule_form_type = schedule_config["scheduleFormType"]
        schedule_asset_type = schedule_config["scheduleAssetType"]
        
        # Get additional schedule details from EventBridge get_schedule API
        schedule_name = training_job_input.get("TrainingJobName", "")
        group_name = self.get_schedule_group_name()
        
        try:
            describe_schedule_response = await self.event_bridge_client().get_schedule(
                name=schedule_name,
                group_name=group_name
            )
            start_time = describe_schedule_response.get("StartDate") if describe_schedule_response.get("StartDate") else datetime.now(timezone.utc)
            end_time = describe_schedule_response.get("EndDate") if describe_schedule_response.get("EndDate") else datetime.now(timezone.utc)
            state = describe_schedule_response.get("State")
        except Exception as error:
            self.log.warning(f"[SageMakerScheduler] Failed to describe schedule {schedule_name}: {error}")
            start_time = None
            end_time = None
            state = None
        connection = ''  # Set connection as None as requested
        
        # Get description from notebook name in tags
        schedule_description = ""
        if "Tags" in training_job_input:
            for tag in training_job_input["Tags"]:
                if tag.get("Key") == "sagemaker:notebook-name":
                    schedule_description = f"Scheduled execution of {tag.get('Value', '')}"
                    break
        
        # Fallback to a default description if not found
        if not schedule_description:
            schedule_description = "Scheduled notebook execution"
        
        # Get S3 input path from training job input for artifactPath
        artifact_path = None
        if "InputDataConfig" in training_job_input and training_job_input["InputDataConfig"]:
            input_config = training_job_input["InputDataConfig"][0]  # Take first input data config
            s3_base_path = input_config.get("DataSource", {}).get("S3DataSource", {}).get("S3Uri")
            
            # Get notebook filename from Environment variables
            notebook_name = None
            if "Environment" in training_job_input:
                notebook_name = training_job_input["Environment"].get(JobEnvironmentVariableName.SM_INPUT_NOTEBOOK_NAME.value)
            
            # Combine S3 path with notebook filename
            if s3_base_path and notebook_name:
                artifact_path = f"{s3_base_path.rstrip('/')}/{notebook_name}"
            else:
                artifact_path = s3_base_path
        
        create_asset_request = {
            "domainIdentifier": domain_identifier,
            "owningProjectIdentifier": project_identifier,
            "name": schedule_name,
            "description": schedule_description,
            "formsInput": [
                {
                    "formName": ASSET_COMMON_DETAILS_FORM_NAME,
                    "typeIdentifier": ASSET_COMMON_DETAILS_FORM_TYPE,
                    "content": json.dumps({
                        "sourceIdentifier": schedule_arn,
                    }),
                },
                {
                    "formName": schedule_form_name,
                    "typeIdentifier": schedule_form_type,
                    "content": json.dumps({
                        "scheduleName": schedule_name,
                        "artifactType": "notebook",
                        "artifactPath": artifact_path,
                        "type": EVENTBRIDGE,
                        "connection": connection,
                        "startTime": start_time.isoformat() if isinstance(start_time, datetime) else start_time,
                        "endTime": end_time.isoformat() if isinstance(end_time, datetime) else end_time,
                        "status": state,
                    }),
                },
            ],
            "typeIdentifier": schedule_asset_type,
        }

        try:
            self.log.info(f"[SageMakerScheduler] Creating DataZone asset for schedule {schedule_name} with parameters {create_asset_request}")
            response = await self.datazone_client().create_asset(create_asset_request)
            
            # Remove metadata from response similar to TypeScript version
            metadata = response.pop("ResponseMetadata", {})
            asset = response
            
            self.log.info(f"[SageMakerScheduler] Successfully created DataZone asset for schedule {schedule_name}.")
            return {"metadata": metadata, "asset": asset}
            
        except Exception as error:
            error_message = f"Error creating asset: {str(error)}"
            self.log.error(f"[SageMakerScheduler] {error_message}")
            raise self.error_factory.internal_error(error_message) from error

    async def deleteDataZoneAsset(self, domain_identifier: str, project_identifier: str, schedule_name: str) -> Dict:
        """
        Delete a DataZone asset for the scheduled job
        
        Parameters:
        - domain_identifier: DataZone domain identifier
        - project_identifier: DataZone project identifier  
        - schedule_name: Name of the schedule to delete the asset for
        
        Returns:
        Empty dictionary on success
        """
        
        # Search for the asset by schedule name - support both managed and custom forms for backward compatibility
        search_params = {
            "domainIdentifier": domain_identifier,
            "owningProjectIdentifier": project_identifier,
            "searchScope": "ASSET",
            "searchText": f'"{schedule_name}"',
            "searchIn": [
                {
                    "attribute": f"{SAGEMAKER_SCHEDULE_FORM_TYPE_NAME}_{project_identifier}.scheduleName"
                },
                {
                    "attribute": f"{SAGEMAKER_SCHEDULE_FORM_NAME}.scheduleName"
                }
            ],
            "additionalAttributes": ["FORMS"]
        }
        
        try:
            self.log.info(f"[SageMakerScheduler] Searching for DataZone asset for schedule {schedule_name}")
            search_response = await self.datazone_client().search(search_params)
            
            # Find the asset with matching schedule name
            schedule_item = None
            if search_response.get("items"):
                for item in search_response["items"]:
                    asset_item = item.get("assetItem")
                    if asset_item and asset_item.get("name") == schedule_name:
                        schedule_item = item
                        break
            
            if not schedule_item or not schedule_item.get("assetItem"):
                error_message = f"Asset not found for schedule: {schedule_name}, consider it's a job from job definition"
                self.log.error(f"[SageMakerScheduler] {error_message}")
                return {}
            
            asset_id = schedule_item["assetItem"]["identifier"]
            
        except Exception as error:
            error_message = f"Error getting asset for schedule {schedule_name}: {str(error)}"
            self.log.error(f"[SageMakerScheduler] {error_message}")
            raise self.error_factory.internal_error(error_message) from error
        
        # Delete the asset
        try:
            self.log.info(f"[SageMakerScheduler] Deleting DataZone asset {asset_id} for schedule {schedule_name}")
            await self.datazone_client().delete_asset(domain_identifier, asset_id)
            
            self.log.info(f"[SageMakerScheduler] Successfully deleted DataZone asset for schedule {schedule_name}")
            return {}
            
        except Exception as error:
            error_message = f"Error deleting asset for schedule: {str(error)}"
            self.log.error(f"[SageMakerScheduler] {error_message}")
            raise self.error_factory.internal_error(error_message) from error

    async def deleteSchedule(self, schedule_name: str) -> Dict:
        """
        Delete an EventBridge schedule
        
        Parameters:
        - schedule_name: Name of the schedule to delete
        
        Returns:
        Empty dictionary on success
        """
        # Get the schedule group name
        group_name = self.get_schedule_group_name()
        
        try:
            self.log.info(f"[SageMakerScheduler] Deleting EventBridge schedule {schedule_name} from group {group_name}")
            await self.event_bridge_client().delete_schedule(
                name=schedule_name,
                group_name=group_name
            )
            
            self.log.info(f"[SageMakerScheduler] Successfully deleted EventBridge schedule {schedule_name}")
            return {}
            
        except Exception as error:
            error_message = f"Error deleting schedule {schedule_name}: {str(error)}"
            self.log.error(f"[SageMakerScheduler] {error_message}")
            raise self.error_factory.internal_error(error_message) from error
    
    async def _create_eventbridge_schedule_and_datazone_asset(
        self,
        training_job_input: Dict,
        schedule_name: str,
        schedule_expression: str,
        job_name: str
    ) -> str:
        """
        Helper function to create EventBridge schedule and DataZone asset
        
        Parameters:
        - training_job_input: Dictionary containing training job configuration
        - schedule_name: Name of the schedule
        - schedule_expression: Schedule expression for EventBridge
        
        Returns:
        - schedule_name: The name of the created schedule
        """
        
        # 1. Get schedule group name
        group_name = self.get_schedule_group_name()
        
        # 2. Get description
        description = self.get_created_resources_description_text()
        
        # 3. Get environment configuration and role ARN from caller identity
        env_config = load_env()
        project_id = safe_env_get(env_config, "project_id", "unknown")
        env_id = safe_env_get(env_config, "environment_id", "unknown")
        
        # Get role ARN from caller identity
        partition = get_partition()
        role_arn = await get_execution_role_arn(project_id, env_id, partition)
        

        eventbridge_input = dict(training_job_input)

        # override parameters for recurrent schedules
        if not schedule_expression.startswith("at"):
            # 3. Modify output notebook name to use pipeline expression for scheduled executions
            # Extract notebook name from the environment
            notebook_name = eventbridge_input["Environment"].get(
                JobEnvironmentVariableName.SM_INPUT_NOTEBOOK_NAME.value, ""
            )
            [notebook_name_without_ext, notebook_extension] = os.path.splitext(notebook_name)
            eventbridge_input["Environment"][
                JobEnvironmentVariableName.SM_OUTPUT_NOTEBOOK_NAME.value
            ] = get_eventbridge_output_name(
                job_name, notebook_name_without_ext, notebook_extension
            )

            eventbridge_input["TrainingJobName"] = generate_dynamic_job_name_for_eventbridge(job_name, notebook_name=notebook_name)

        
        # 4. Create target configuration
        target = {
            "Arn": SAGEMAKER_TRAINING_JOB_TARGET_ARN,
            "RoleArn": role_arn,
            "Input": json.dumps(eventbridge_input),
            "RetryPolicy": {
                "MaximumRetryAttempts": 3,
                "MaximumEventAgeInSeconds": 86400
            }
        }

        # 5. Create the schedule using EventBridge Scheduler
        self.log.info(f"[SageMakerScheduler] Creating EventBridge Schedule for job {schedule_name}...")
        
        try:
            eb_schedule_response = await self.event_bridge_client().create_schedule(
                name=schedule_name,
                group_name=group_name,
                schedule_expression=schedule_expression,
                description=description,
                target=target,
                flexible_time_window={"Mode": "OFF"}
            )
        except Exception as error:

            self.log.info(f"target is {target}")
            self.handle_aws_client_error(
                error,
                f"Error when calling EventBridge Scheduler CreateSchedule for job {schedule_name}: {error}",
            )
        
        self.log.info(f"[SageMakerScheduler] Successfully created EventBridge Schedule for job {schedule_name}.")
        
        # 6. Create DataZone Asset after EventBridge Schedule creation
        try:
            # Get domain and project identifiers and schedule ARN
            domain_id = safe_env_get(env_config, "domain_id", "unknown")
            schedule_arn = eb_schedule_response.get("ScheduleArn")
            
            # Create DataZone asset
            await self.createDataZoneAsset(domain_id, project_id, schedule_arn, training_job_input)
            
        except Exception as error:
            self.log.error(f"[SageMakerScheduler] Error creating DataZone asset for job {schedule_name}: {error}")
            # Note: We don't fail the entire job creation if DataZone asset creation fails
        
        return schedule_name

    @async_with_metrics("CreateJob")
    async def create_job(self, input: CreateJob, metrics: MetricsContext) -> str:
        """
        Create a scheduled job using EventBridge Scheduler
        """

        if should_use_jupyter_scheduler(input):
            try:
                self.log.info(f"[SageMakerScheduler] create_job: runtime_environment_name is {input.runtime_environment_name}, delegating to jupyter scheduler")
                return self.jupyter_scheduler.create_job(input)
            except Exception as error:
                self.log.error(f"[SageMakerScheduler] create_job: Error delegating to jupyter scheduler: {error}")
                # Continue with SageMaker logic
                raise error
        
        # 1. Create schedule expression with current UTC time
        current_utc_time = datetime.now(timezone.utc)
        schedule_expression = f"at({current_utc_time.strftime('%Y-%m-%dT%H:%M:%S')})"
        
        # 2. Get training job input with schedule expression
        training_job_input = await self.create_training_job_input(input, metrics, schedule_expression)
        
        eventbridge_schedule_name = training_job_input["TrainingJobName"]
        
        # 3. Call helper function to create EventBridge schedule and DataZone asset
        return await self._create_eventbridge_schedule_and_datazone_asset(
            training_job_input, eventbridge_schedule_name, schedule_expression, input.name
        )

    async def create_training_job_input(self, input: CreateJob | CreateJobDefinition, metrics: MetricsContext, schedule_expression: str = None) -> str:
        """
        The SageMaker implementation of `POST scheduler/jobs`

        # TODO: better documentation
        """

        # log the input parameters
        self.log.info(f"[SageMakerScheduler] Input parameters for create_job: {input}")

        training_job_name = generate_job_identifier(
            name=input.name,
            notebook_name=os.path.splitext(os.path.basename(input.input_uri))[0],
        )
        metrics.set_property("Id", training_job_name)

        deletable_resources = DeletableResourceContainer(self.log)

        packaged_file_paths = []
        if input.package_input_folder:
            packaged_file_paths = self.get_packaged_file_paths(input.input_uri)
            self.log.info("[SageMakerScheduler] Creating a job with packaged input folder...")
        try:
            s3_file_uploader = await self._prepare_job_artifacts(
                deletable_resources=deletable_resources,
                training_job_name=training_job_name,
                file_name=input.input_uri,
                runtime_environment_parameters=RuntimeEnvironmentParameters(
                    input.runtime_environment_parameters
                ),
                root_dir=self.root_dir,
                packaged_file_paths=packaged_file_paths
            )

            self.log.info(f"[SageMakerScheduler] Getting S3 dependency Uri...")
            stage = InternalMetadataAdapter().get_stage()
            self.log.info(f"[SageMakerScheduler] Successfully got S3 dependency Uri")

            create_training_job_input = (
                await self.converter.to_create_training_job_input(
                    training_job_name=training_job_name,
                    upstream_model=input,
                    s3_file_uploader=s3_file_uploader,
                )
            )

            create_training_job_input["TrainingJobName"] = training_job_name

            self.log.info(
                f"[SageMakerScheduler] Calling SageMaker CreateTrainingJob for job {training_job_name}..."
            )

            try:
                create_training_job_input["Tags"] = await get_resource_create_tags(
                    job_name=input.name,
                    notebook_name=s3_file_uploader.notebook_name,
                    headless_driver_version="false",  # TODO: Update this to the correct version
                    logger=self.log,
                )

                # Add sagemaker-studio:user-id tag from environment configuration
                env_config = load_env()
                user_id = safe_env_get(env_config, "user_id", "unknown")
                # check if user_id is a valid uuid
                if user_id != "unknown" and user_id.count('-') == 4:
                    create_training_job_input["Tags"].append(
                        {
                            "Key": JobTag.SMUS_USER_ID,
                            "Value": user_id,
                        }
                    )

                # Add job-definition-id tag for recurring schedules (not one-time schedules that start with "at")
                if schedule_expression:
                    if not schedule_expression.startswith("at"):
                        create_training_job_input["Tags"].append(
                            {
                                "Key": JobTag.JOB_DEFINITION_ID,
                                "Value": training_job_name,
                            }
                        )
                    else:
                        create_training_job_input["Tags"].append(
                            {
                                "Key": JobTag.ONE_TIME_SCHEDULE,
                                "Value": "true",
                            }
                        )

                # log the create_training_job_input
                self.log.info(f"create_training_job_input: {create_training_job_input}")

                # await self.sagemaker_client().create_training_job(
                #     create_training_job_input
                # )
            except Exception as error:
                self.log.error(
                    f"[SageMakerScheduler] Error when calling SageMaker CreateTrainingJob or ListTags with job {training_job_name}: {error}"
                )
                raise error

            # All operations succeeded, so don't delete any resources.
            deletable_resources.clear()

        except Exception as error:
            self.handle_aws_client_error(error)
        finally:
            await deletable_resources.delete_all()

        self.log.info(
            f"[SageMakerScheduler] Successfully called SageMaker CreateTrainingJob for job {training_job_name}."
        )

        return create_training_job_input
    

    async def update_job(self, job_id: str, model: UpdateJob):
        """Updates job metadata in the persistence store,
        for example name, status etc. In case of status
        change to STOPPED, should call stop_job
        """
        if should_use_jupyter_scheduler(job_id):
            try:
                self.log.info(f"[SageMakerScheduler] update_job: Job ID {job_id} is UUID format, delegating to jupyter scheduler")
                return self.jupyter_scheduler.update_job(job_id, model)
            except Exception as error:
                self.log.error(f"[SageMakerScheduler] update_job: Error delegating to jupyter scheduler: {error}")
                # Continue with SageMaker logic
                pass
        
        # SageMaker logic for updating job - currently not implemented
        pass

    @async_with_metrics("CreateJobFromJobDefinition")
    async def create_job_from_definition(
        self,
        job_definition_id: str,
        model: CreateJobFromDefinition,
        metrics: MetricsContext,
    ):
        try:
            metrics.set_property("Id", job_definition_id)
            group_name = self.get_schedule_group_name()
            
            self.log.info(
                f"[SageMakerScheduler] Calling EventBridge Scheduler GetSchedule for job definition {job_definition_id}..."
            )
            
            # Get job definition details from EventBridge Schedule
            describe_schedule_response = await self.event_bridge_client().get_schedule(
                name=job_definition_id,
                group_name=group_name
            )
            
            self.log.info(
                f"[SageMakerScheduler] Successfully called EventBridge Scheduler GetSchedule for job definition {job_definition_id}."
            )

            # Extract training job details from EventBridge target
            target = describe_schedule_response.get("Target", {})
            if not target.get("Input"):
                raise SchedulerError(f"No training job configuration found in EventBridge schedule {job_definition_id}")
            
            try:
                training_job_template = json.loads(target["Input"])
            except json.JSONDecodeError as error:
                raise SchedulerError(f"Failed to parse training job configuration from EventBridge schedule {job_definition_id}: {error}")

            environment = training_job_template.get("Environment", {})
            
            # Extract job details from tags
            tag_dict = self.converter.to_tag_dict(training_job_template.get("Tags", []))
            job_name = tag_dict.get(JobTag.NAME.value, "Untitled Job")
            notebook_name = environment.get(JobEnvironmentVariableName.SM_INPUT_NOTEBOOK_NAME.value, "")

            # Generate unique job ID for this execution
            job_id = generate_job_identifier(
                name=job_name,
                notebook_name=os.path.splitext(notebook_name)[0] if notebook_name else "notebook",
            )

            # Create a copy of the training job template for this execution
            training_job_details = dict(training_job_template)
            
            # Update job-specific parameters
            training_job_details["TrainingJobName"] = job_id
            training_job_details["HyperParameters"] = model.parameters or {}
            
            # Generate unique output notebook name for this execution (not parameterized)
            if notebook_name:
                training_job_details["Environment"][
                    JobEnvironmentVariableName.SM_OUTPUT_NOTEBOOK_NAME.value
                ] = self.converter.generate_training_job_name(
                    job_name=job_name,
                    notebook_name=notebook_name,
                )

            # Keep all existing tags including job-definition-id tag (this shows it came from a job definition)
            # Just add a reference to the source job definition for clarity
            updated_tags = list(training_job_details.get("Tags", []))
            
            # Add reference to the source job definition if not already present
            has_source_ref = any(
                tag.get("Key") == "sagemaker:source-job-definition-id" 
                for tag in updated_tags
            )
            if not has_source_ref:
                updated_tags.append({
                    "Key": "sagemaker:source-job-definition-id",
                    "Value": job_definition_id,
                })
            
            training_job_details["Tags"] = updated_tags

            self.log.info(f"[SageMakerScheduler] Creating job {job_id} from job definition {job_definition_id}...")
            
            # Create EventBridge schedule for immediate execution
            current_utc_time = datetime.now(timezone.utc)
            schedule_expression = f"at({current_utc_time.strftime('%Y-%m-%dT%H:%M:%S')})"
            
            # Create EventBridge schedule and DataZone asset
            await self._create_eventbridge_schedule_and_datazone_asset(
                training_job_input=training_job_details,
                schedule_name=job_id,
                schedule_expression=schedule_expression,
                job_name=job_name
            )
            
            self.log.info(
                f"[SageMakerScheduler] Successfully created job {job_id} from job definition {job_definition_id}."
            )
            return job_id
            
        except Exception as error:
            self.handle_aws_client_error(
                error,
                f"Error when creating job from definition {job_definition_id}: {error}",
            )


    @async_with_metrics("ListJobs")
    async def list_jobs(
        self, query: ListJobsQuery, metrics: MetricsContext
    ) -> ListJobsResponse:
        """Returns list of all jobs filtered by query from both jupyter scheduler and unified studio"""

        self.log.info("[SageMakerScheduler] Calling both jupyter scheduler and SageMaker Search in parallel...")

        # max_items has default value and if it's overridden as 0, return empty list without calling
        # search API. Max_items as 0 is used by a contract from OSS side to detect the
        # scheduler extension availability.
        if query.max_items == 0:
            return ListJobsResponse(jobs=[])

        async def get_jupyter_scheduler_jobs():
            """Get jobs from jupyter scheduler"""
            try:
                jupyter_response = self.jupyter_scheduler.list_jobs(query)
                self.log.info(f"[SageMakerScheduler] Successfully retrieved {len(jupyter_response.jobs)} jobs from jupyter scheduler.")
                return jupyter_response
            except Exception as error:
                self.log.error(f"[SageMakerScheduler] Error calling jupyter scheduler list_jobs: {error}")
                return ListJobsResponse(jobs=[])

        async def get_unified_studio_jobs():
            """Get jobs from unified studio (SageMaker)"""
            try:
                training_job_list_response = await self.sagemaker_client().search(
                    self.converter.to_training_job_search_input(query)
                )
                unified_studio_response = self.converter.to_jupyter_list_jobs_response(
                    self, training_job_list_response
                )
                self.log.info(f"[SageMakerScheduler] Successfully retrieved {len(unified_studio_response.jobs)} jobs from unified studio.")
                return unified_studio_response
            except Exception as error:
                self.log.error(f"[SageMakerScheduler] Error calling unified studio list_jobs: {error}")
                return ListJobsResponse(jobs=[])

        # Run both schedulers in parallel
        jupyter_response, unified_studio_response = await asyncio.gather(
            get_jupyter_scheduler_jobs(),
            get_unified_studio_jobs(),
            return_exceptions=True
        )

        # Handle exceptions from parallel execution
        if isinstance(jupyter_response, Exception):
            self.log.error(f"[SageMakerScheduler] Exception in jupyter scheduler list_jobs: {jupyter_response}")
            jupyter_response = ListJobsResponse(jobs=[])
        
        if isinstance(unified_studio_response, Exception):
            self.log.error(f"[SageMakerScheduler] Exception in unified studio list_jobs: {unified_studio_response}")
            unified_studio_response = ListJobsResponse(jobs=[])

        # Combine results with jupyter scheduler results first
        combined_jobs = jupyter_response.jobs + unified_studio_response.jobs
        
        # Use jupyter scheduler next_token first if it has it, otherwise use unified studio's
        combined_next_token = jupyter_response.next_token or unified_studio_response.next_token
        
        # Calculate total count (sum of both if available, otherwise use -1)
        if (jupyter_response.total_count is not None and jupyter_response.total_count >= 0 and 
            unified_studio_response.total_count is not None and unified_studio_response.total_count >= 0):
            combined_total_count = jupyter_response.total_count + unified_studio_response.total_count
        else:
            combined_total_count = -1

        self.log.info(f"[SageMakerScheduler] Combined {len(jupyter_response.jobs)} jupyter scheduler jobs and {len(unified_studio_response.jobs)} unified studio jobs.")

        return ListJobsResponse(
            jobs=combined_jobs,
            next_token=combined_next_token,
            total_count=combined_total_count
        )

    async def count_jobs(self, query: CountJobsQuery) -> int:
        """Returns number of jobs filtered by query"""
        pass

    @async_with_metrics("DescribeJob")
    async def get_job(
        self,
        job_id: str,
        outputs: Optional[bool] = True,
        metrics: MetricsContext = None,
    ) -> DescribeJob:
        """Returns job record for a single job"""

        if should_use_jupyter_scheduler(job_id):
            try:
                self.log.info(f"[SageMakerScheduler] get_job: Job ID {job_id} is UUID format, delegating to jupyter scheduler")
                return self.jupyter_scheduler.get_job(job_id)
            except Exception as error:
                self.log.error(f"[SageMakerScheduler] get_job: Error delegating to jupyter scheduler: {error}")
                # Continue with SageMaker logic
                raise error

        self.log.info(f"[SageMakerScheduler] Calling SageMaker DescribeTrainingJob for job {job_id}...")

        try:
            training_job_response = await self.sagemaker_client().describe_training_job(
                job_name=job_id
            )
        except Exception as error:
            self.handle_aws_client_error(
                error,
                f"Error when calling SageMaker DescribeTrainingJob for job {job_id}: {error}",
            )

        self.log.info(
            f"[SageMakerScheduler] Successfully called SageMaker DescribeTrainingJob for job {job_id}."
        )

        # Extract the Training Job ARN from the response since its case might differ from the Training Job Name.
        resource_arn = training_job_response["TrainingJobArn"]

        self.log.info(f"[SageMakerScheduler] Calling SageMaker ListTags for {resource_arn}...")

        try:
            list_tags_response = await self.sagemaker_client().list_tags(
                resource_arn=resource_arn
            )
        except Exception as error:
            self.handle_aws_client_error(
                error,
                f"Error when calling SageMaker ListTags for {resource_arn}: {error}",
            )

        self.log.info(f"[SageMakerScheduler] Successfully called SageMaker ListTags for {resource_arn}.")

        return self.converter.to_jupyter_describe_job_output(
            scheduler=self,
            outputs=outputs,
            training_job_response=training_job_response,
            tag_dict=self.converter.to_tag_dict(list_tags_response["Tags"]),
        )

    @async_with_metrics("DeleteJob")
    async def delete_job(self, job_id: str, metrics: MetricsContext):
        """Deletes the job record, stops the job if running"""

        metrics.set_property("Id", job_id)

        if should_use_jupyter_scheduler(job_id):
            try:
                self.log.info(f"[SageMakerScheduler] delete_job: Job ID {job_id} is UUID format, delegating to jupyter scheduler")
                return self.jupyter_scheduler.delete_job(job_id)
            except Exception as error:
                self.log.error(f"[SageMakerScheduler] delete_job: Error delegating to jupyter scheduler: {error}")
                # Continue with SageMaker logic
                raise error

        # Call DescribeTrainingJob to get the ARN, since its case does not necessarily not match the training job name.
        self.log.info(f"Calling SageMaker DescribeTrainingJob for job {job_id}...")

        try:
            training_job_details = await self.sagemaker_client().describe_training_job(
                job_id
            )
        except Exception as error:
            self.handle_aws_client_error(
                error,
                f"Error in describe_training_job while processing job {job_id}"
            )

        self.log.info(
            f"[SageMakerScheduler] Successfully called SageMaker DescribeTrainingJob for job {job_id}..."
        )

        resource_arn = training_job_details["TrainingJobArn"]

        self.log.info(f"Calling SageMaker StopTrainingJob for job {job_id}...")
        self.log.info(f"Calling SageMaker ListTags for {resource_arn}...")

        [stop_job_response, add_tag_response] = await asyncio.gather(
            self.sagemaker_client().stop_training_job(training_job_name=job_id),
            self.sagemaker_client().add_tags(
                resource_arn=resource_arn,
                tag_list=self.converter.to_tag_list(
                    {JobTag.IS_STUDIO_ARCHIVED.value: "true"}
                ),
            ),
            return_exceptions=True,
        )

        if isinstance(stop_job_response, botocore.exceptions.ClientError):
            if not self.error_matcher.is_training_job_status_validation_error(
                stop_job_response
            ):
                self.log.error(
                    f"[SageMakerScheduler] Boto client error when calling SageMaker StopTrainingJob for job {job_id}: {stop_job_response}"
                )
                raise self.error_converter.boto_error_to_web_error(
                    stop_job_response
                ) from stop_job_response
        elif isinstance(stop_job_response, Exception):
            self.log.error(
                f"[SageMakerScheduler] Error when calling SageMaker StopTrainingJob for job {job_id}: {stop_job_response}"
            )
            raise self.error_factory.internal_error(
                stop_job_response
            ) from stop_job_response

        self.log.info(
            f"[SageMakerScheduler] Successfully called SageMaker StopTrainingJob for job {job_id}."
        )

        if isinstance(add_tag_response, Exception):
            self.log.error(
                f"[SageMakerScheduler] Error when calling SageMaker AddTags for {resource_arn}: {add_tag_response}"
            )
            raise self.error_factory.internal_error(
                add_tag_response
            ) from add_tag_response

        self.log.info(f"[SageMakerScheduler] Successfully called SageMaker ListTags for {resource_arn}.")

        # Delete EventBridge schedule
        try:
            self.log.info(f"[SageMakerScheduler] Attempting to delete EventBridge schedule for job {job_id}")
            await self.deleteSchedule(job_id)
        except Exception as error:
            self.log.error(f"[SageMakerScheduler] Error deleting EventBridge schedule for job {job_id}: {error}")
            # Note: We don't fail the entire job deletion if schedule deletion fails

        # Delete DataZone asset
        try:
            # Get environment configuration for domain and project identifiers
            env_config = load_env()
            domain_id = safe_env_get(env_config, "domain_id", "unknown")
            project_id = safe_env_get(env_config, "project_id", "unknown")
            
            self.log.info(f"[SageMakerScheduler] Attempting to delete DataZone asset for job {job_id}")
            await self.deleteDataZoneAsset(domain_id, project_id, job_id)
        except Exception as error:
            self.log.error(f"[SageMakerScheduler] Error deleting DataZone asset for job {job_id}: {error}")
            # Note: We don't fail the entire job deletion if DataZone asset deletion fails

    @async_with_metrics("StopJob")
    async def stop_job(self, job_id: str, metrics: MetricsContext):
        """Stops the job, this is not analogous
        to the REST API that will be called to
        stop the job. Front end will call the PUT
        API with status update to STOPPED, which will
        call the update_job method. This method is
        supposed to do the work of actually stopping
        the process that is executing the job. In case
        of a task runner, you can assume a call to task
        runner to suspend the job.
        """

        metrics.set_property("Id", job_id)
        self.log.info(f"[SageMakerScheduler] Calling SageMaker StopTrainingJob for job {job_id}...")

        try:
            await self.sagemaker_client().stop_training_job(job_id)
        except Exception as error:
            self.handle_aws_client_error(
                error,
                f"Error when calling SageMaker StopTrainingJob for job {job_id}: {error}",
            )

        self.log.info(
            f"[SageMakerScheduler] Successfully called SageMaker StopTrainingJob for job {job_id}."
        )

    def get_created_resources_description_text(self):
        return "Created for Notebook execution from sagemaker unified studio notebook scheduler"

    @async_with_metrics("CreateJobDefinition")
    async def create_job_definition(
        self, model: CreateJobDefinition, metrics: MetricsContext
    ) -> str:
        """Creates a new job definition record,
        consider this as the template for creating
        recurring/scheduled jobs.
        """
        cron_expression = EventBridgeCronExpressionAdapter(
            model.schedule if model.schedule else DEFAULT_CRON_EXPRESSION
        ).cron_expression

        schedule_expression = f"cron({cron_expression})"

        if get_space_type() == "shared":
            model.input_uri = model.input_uri.replace(SHARED_SPACE_PREFIX, "", 1)
            self.log.info(f'[SageMakerScheduler] Job Definition: Shared Space: remove the RTC: prefix {model.input_uri}')

        # Reuse the existing create_training_job_input function to avoid code duplication
        self.log.info(f"[SageMakerScheduler] Creating training job input for job definition...")
        create_training_job_input = await self.create_training_job_input(model, metrics, schedule_expression)
        
        job_definition_id = create_training_job_input["TrainingJobName"]

        try:
            self.log.info(f"[SageMakerScheduler] Creating EventBridge Schedule for job definition {job_definition_id}")
            
            schedule_result = await self._create_eventbridge_schedule_and_datazone_asset(
                training_job_input=create_training_job_input,
                schedule_name=job_definition_id,
                schedule_expression=schedule_expression,
                job_name=model.name
            )

        except Exception as error:
            self.log.error(
                f"[SageMakerScheduler] Error when calling EventBridge Schedule creation for job definition {job_definition_id}: {error}"
            )
            raise error

        self.log.info(f"[SageMakerScheduler] Successfully created EventBridge Schedule for job definition {job_definition_id}")

        return job_definition_id

    async def _update_eventbridge_schedule(
        self, job_definition_id: str, model: UpdateJobDefinition = None, state: str = None
    ):
        """Update EventBridge Schedule with new schedule expression or state"""
        group_name = self.get_schedule_group_name()

        # Get existing schedule to preserve target configuration
        try:
            existing_schedule = await self.event_bridge_client().get_schedule(
                name=job_definition_id,
                group_name=group_name
            )
        except Exception as error:
            self.handle_aws_client_error(
                error,
                f"Error when getting existing EventBridge Schedule {job_definition_id}: {error}",
            )

        # Determine schedule expression and state
        if model and model.schedule:
            # Update with new schedule expression
            cron_expression = EventBridgeCronExpressionAdapter(model.schedule).cron_expression
            schedule_expression = f"cron({cron_expression})"
            self.log.info(f"[SageMakerScheduler] Updating EventBridge Schedule {job_definition_id} with new schedule expression...")
        else:
            # Keep existing schedule expression
            schedule_expression = existing_schedule.get("ScheduleExpression")
            if state:
                self.log.info(f"[SageMakerScheduler] Updating EventBridge Schedule {job_definition_id} state to {state}...")
            else:
                self.log.info(f"[SageMakerScheduler] Updating EventBridge Schedule {job_definition_id}...")

        # Update the schedule
        try:
            update_params = {
                "name": job_definition_id,
                "group_name": group_name,
                "schedule_expression": schedule_expression,
                "description": self.get_created_resources_description_text(),
                "target": existing_schedule.get("Target"),  # Preserve existing target
                "flexible_time_window": {"Mode": "OFF"}
            }
            
            # Add state if provided (EventBridge Scheduler uses State field)
            if state:
                update_params["state"] = state

            await self.event_bridge_client().update_schedule(**update_params)
        except Exception as error:
            self.handle_aws_client_error(
                error,
                f"Error when calling EventBridge Scheduler UpdateSchedule for {job_definition_id}: {error}",
            )

        self.log.info(
            f"[SageMakerScheduler] Successfully updated EventBridge Schedule {job_definition_id}"
        )

    async def _update_datazone_asset_status(self, job_definition_id: str, status: str):
        """Update only the status field in DataZone asset"""
        # Get environment configuration
        env_config = load_env()
        domain_id = safe_env_get(env_config, "domain_id", "unknown")
        project_id = safe_env_get(env_config, "project_id", "unknown")

        try:
            # Search for existing asset - support both managed and custom forms for backward compatibility
            search_params = {
                "domainIdentifier": domain_id,
                "owningProjectIdentifier": project_id,
                "searchScope": "ASSET",
                "searchText": f'"{job_definition_id}"',
                "searchIn": [
                    {
                        "attribute": f"{SAGEMAKER_SCHEDULE_FORM_TYPE_NAME}_{project_id}.scheduleName"
                    },
                    {
                        "attribute": f"{SAGEMAKER_SCHEDULE_FORM_NAME}.scheduleName"
                    }
                ],
                "additionalAttributes": ["FORMS"]
            }
            
            search_response = await self.datazone_client().search(search_params)
            
            # Find the asset
            asset_item = None
            if search_response.get("items"):
                for item in search_response["items"]:
                    candidate = item.get("assetItem")
                    if candidate and candidate.get("name") == job_definition_id:
                        asset_item = candidate
                        break

            if not asset_item:
                self.log.warning(f"[SageMakerScheduler] DataZone asset not found for schedule {job_definition_id}, skipping asset status update.")
                return

            # Get existing form content and update only status
            asset_forms = asset_item.get("additionalAttributes").get("formsOutput", [])
            schedule_form = None
            common_details_form = None
            
            # Search for schedule form - support both managed and custom forms
            for form in asset_forms:
                form_name = form.get("formName")
                if form_name == f"{SAGEMAKER_SCHEDULE_FORM_TYPE_NAME}_{project_id}" or form_name == SAGEMAKER_SCHEDULE_FORM_NAME:
                    schedule_form = form
                elif form_name == ASSET_COMMON_DETAILS_FORM_NAME:
                    common_details_form = form

            if not schedule_form:
                self.log.warning(f"[SageMakerScheduler] Schedule form not found in DataZone asset for {job_definition_id}")
                return

            # Parse existing content and update status
            try:
                existing_schedule_content = json.loads(schedule_form.get("content", "{}"))
                existing_schedule_content["status"] = status
                
                # Prepare forms input array
                forms_input = []
                
                # Add common details form if it exists (preserve existing content)
                if common_details_form:
                    forms_input.append({
                        "formName": ASSET_COMMON_DETAILS_FORM_NAME,
                        "typeIdentifier": ASSET_COMMON_DETAILS_FORM_TYPE,
                        "content": common_details_form.get("content", "{}"),
                    })
                
                # Add schedule form with updated status - use the existing form configuration
                existing_form_name = schedule_form.get("formName")
                existing_type_identifier = schedule_form.get("typeIdentifier")
                existing_type_name = schedule_form.get("typeName")

                if not existing_type_identifier:
                    existing_type_identifier = existing_type_name
                
                forms_input.append({
                    "formName": existing_form_name,
                    "typeIdentifier": existing_type_identifier,
                    "content": json.dumps(existing_schedule_content),
                })
                
                # Update the asset with both forms
                asset_id = asset_item["identifier"]
                asset_name = asset_item.get("name", job_definition_id)  # Use existing asset name or fallback to job_definition_id
                update_asset_request = {
                    "domainIdentifier": domain_id,
                    "identifier": asset_id,
                    "name": asset_name,  # Required parameter for create_asset_revision
                    "formsInput": forms_input,
                }

                await self.datazone_client().update_asset(update_asset_request)
                self.log.info(f"[SageMakerScheduler] Successfully updated DataZone asset status to {status} for schedule {job_definition_id}.")

            except json.JSONDecodeError as error:
                self.log.error(f"[SageMakerScheduler] Failed to parse existing asset content for {job_definition_id}: {error}")

        except Exception as error:
            self.log.error(f"[SageMakerScheduler] Error updating DataZone asset status for schedule {job_definition_id}: {error}")
            # Don't fail the entire update if DataZone asset update fails

    @async_with_metrics("UpdateJobDefinition")
    async def update_job_definition(
        self,
        job_definition_id: str,
        model: UpdateJobDefinition,
        metrics: MetricsContext,
    ):
        """Updates job definition metadata using EventBridge Scheduler and DataZone assets"""
        metrics.set_property("Id", job_definition_id)
        enable = disable = update = 0

        try:
            if model.active is None:
                # Update schedule expression
                update = 1
                await self._update_eventbridge_schedule(job_definition_id, model)
                
                # Update DataZone asset status to reflect current state (assumed ENABLED for schedule updates)
                await self._update_datazone_asset_status(job_definition_id, "ENABLED")

            elif model.active:
                # Enable schedule
                enable = 1
                await self._update_eventbridge_schedule(job_definition_id, state="ENABLED")
                
                # Update DataZone asset status
                await self._update_datazone_asset_status(job_definition_id, "ENABLED")

            else:
                # Disable schedule
                disable = 1
                await self._update_eventbridge_schedule(job_definition_id, state="DISABLED")
                
                # Update DataZone asset status
                await self._update_datazone_asset_status(job_definition_id, "DISABLED")

        except Exception as error:
            self.handle_aws_client_error(
                error,
                f"Error when updating job definition {job_definition_id}: {error}",
            )

        metrics.put_metric("Enable", enable)
        metrics.put_metric("Disable", disable)
        metrics.put_metric("Update", update)

    @async_with_metrics("DeleteJobDefinition")
    async def delete_job_definition(
        self, job_definition_id: str, metrics: MetricsContext
    ):
        """Deletes the job definition record using EventBridge Scheduler and DataZone assets"""
        try:
            metrics.set_property("Id", job_definition_id)

            # Get environment configuration
            env_config = load_env()
            domain_id = safe_env_get(env_config, "domain_id", "unknown")
            project_id = safe_env_get(env_config, "project_id", "unknown")

            # Delete EventBridge Schedule first
            self.log.info(f"[SageMakerScheduler] Deleting EventBridge Schedule for job definition {job_definition_id}...")
            
            try:
                await self.deleteSchedule(job_definition_id)
                self.log.info(f"[SageMakerScheduler] Successfully deleted EventBridge Schedule {job_definition_id}")
            except Exception as schedule_error:
                self.log.error(f"[SageMakerScheduler] Error deleting EventBridge Schedule {job_definition_id}: {schedule_error}")
                # Continue with DataZone asset deletion even if schedule deletion fails
            
            # Delete DataZone Asset
            self.log.info(f"[SageMakerScheduler] Deleting DataZone asset for job definition {job_definition_id}...")
            
            try:
                await self.deleteDataZoneAsset(domain_id, project_id, job_definition_id)
                self.log.info(f"[SageMakerScheduler] Successfully deleted DataZone asset for job definition {job_definition_id}")
            except Exception as asset_error:
                self.log.error(f"[SageMakerScheduler] Error deleting DataZone asset for job definition {job_definition_id}: {asset_error}")
                # Log error but don't fail the entire deletion

        except Exception as error:
            self.handle_aws_client_error(
                error,
                f"Error when deleting job definition {job_definition_id}: {error}",
            )

    async def _get_schedule_details_batch(self, schedule_names: List[str]) -> Dict[str, Dict]:
        """
        Batch fetch EventBridge schedule details for multiple schedules in parallel
        
        Parameters:
        - schedule_names: List of schedule names to fetch
        
        Returns:
        - Dictionary mapping schedule_name to schedule details (or None if error)
        """
        group_name = self.get_schedule_group_name()
        
        async def get_single_schedule(schedule_name: str) -> Tuple[str, Dict]:
            try:
                describe_schedule_response = await self.event_bridge_client().get_schedule(
                    name=schedule_name,
                    group_name=group_name
                )
                return schedule_name, describe_schedule_response
            except Exception as error:
                self.log.warning(f"[SageMakerScheduler] Error getting schedule details for {schedule_name}: {error}")
                return schedule_name, None
        
        # Fetch all schedules in parallel
        results = await asyncio.gather(
            *[get_single_schedule(name) for name in schedule_names],
            return_exceptions=True
        )
        
        # Build results dictionary
        schedule_details = {}
        for result in results:
            if isinstance(result, tuple):
                schedule_name, schedule_data = result
                schedule_details[schedule_name] = schedule_data
            else:
                # Exception occurred - log it
                self.log.warning(f"[SageMakerScheduler] Exception in batch schedule fetch: {result}")
        
        return schedule_details

    @async_with_metrics("GetJobDefinition")
    async def get_job_definition(
        self,
        job_definition_id: str,
        list_tags_response: Dict = None,
        metrics: MetricsContext = None,
        cached_schedule_response: Dict = None,
    ) -> DescribeJobDefinition:
        """Returns job definition record for a single job definition from EventBridge scheduler
        
        Parameters:
        - job_definition_id: The job definition ID
        - list_tags_response: Optional cached tags response  
        - metrics: Metrics context
        - cached_schedule_response: Optional cached schedule response to avoid duplicate API calls
        """
        if metrics:
            metrics.set_property("Id", job_definition_id)
            
        # Use cached schedule response if provided, otherwise fetch it
        if cached_schedule_response:
            describe_schedule_response = cached_schedule_response
            self.log.info(f"[SageMakerScheduler] Using cached schedule response for {job_definition_id}.")
        else:
            group_name = self.get_schedule_group_name()
            
            self.log.info(f"[SageMakerScheduler] Calling EventBridge Scheduler GetSchedule for {job_definition_id} in group {group_name}...")
            
            try:
                # Get EventBridge Schedule details
                describe_schedule_response = await self.event_bridge_client().get_schedule(
                    name=job_definition_id,
                    group_name=group_name
                )
                
            except Exception as error:
                self.handle_aws_client_error(
                    error,
                    f"Error when calling EventBridge Scheduler GetSchedule for {job_definition_id}: {error}",
                )

            self.log.info(
                f"[SageMakerScheduler] Successfully called EventBridge Scheduler GetSchedule for {job_definition_id}."
            )

        # Extract training job details and tags from EventBridge target if not provided
        if not list_tags_response:
            target = describe_schedule_response.get("Target", {})
            if target.get("Input"):
                try:
                    training_job_input = json.loads(target["Input"])
                    if training_job_input.get("Tags"):
                        list_tags_response = {"Tags": training_job_input["Tags"]}
                        self.log.info(f"[SageMakerScheduler] Successfully extracted tags from EventBridge target training job details.")
                    else:
                        list_tags_response = {"Tags": []}
                        self.log.info(f"[SageMakerScheduler] No tags found in EventBridge target training job input.")
                except json.JSONDecodeError as error:
                    self.log.error(f"[SageMakerScheduler] Failed to parse training job input from EventBridge target: {error}")
                    list_tags_response = {"Tags": []}
            else:
                self.log.warning(f"[SageMakerScheduler] No training job input found in EventBridge target for schedule {job_definition_id}")
                list_tags_response = {"Tags": []}

        return self.converter.to_jupyter_describe_job_definition_from_schedule_output(
            job_definition_id=job_definition_id,
            describe_schedule_response=describe_schedule_response,
            list_tags_response=list_tags_response,
        )

    @async_with_metrics("ListJobDefinition")
    async def list_job_definitions(
        self, query: ListJobDefinitionsQuery, metrics: MetricsContext
    ) -> ListJobDefinitionsResponse:
        """Returns list of all job definitions filtered by query using DataZone assets and EventBridge schedules
        
        Optimized version that eliminates duplicate get_schedule API calls by:
        1. Batch fetching all schedule details in parallel
        2. Using cached schedule data when calling get_job_definition
        3. Reducing overall API calls and improving performance
        """

        # Get environment configuration for DataZone search
        env_config = load_env()
        domain_id = safe_env_get(env_config, "domain_id", "unknown")
        project_id = safe_env_get(env_config, "project_id", "unknown")
        user_id = safe_env_get(env_config, "user_id", "unknown")

        self.log.info("[SageMakerScheduler] Searching DataZone assets for notebook schedules...")

        # Search DataZone for notebook-type schedule assets
        search_text = "notebook"  # Search for artifacts with artifactType = "notebook"
        search_attribute = 'artifactType'

        # Build custom form name based on project
        custom_schedule_form_name = f"{SAGEMAKER_SCHEDULE_FORM_TYPE_NAME}_{project_id}"

        search_params = {
            "domainIdentifier": domain_id,
            "owningProjectIdentifier": project_id,
            "searchScope": "ASSET",
            "additionalAttributes": ["FORMS", "TIME_SERIES_DATA_POINT_FORMS"],
            "searchText": search_text,
            "searchIn": [
                {
                    "attribute": f"{custom_schedule_form_name}.{search_attribute}"
                },
                {
                    "attribute": f"{SAGEMAKER_SCHEDULE_FORM_NAME}.{search_attribute}"
                }
            ],
            "maxResults": min(query.max_items or 50, 50),
        }

        # Apply name filter if provided - search by schedule name
        if query.name:
            search_params["searchText"] = f'"{query.name}"'
            search_params["searchIn"] = [
                {
                    "attribute": f"{custom_schedule_form_name}.scheduleName"
                },
                {
                    "attribute": f"{SAGEMAKER_SCHEDULE_FORM_NAME}_{project_id}.scheduleName"
                }
            ]

        try:
            search_response = await self.datazone_client().search(search_params)
        except Exception as error:
            self.handle_aws_client_error(
                error, f"Error when searching DataZone assets: {error}"
            )

        self.log.info(f"[SageMakerScheduler] Found {len(search_response.get('items', []))} schedule assets from DataZone.")

        # Extract schedule names from DataZone assets
        schedule_names = []
        asset_items = search_response.get("items", [])

        for item in asset_items:
            asset_item = item.get("assetItem")
            if not asset_item:
                continue

            # Verify this is a schedule asset by checking type identifier - support both managed and custom forms
            type_identifier = asset_item.get("typeIdentifier", "")
            is_custom_asset = type_identifier.startswith(f"{SAGEMAKER_SCHEDULE_ASSET_TYPE}_{project_id}")
            is_managed_asset = type_identifier.startswith(f"amazon.datazone.{SAGEMAKER_SCHEDULE_ASSET_TYPE}")
            
            if not (is_custom_asset or is_managed_asset):
                continue

            # Get schedule name from the asset
            schedule_name = asset_item.get("name")
            if schedule_name:
                schedule_names.append(schedule_name)

        self.log.info(f"[SageMakerScheduler] Extracted {len(schedule_names)} schedule names from DataZone assets.")

        if not schedule_names:
            self.log.info("[SageMakerScheduler] No schedule names found, returning empty response.")
            return ListJobDefinitionsResponse(
                job_definitions=[],
                next_token=search_response.get("nextToken"),
                total_count=0,
            )

        # PERFORMANCE OPTIMIZATION: Batch fetch all schedule details in parallel
        self.log.info(f"[SageMakerScheduler] Batch fetching schedule details for {len(schedule_names)} schedules...")
        schedule_details_cache = await self._get_schedule_details_batch(schedule_names)
        
        # Filter valid job definitions using cached schedule data
        valid_job_definitions_data = []

        for schedule_name in schedule_names:
            describe_schedule_response = schedule_details_cache.get(schedule_name)
            
            if not describe_schedule_response:
                self.log.warning(f"[SageMakerScheduler] No schedule details found for {schedule_name}")
                continue

            # Parse target input to check for job-definition-id tag
            target = describe_schedule_response.get("Target", {})
            if target.get("Input"):
                try:
                    training_job_input = json.loads(target["Input"])
                    tags = training_job_input.get("Tags", [])

                    # Check if this schedule has the job-definition-id tag (indicates it's a recurring job definition)
                    has_job_definition_tag = any(
                        tag.get("Key") == JobTag.JOB_DEFINITION_ID.value 
                        for tag in tags
                    )

                    belong_to_current_user = any(
                        tag.get("Key") == JobTag.SMUS_USER_ID.value and tag.get("Value") == user_id 
                        for tag in tags
                    )

                    if has_job_definition_tag and belong_to_current_user:
                        valid_job_definitions_data.append({
                            'schedule_name': schedule_name,
                            'schedule_response': describe_schedule_response
                        })
                        self.log.debug(f"[SageMakerScheduler] Schedule {schedule_name} identified as job definition.")
                    else:
                        self.log.debug(f"[SageMakerScheduler] Schedule {schedule_name} is not a job definition (no job-definition-id tag).")

                except json.JSONDecodeError as parse_error:
                    self.log.warning(f"[SageMakerScheduler] Failed to parse EventBridge target input for schedule {schedule_name}: {parse_error}")
                    continue
            else:
                self.log.warning(f"[SageMakerScheduler] No target input found for schedule {schedule_name}")
                continue

        self.log.info(f"[SageMakerScheduler] Found {len(valid_job_definitions_data)} valid job definitions.")

        if not valid_job_definitions_data:
            return ListJobDefinitionsResponse(
                job_definitions=[],
                next_token=search_response.get("nextToken"),
                total_count=0,
            )

        # PERFORMANCE OPTIMIZATION: Use cached schedule data when calling get_job_definition
        async def get_job_definition_with_cache(job_def_data):
            return await self.get_job_definition(
                job_definition_id=job_def_data['schedule_name'],
                cached_schedule_response=job_def_data['schedule_response']
            )

        # Get job definition details in parallel using cached data
        self.log.info(f"[SageMakerScheduler] Processing {len(valid_job_definitions_data)} job definitions in parallel...")
        job_definition_results = await asyncio.gather(
            *[get_job_definition_with_cache(job_def_data) for job_def_data in valid_job_definitions_data],
            return_exceptions=True,
        )

        successful_job_definitions: List[DescribeJobDefinition] = []

        for idx, describe_job_definition in enumerate(job_definition_results):
            if isinstance(describe_job_definition, DescribeJobDefinition):
                successful_job_definitions.append(describe_job_definition)
            else:
                schedule_name = valid_job_definitions_data[idx]['schedule_name']
                self.log.error(
                    f"[SageMakerScheduler] Error when getting job definition for schedule {schedule_name}: {describe_job_definition}"
                )

        self.log.info(f"[SageMakerScheduler] Successfully retrieved {len(successful_job_definitions)} job definitions.")

        return ListJobDefinitionsResponse(
            job_definitions=successful_job_definitions,
            next_token=search_response.get("nextToken"),  # Use DataZone's next token
            total_count=-1,
        )

    async def get_staging_paths(
        self, model: Union[DescribeJob, DescribeJobDefinition]
    ) -> Dict[str, str]:
        """Returns full staging paths for all job files

        Notes
        -----
        Any path supported by `fsspec https://filesystem-spec.readthedocs.io/en/latest/index.html`_
        is a valid return value. For staging files that
        are stored as tar or compressed tar archives, this
        should specify the first entry with a key as `tar`
        or `tar.gz` and value as path to the archive file;
        the values for the actual format files will be just
        the path to them in the archive, in most cases just
        the filename. For input files, the key 'input' is
        expected.


        Examples
        --------
        >>> self.get_staging_paths(1)
        {
            'ipynb': '/job_files/helloworld-2022-10-10.ipynb',
            'html': '/job_files/helloworld-2022-10-10.html',
            'input': '/job_files/helloworld.ipynb',
            'files': ["abc.txt", "def.csv"]
        }

        For files that are archived as tar or compressed tar
        >>> self.get_staging_paths(2)
        {
            'tar.gz': '/job_files/helloworld.tar.gz',
            'ipynb': 'helloworld-2022-10-10.ipynb',
            'html': 'helloworld-2022-10-10.html',
            'input': 'helloworld.ipynb',
            'files': ["abc.txt", "def.csv"]
        }

        Parameters
        ----------
        job_id : str
            Unique identifier for the job

        Returns
        -------
        Dictionary with keys as output format and values
        as full path to the job file in staging location.
        """

        if should_use_jupyter_scheduler(model.job_id):
            try:
                self.log.info(f"[SageMakerScheduler] get_staging_paths: Job ID {model.job_id} is UUID format, delegating to jupyter scheduler")
                return self.jupyter_scheduler.get_staging_paths(model)
            except Exception as error:
                self.log.error(f"[SageMakerScheduler] get_staging_paths: Error delegating to jupyter scheduler: {error}")
                # Continue with SageMaker logic
                raise error

        if not isinstance(model, DescribeJob):
            raise NotImplementedError("Cannot get staging paths for a job definition")

        training_job_response = await self.sagemaker_client().describe_training_job(
            job_name=model.job_id
        )

        original_output_file_name = (
            training_job_response.get("Environment", {})
            .get(JobEnvironmentVariableName.SM_OUTPUT_NOTEBOOK_NAME.value)
            .replace("Z-.ipynb", "Z.ipynb")
            .replace(":", "-")
        )

        # From: hello-7-Hello-2022-10-24T18:59:43.851Z-.ipynb
        #   To: hello-7-Hello-2022-10-24T18-59-43-851Z.ipynb
        output_filename_parts = os.path.splitext(original_output_file_name)

        files = []
        if model.package_input_folder and model.packaged_files:
            files = model.packaged_files

        # Define all known output formats, then remove unavailable ones depending on the job status.
        output_mapping = {
            "tar.gz": os.path.join(
                model.runtime_environment_parameters[
                    str(RuntimeEnvironmentParameterName.S3_OUTPUT)
                ],
                model.job_id,
                "output",
                "output.tar.gz",
            ),
            "input": model.input_filename,
            "ipynb": (
                output_filename_parts[0].rstrip("-").replace(".", "-")
                + output_filename_parts[1]
            ),
            "log": "sagemaker_job_execution.log",
            "files": files
        }

        if model.status == Status.COMPLETED:
            # When we expand to more output formats, this should be updated to respect model.output_formats.
            self.log.info(f"[SageMakerScheduler] get_staging_paths returned with status completed, output_mapping is {output_mapping}")
            return output_mapping

        (
            available_output_formats,
            _,
        ) = self.converter.determine_available_output_formats_and_failure_reason(
            model.status, training_job_response.get("FailureReason")
        )

        if not available_output_formats:
            # Allow the user to download only the original input file.
            output_mapping = {
                "input": os.path.join(
                    model.runtime_environment_parameters[
                        str(RuntimeEnvironmentParameterName.S3_INPUT)
                    ].rstrip("/input"),
                    model.job_id,
                    "input",
                    model.input_filename,
                ),
            }

            self.log.info(f"[SageMakerScheduler] get_staging_paths returned no available_output_formats, output_mapping is {output_mapping}")
            return output_mapping

        available_output_formats.append("tar.gz")

        # Remove unavailable output formats.
        for output_format in [*output_mapping.keys()]:
            if output_format not in available_output_formats:
                output_mapping.pop(output_format, None)

        self.log.info(f"[SageMakerScheduler] get_staging_paths returned fallback, output_mapping is {output_mapping}")
        return output_mapping

    @async_with_metrics("GetScheduleGroup")
    async def get_schedule_group(self) -> Dict:
        """Get schedule group details by name"""
        if not self.event_bridge_client():
            raise SchedulerError('EventBridge client not initialized')

        name = self.get_schedule_group_name()
        self.log.info(f"[SageMakerScheduler] Calling EventBridge Scheduler GetScheduleGroup for {name}...")
        
        try:
            response = await self.event_bridge_client().get_schedule_group(name=name)
        except Exception as error:
            self.handle_aws_client_error(
                error,
                f"Error when calling EventBridge Scheduler GetScheduleGroup for {name}: {error}",
            )
        
        # Extract Name from response and validate it exists
        schedule_group_name = response.get("Name")
        if not schedule_group_name:
            raise SchedulerError('Schedule group not found')
        
        self.log.info(f"[SageMakerScheduler] Successfully called EventBridge Scheduler GetScheduleGroup for {name}.")
        return {"scheduleGroupName": schedule_group_name}
