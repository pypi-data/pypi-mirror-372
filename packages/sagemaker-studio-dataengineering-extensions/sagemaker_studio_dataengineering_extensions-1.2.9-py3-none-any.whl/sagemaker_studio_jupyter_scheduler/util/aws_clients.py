import asyncio
import logging
import os
from typing import Dict, List, Optional
import botocore
import boto3
from sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter import (
    InternalMetadataAdapter,
)
from aiobotocore.session import get_session, AioSession

from sagemaker_studio_jupyter_scheduler.util.app_metadata import (
    get_partition,
    get_region_name,
)

from sagemaker_studio_jupyter_scheduler.util.constants import USE_DUALSTACK_ENDPOINT
from sagemaker_studio_jupyter_scheduler.util.utils import safe_env_get, load_env

LOOSELEAF_STAGE_MAPPING = {"devo": "beta", "loadtest": "gamma"}

from sagemaker_studio_jupyter_scheduler.util.constants import IAM_TIMEOUT

# Profile name constant for EventBridge client
DOMAIN_EXECUTION_ROLE_CREDS = "DomainExecutionRoleCreds"


class BaseAsyncBotoClient:
    cfg: any
    partition: str
    region_name: str
    sess: AioSession
    profile_name: str

    def __init__(self, partition: str, region_name: str, profile_name: str = None):
        self.cfg = botocore.client.Config(
            # TODO: Refine these values (currently copied from LooseLeafNb2Kg)
            connect_timeout=10,
            read_timeout=20,
            retries={"max_attempts": 2},
            use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT
        )
        self.partition = partition
        self.region_name = region_name
        self.profile_name = profile_name
        self.sess = get_session()

    def _add_profile_credentials(self, create_client_args: Dict) -> None:
        """Add profile credentials to client creation arguments"""
        # Safety check: verify profile exists before using it
        try:
            session = None
            available_profiles = boto3.Session().available_profiles
            if self.profile_name and self.profile_name in available_profiles:
                session = boto3.Session(profile_name=self.profile_name)
            else:
                logging.warning(f"Profile '{self.profile_name}' not found in available profiles. Using default credentials.")
                session = boto3.Session()
            credentials = session.get_credentials() if session else None
            if credentials:
                create_client_args["aws_access_key_id"] = credentials.access_key
                create_client_args["aws_secret_access_key"] = credentials.secret_key
                create_client_args["aws_session_token"] = credentials.token
        except Exception as e:
            logging.warning(f"Error checking profile '{self.profile_name}': {e}. Using default credentials.")
        # If no profile_name provided or profile doesn't exist, use default credentials (no additional args needed)


class SageMakerAsyncBoto3Client(BaseAsyncBotoClient):
    def _create_sagemaker_client(self):
        # based on the Studio domain stage, we want to choose the sagemaker endpoint
        # rest of the services will use prod stages for non prod stages
        stage = InternalMetadataAdapter().get_stage()
        self.cfg = botocore.client.Config(
            connect_timeout=3,
            read_timeout=15,
            retries={"max_attempts": 2},
            use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT
        )
        create_client_args = {
            "service_name": "sagemaker",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        
        # Add profile credentials
        self._add_profile_credentials(create_client_args)
        
        return self.sess.create_client(**create_client_args)

    async def describe_training_job(self, job_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_training_job(TrainingJobName=job_name)

    async def create_training_job(self, input: Dict) -> Dict:
        try:
            async with self._create_sagemaker_client() as sm:
                return await sm.create_training_job(**input)
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def list_tags(self, resource_arn: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.list_tags(ResourceArn=resource_arn)

    async def list_training_jobs(
        self,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        name_contains: Optional[str] = None,
        creation_time_after: Optional[str] = None,
        creation_time_before: Optional[str] = None,
        last_modified_time_after: Optional[str] = None,
        last_modified_time_before: Optional[str] = None,
        status_equals: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict:
        """
        List training jobs with optional filtering and sorting parameters.
        
        Parameters:
        - sort_by: The field to sort by ('Name', 'CreationTime', 'Status')
        - sort_order: Sort order ('Ascending' or 'Descending')
        - name_contains: Filter by training job name containing this string
        - creation_time_after: Filter jobs created after this timestamp
        - creation_time_before: Filter jobs created before this timestamp
        - last_modified_time_after: Filter jobs modified after this timestamp
        - last_modified_time_before: Filter jobs modified before this timestamp
        - status_equals: Filter by training job status
        - max_results: Maximum number of results to return (1-100)
        - next_token: Pagination token for retrieving additional results
        
        Returns:
        Dictionary containing TrainingJobSummaries and NextToken (if applicable)
        """
        try:
            async with self._create_sagemaker_client() as sm:
                # Build the request parameters dictionary
                request_params = {}
                
                if sort_by is not None:
                    request_params["SortBy"] = sort_by
                if sort_order is not None:
                    request_params["SortOrder"] = sort_order
                if name_contains is not None:
                    request_params["NameContains"] = name_contains
                if creation_time_after is not None:
                    request_params["CreationTimeAfter"] = creation_time_after
                if creation_time_before is not None:
                    request_params["CreationTimeBefore"] = creation_time_before
                if last_modified_time_after is not None:
                    request_params["LastModifiedTimeAfter"] = last_modified_time_after
                if last_modified_time_before is not None:
                    request_params["LastModifiedTimeBefore"] = last_modified_time_before
                if status_equals is not None:
                    request_params["StatusEquals"] = status_equals
                if max_results is not None:
                    request_params["MaxResults"] = max_results
                if next_token is not None:
                    request_params["NextToken"] = next_token
                
                return await sm.list_training_jobs(**request_params)
                
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def search(self, input: Dict) -> Dict:
        try:
            async with self._create_sagemaker_client() as sm:
                return await sm.search(**input)
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def stop_training_job(self, training_job_name: str) -> Dict:
        try:
            async with self._create_sagemaker_client() as sm:
                return await sm.stop_training_job(TrainingJobName=training_job_name)
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def add_tags(self, resource_arn: str, tag_list: List[Dict]) -> Dict:
        try:
            async with self._create_sagemaker_client() as sm:
                return await sm.add_tags(ResourceArn=resource_arn, Tags=tag_list)
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def delete_tags(self, resource_arn: str, tag_keys: List[str]):
        try:
            async with self._create_sagemaker_client() as sm:
                return await sm.delete_tags(ResourceArn=resource_arn, TagKeys=tag_keys)
        except botocore.exceptions.ClientError as error:
            # TODO: Logger?
            print(f"Received ClientError: {str(error)}")
            # TODO: better error handling
            raise error

    async def describe_lcc(self, lcc_arn: str):
        lcc_name = lcc_arn.split("studio-lifecycle-config/")[-1]

        async with self._create_sagemaker_client() as sm:
            return await sm.describe_studio_lifecycle_config(
                StudioLifecycleConfigName=lcc_name
            )

    async def list_domains(self):
        async with self._create_sagemaker_client() as sm:
            return await sm.list_domains()

    async def describe_domain(self, domain_id: str) -> Dict:
        if domain_id is None:
            return {}
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_domain(DomainId=domain_id)

    async def describe_user_profile(
        self, domain_id: str, user_profile_name: str
    ) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_user_profile(
                DomainId=domain_id, UserProfileName=user_profile_name
            )

    async def describe_space(self, domain_id: str, space_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_space(DomainId=domain_id, SpaceName=space_name)

    async def describe_app(self, domain_id: str, space_name: str, app_type: str, app_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_app(DomainId=domain_id, SpaceName=space_name, AppType=app_type, AppName=app_name)

    async def create_pipeline(
        self,
        pipeline_name: str,
        pipeline_display_name: str,
        pipeline_description: str,
        pipeline_definition: str,
        role_arn: str,
        tags: List[Dict],
    ) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.create_pipeline(
                PipelineName=pipeline_name,
                PipelineDisplayName=pipeline_display_name,
                PipelineDescription=pipeline_description,
                PipelineDefinition=pipeline_definition,
                RoleArn=role_arn,
                Tags=tags,
            )

    async def update_pipeline(
        self,
        pipeline_name: str,
        pipeline_display_name: str,
        pipeline_description: str,
        pipeline_definition: str,
        role_arn: str,
    ) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.update_pipeline(
                PipelineName=pipeline_name,
                PipelineDisplayName=pipeline_display_name,
                PipelineDescription=pipeline_description,
                PipelineDefinition=pipeline_definition,
                RoleArn=role_arn,
            )

    async def describe_pipeline(self, pipeline_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_pipeline(
                PipelineName=pipeline_name,
            )

    async def list_pipeline_executions(self, pipeline_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            # TODO: use the next token to deal with pagination
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html#SageMaker.Client.get_paginator
            return await sm.list_pipeline_executions(
                PipelineName=pipeline_name,
            )

    async def delete_pipeline(self, pipeline_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.delete_pipeline(
                PipelineName=pipeline_name,
            )

    async def stop_pipeline_execution(self, pipeline_execution_arn: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.stop_pipeline_execution(
                PipelineExecutionArn=pipeline_execution_arn
            )

    async def describe_image(self, image_name: str) -> Dict:
         async with self._create_sagemaker_client() as sm:
            describe_image_version_args = {"ImageName": image_name}
            return await sm.describe_image(**describe_image_version_args)

    async def describe_image_version(
        self, image_name: str, image_version_number: int = None
    ) -> Dict:
        async with self._create_sagemaker_client() as sm:
            describe_image_version_args = {"ImageName": image_name}
            if image_version_number:
                describe_image_version_args["Version"] = image_version_number
            return await sm.describe_image_version(**describe_image_version_args)

    async def describe_app_image_config(self, app_image_config_name: str) -> Dict:
        async with self._create_sagemaker_client() as sm:
            return await sm.describe_app_image_config(
                AppImageConfigName=app_image_config_name
            )


def get_sagemaker_client() -> SageMakerAsyncBoto3Client:
    return SageMakerAsyncBoto3Client(get_partition(), get_region_name())


class S3AsyncBoto3Client(BaseAsyncBotoClient):
    def __init__(self, partition: str, region_name: str, profile_name: str = None):
        super().__init__(partition, region_name, profile_name)
        self.cfg = botocore.client.Config(
            # TODO: Refine these values (currently copied from LooseLeafNb2Kg)
            connect_timeout=15,
            read_timeout=15,
            retries={"max_attempts": 2},
            use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT
        )

    def _create_s3_client(self):
        create_client_args = {
            "service_name": "s3",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        
        # Add profile credentials
        self._add_profile_credentials(create_client_args)
        
        return self.sess.create_client(**create_client_args)

    async def get_bucket_location(self, bucket: str, accountId: str):
        async with self._create_s3_client() as s3:
            return await s3.get_bucket_location(
                Bucket=bucket, ExpectedBucketOwner=accountId
            )

    async def upload_file(
        self, file_name: str, bucket: str, key: str, aws_account_id: str, encrypt: bool
    ):
        async with self._create_s3_client() as s3:
            with open(file_name, "rb") as f:
                args = {
                    "Body": f,
                    "Bucket": bucket,
                    "Key": key,
                    "ExpectedBucketOwner": aws_account_id,
                }

                if encrypt:
                    args["ServerSideEncryption"] = "aws:kms"

                await s3.put_object(**args)

    async def delete_object(self, bucket: str, key: str):
        async with self._create_s3_client() as s3:
            await s3.delete_object(Bucket=bucket, Key=key)

    async def get_object(self, bucket: str, key: str) -> Dict:
        async with self._create_s3_client() as s3:
            return await s3.get_object(Bucket=bucket, Key=key)

    async def get_object_content(self, bucket: str, key: str) -> str:
        async with self._create_s3_client() as s3:
            response = await s3.get_object(Bucket=bucket, Key=key)
            return await response["Body"].read()
        
    async def list_objects(self, bucket: str, prefix: str) -> List[str]:
        async with self._create_s3_client() as s3:
            paginator = s3.get_paginator('list_objects_v2')
            params = {'Bucket': bucket, 'Prefix': prefix}
            page_iterator = paginator.paginate(**params)

            list_s3_objects = []
            async for page in page_iterator:
                contents = page.get('Contents', [])
                for content in contents:
                    list_s3_objects.append(content.get("Key", ""))

            return list_s3_objects

    async def create_bucket(self, bucket_name: str, region_name: str):
        async with self._create_s3_client() as s3:
            if region_name == "us-east-1":
                # If your region is us-east-1 then you simply run the command without the --location constraint
                # because by default bucket is created in the us-east-1 region
                return await s3.create_bucket(
                    Bucket=bucket_name,
                )

            else:
                # TODO: consolidate the edge case
                return await s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region_name},
                )
            
    async def head_bucket(self, bucket_name: str):
        async with self._create_s3_client() as s3:
            return await s3.head_bucket(Bucket=bucket_name)

    async def enable_server_side_encryption_with_s3_keys(self, bucket_name: str):
        async with self._create_s3_client() as s3:
            await s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    "Rules": [
                        {
                            "ApplyServerSideEncryptionByDefault": {
                                "SSEAlgorithm": "aws:kms",
                            }
                        }
                    ]
                },
            )

    async def enable_versioning(self, bucket_name: str):
        async with self._create_s3_client() as s3:
            await s3.put_bucket_versioning(
                Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
            )

    async def get_bucket_encryption(self, bucket_name: str) -> Dict:
        async with self._create_s3_client() as s3:
            return await s3.get_bucket_encryption(Bucket=bucket_name)


def get_s3_client():
    return S3AsyncBoto3Client(get_partition(), get_region_name())


class EventBridgeAsyncBotoClient(BaseAsyncBotoClient):
    def __init__(self, partition: str, region_name: str, profile_name: str = None):
        super().__init__(partition, region_name, profile_name)

    def _create_event_bridge_client(self):
        create_client_args = {
            "service_name": "events",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        
        # Add profile credentials
        self._add_profile_credentials(create_client_args)
        
        return self.sess.create_client(**create_client_args)

    def _create_event_bridge_scheduler_client(self):
        create_client_args = {
            "service_name": "scheduler",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        
        # Add profile credentials
        self._add_profile_credentials(create_client_args)
        
        return self.sess.create_client(**create_client_args)

    async def put_rule(
        self,
        name: str,
        description: str,
        schedule_expression: str,
        state: str,
        tags: Optional[List[Dict]] = None,
    ) -> Dict:
        async with self._create_event_bridge_client() as eb:
            if tags is None:
                tags = []

            return await eb.put_rule(
                Name=name,
                Description=description,
                ScheduleExpression=schedule_expression,
                State=state,
                Tags=tags,
            )

    async def put_targets(self, rule_name: str, targets: List[Dict]) -> Dict:
        async with self._create_event_bridge_client() as eb:
            return await eb.put_targets(Rule=rule_name, Targets=targets)

    async def describe_rule(self, name: str) -> Dict:
        async with self._create_event_bridge_client() as eb:
            return await eb.describe_rule(Name=name)

    async def disable_rule(self, name: str) -> None:
        async with self._create_event_bridge_client() as eb:
            await eb.disable_rule(Name=name)

    async def enable_rule(self, name: str) -> None:
        async with self._create_event_bridge_client() as eb:
            await eb.enable_rule(Name=name)

    async def remove_targets(self, rule_name: str, ids: List[str]) -> None:
        async with self._create_event_bridge_client() as eb:
            await eb.remove_targets(Rule=rule_name, Ids=ids)

    async def delete_rule(self, name: str) -> None:
        async with self._create_event_bridge_client() as eb:
            await eb.delete_rule(Name=name)

    async def list_tags_for_resource(self, resource_arn: str) -> Dict:
        async with self._create_event_bridge_client() as eb:
            return await eb.list_tags_for_resource(ResourceARN=resource_arn)

    async def tag_resource(self, resource_arn: str, tag_list: List[Dict]):
        async with self._create_event_bridge_client() as eb:
            await eb.tag_resource(ResourceARN=resource_arn, Tags=tag_list)

    async def untag_resource(self, resource_arn: str, tag_keys: List[str]):
        async with self._create_event_bridge_client() as eb:
            await eb.untag_resource(ResourceARN=resource_arn, TagKeys=tag_keys)

    async def get_schedule_group(self, name: str) -> Dict:
        async with self._create_event_bridge_scheduler_client() as scheduler:
            return await scheduler.get_schedule_group(Name=name)

    async def create_schedule_group(
        self, 
        name: str, 
        tags: Optional[List[Dict]] = None
    ) -> Dict:
        async with self._create_event_bridge_scheduler_client() as scheduler:
            create_args = {"Name": name}
            if tags is not None:
                create_args["Tags"] = tags
            return await scheduler.create_schedule_group(**create_args)

    async def create_schedule(
        self,
        name: str,
        schedule_expression: str,
        target: Dict,
        flexible_time_window: Dict,
        group_name: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        kms_key_arn: Optional[str] = None,
        role_arn: Optional[str] = None,
        action_after_completion: Optional[str] = None,
    ) -> Dict:
        async with self._create_event_bridge_scheduler_client() as scheduler:
            create_args = {
                "Name": name,
                "ScheduleExpression": schedule_expression,
                "Target": target,
                "FlexibleTimeWindow": flexible_time_window,
            }
            
            if group_name is not None:
                create_args["GroupName"] = group_name
            if description is not None:
                create_args["Description"] = description
            if state is not None:
                create_args["State"] = state
            if start_date is not None:
                create_args["StartDate"] = start_date
            if end_date is not None:
                create_args["EndDate"] = end_date
            if kms_key_arn is not None:
                create_args["KmsKeyArn"] = kms_key_arn
            if role_arn is not None:
                create_args["RoleArn"] = role_arn
            if action_after_completion is not None:
                create_args["ActionAfterCompletion"] = action_after_completion
                
            return await scheduler.create_schedule(**create_args)

    async def get_schedule(self, name: str, group_name: Optional[str] = None) -> Dict:
        async with self._create_event_bridge_scheduler_client() as scheduler:
            get_args = {"Name": name}
            if group_name is not None:
                get_args["GroupName"] = group_name
            return await scheduler.get_schedule(**get_args)

    async def update_schedule(
        self,
        name: str,
        schedule_expression: str,
        target: Dict,
        flexible_time_window: Dict,
        group_name: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        kms_key_arn: Optional[str] = None,
        action_after_completion: Optional[str] = None,
    ) -> Dict:
        async with self._create_event_bridge_scheduler_client() as scheduler:
            update_args = {
                "Name": name,
                "ScheduleExpression": schedule_expression,
                "Target": target,
                "FlexibleTimeWindow": flexible_time_window,
            }
            
            if group_name is not None:
                update_args["GroupName"] = group_name
            if description is not None:
                update_args["Description"] = description
            if state is not None:
                update_args["State"] = state
            if start_date is not None:
                update_args["StartDate"] = start_date
            if end_date is not None:
                update_args["EndDate"] = end_date
            if kms_key_arn is not None:
                update_args["KmsKeyArn"] = kms_key_arn
            if action_after_completion is not None:
                update_args["ActionAfterCompletion"] = action_after_completion
                
            return await scheduler.update_schedule(**update_args)

    async def delete_schedule(self, name: str, group_name: Optional[str] = None) -> Dict:
        async with self._create_event_bridge_scheduler_client() as scheduler:
            delete_args = {"Name": name}
            if group_name is not None:
                delete_args["GroupName"] = group_name
            return await scheduler.delete_schedule(**delete_args)

    async def list_schedules(self, group_name: Optional[str] = None, name_prefix: Optional[str] = None, state: Optional[str] = None, max_results: Optional[int] = None, next_token: Optional[str] = None) -> Dict:
        async with self._create_event_bridge_scheduler_client() as scheduler:
            list_args = {}
            if group_name is not None:
                list_args["GroupName"] = group_name
            if name_prefix is not None:
                list_args["NamePrefix"] = name_prefix
            if state is not None:
                list_args["State"] = state
            if max_results is not None:
                list_args["MaxResults"] = max_results
            if next_token is not None:
                list_args["NextToken"] = next_token
            return await scheduler.list_schedules(**list_args)

    async def list_tags_for_resource(self, resource_arn: str) -> Dict:
        async with self._create_event_bridge_scheduler_client() as scheduler:
            return await scheduler.list_tags_for_resource(ResourceArn=resource_arn)

    async def tag_resource(self, resource_arn: str, tags: Dict[str, str]) -> Dict:
        async with self._create_event_bridge_scheduler_client() as scheduler:
            return await scheduler.tag_resource(ResourceArn=resource_arn, Tags=tags)

    async def untag_resource(self, resource_arn: str, tag_keys: List[str]) -> Dict:
        async with self._create_event_bridge_scheduler_client() as scheduler:
            return await scheduler.untag_resource(ResourceArn=resource_arn, TagKeys=tag_keys)


def get_event_bridge_client():
    return EventBridgeAsyncBotoClient(get_partition(), get_region_name())


class EC2AsyncBotoClient(BaseAsyncBotoClient):
    def _create_ec2_client(self):
        create_client_args = {
            "service_name": "ec2",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        
        # Add profile credentials
        self._add_profile_credentials(create_client_args)
        
        return self.sess.create_client(**create_client_args)

    async def list_security_groups_by_vpc_id(self, vpc_id: str):
        async with self._create_ec2_client() as ec2:
            return await ec2.describe_security_groups(
                Filters=[
                    {
                        "Name": "vpc-id",
                        "Values": [vpc_id],
                    },
                ]
            )

    async def list_subnets_by_vpc_id(self, vpc_id: str):
        async with self._create_ec2_client() as ec2:
            return await ec2.describe_subnets(
                Filters=[
                    {
                        "Name": "vpc-id",
                        "Values": [vpc_id],
                    },
                ]
            )

    async def list_routetable_by_vpc_id(self, vpc_id: str):
        async with self._create_ec2_client() as ec2:
            return await ec2.describe_route_tables(
                Filters=[
                    {
                        "Name": "vpc-id",
                        "Values": [vpc_id],
                    },
                ]
            )


def get_ec2_client():
    return EC2AsyncBotoClient(get_partition(), get_region_name())


class STSAsyncBotoClient(BaseAsyncBotoClient):
    def _create_sts_client(self):
        session = botocore.session.Session()
        endpoint_resolver = session.get_component('endpoint_resolver')
        endpoint_data = endpoint_resolver.construct_endpoint('sts', self.region_name, use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT)

        # Use the resolved endpoint if available; otherwise, default to global STS endpoint.
        endpoint_url = "https://sts.amazonaws.com"
        # Use dual stack STS global endpoint if dual stack is enabled otherwise use legacy global STS endpoint.
        # https://docs.aws.amazon.com/general/latest/gr/sts.html
        if USE_DUALSTACK_ENDPOINT:
            endpoint_url = "https://sts.api.aws.com"

        if endpoint_data and 'hostname' in endpoint_data:
            resolved_url = endpoint_data['hostname']
            if not resolved_url.startswith("https://"):
                resolved_url = "https://" + resolved_url
            endpoint_url = resolved_url

        create_client_args = {
            "service_name": "sts",
            "config": self.cfg,
            "region_name": self.region_name,
            "endpoint_url": endpoint_url
        }
        
        # Add profile credentials
        self._add_profile_credentials(create_client_args)
        
        return self.sess.create_client(**create_client_args)

    # Used to get AWS account id
    # This API does not require special IAM permissions
    async def get_caller_identity(self) -> Dict:
        async with self._create_sts_client() as sts:
            return await sts.get_caller_identity()


def get_sts_client():
    return STSAsyncBotoClient(get_partition(), get_region_name())


class IAMAsyncBotoClient(BaseAsyncBotoClient):
    def _create_iam_client(self):
        create_client_args = {
            "service_name": "iam",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        
        # Add profile credentials
        self._add_profile_credentials(create_client_args)
        
        return self.sess.create_client(**create_client_args)

    # Used to get AWS account id
    # This API does not require special IAM permissions
    async def list_entities_for_policy(self, policy_arn, max_items=None) -> Dict:
        async with self._create_iam_client() as iam:
            return await iam.list_entities_for_policy(
                PolicyArn=policy_arn,
                EntityFilter="Role",
                MaxItems=max_items,
            )

    async def list_role_arns_with_matching_prefix(self, prefix: str) -> List[str]:
        matching_role_arns = []
        async with self._create_iam_client() as iam:
            paginator = iam.get_paginator("list_roles")
            async for page in paginator.paginate():
                for role in page["Roles"]:
                    if role["RoleName"].startswith(prefix):
                        matching_role_arns.append(role["Arn"])
        return matching_role_arns

    async def list_role_arns_with_matching_prefix_timeout_wrapper(
        self, prefix: str, logger
    ) -> List[str]:
        try:
            return await asyncio.wait_for(
                self.list_role_arns_with_matching_prefix(prefix), timeout=IAM_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.info("IAM call timed out, returning empty response")
            return []

    async def get_role_arn_by_role_name(
        self, role_name: str
    ) -> str:
        async with self._create_iam_client() as iam:
            role = await iam.get_role(RoleName=role_name)
            return role["Role"]["Arn"]

def get_iam_client():
    return IAMAsyncBotoClient(get_partition(), get_region_name())


class DataZoneAsyncBotoClient(BaseAsyncBotoClient):
    def __init__(self, partition: str, region_name: str, profile_name: str = DOMAIN_EXECUTION_ROLE_CREDS):
        super().__init__(partition, region_name, profile_name)

    def _create_datazone_client(self):
        create_client_args = {
            "service_name": "datazone",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        
        # Add profile credentials
        self._add_profile_credentials(create_client_args)
        
        # Load environment configuration to get datazone endpoint
        try:
            env_config = load_env()
            datazone_endpoint = safe_env_get(env_config, "dz_endpoint", "")
            if datazone_endpoint:
                create_client_args["endpoint_url"] = datazone_endpoint
        except Exception as e:
            # Log the error but don't fail - continue with default endpoint
            logging.warning(f"Failed to load datazone endpoint from environment: {e}")
        
        return self.sess.create_client(**create_client_args)

    async def list_domains(self) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.list_domains()

    async def get_domain(self, identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.get_domain(identifier=identifier)

    async def create_domain(self, domain_execution_role: str, name: str, **kwargs) -> Dict:
        async with self._create_datazone_client() as datazone:
            create_args = {
                "domainExecutionRole": domain_execution_role,
                "name": name
            }
            create_args.update(kwargs)
            return await datazone.create_domain(**create_args)

    async def delete_domain(self, identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.delete_domain(identifier=identifier)

    async def list_projects(self, domain_identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.list_projects(domainIdentifier=domain_identifier)

    async def get_project(self, domain_identifier: str, identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.get_project(
                domainIdentifier=domain_identifier,
                identifier=identifier
            )

    async def create_project(self, domain_identifier: str, name: str, **kwargs) -> Dict:
        async with self._create_datazone_client() as datazone:
            create_args = {
                "domainIdentifier": domain_identifier,
                "name": name
            }
            create_args.update(kwargs)
            return await datazone.create_project(**create_args)

    async def delete_project(self, domain_identifier: str, identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.delete_project(
                domainIdentifier=domain_identifier,
                identifier=identifier
            )

    async def list_environments(self, domain_identifier: str, project_identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.list_environments(
                domainIdentifier=domain_identifier,
                projectIdentifier=project_identifier
            )

    async def get_environment(self, domain_identifier: str, identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.get_environment(
                domainIdentifier=domain_identifier,
                identifier=identifier
            )

    async def create_environment(
        self, 
        domain_identifier: str, 
        environment_profile_identifier: str,
        name: str,
        project_identifier: str,
        **kwargs
    ) -> Dict:
        async with self._create_datazone_client() as datazone:
            create_args = {
                "domainIdentifier": domain_identifier,
                "environmentProfileIdentifier": environment_profile_identifier,
                "name": name,
                "projectIdentifier": project_identifier
            }
            create_args.update(kwargs)
            return await datazone.create_environment(**create_args)

    async def delete_environment(self, domain_identifier: str, identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.delete_environment(
                domainIdentifier=domain_identifier,
                identifier=identifier
            )

    async def list_data_sources(self, domain_identifier: str, project_identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.list_data_sources(
                domainIdentifier=domain_identifier,
                projectIdentifier=project_identifier
            )

    async def get_data_source(self, domain_identifier: str, identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.get_data_source(
                domainIdentifier=domain_identifier,
                identifier=identifier
            )

    async def create_data_source(
        self,
        domain_identifier: str,
        environment_identifier: str,
        name: str,
        project_identifier: str,
        type: str,
        **kwargs
    ) -> Dict:
        async with self._create_datazone_client() as datazone:
            create_args = {
                "domainIdentifier": domain_identifier,
                "environmentIdentifier": environment_identifier,
                "name": name,
                "projectIdentifier": project_identifier,
                "type": type
            }
            create_args.update(kwargs)
            return await datazone.create_data_source(**create_args)

    async def delete_data_source(self, domain_identifier: str, identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.delete_data_source(
                domainIdentifier=domain_identifier,
                identifier=identifier
            )

    async def get_project_profile(self, domain_identifier: str, identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.get_project_profile(
                domainIdentifier=domain_identifier,
                identifier=identifier
            )

    async def list_environment_profiles(self, domain_identifier: str, **kwargs) -> Dict:
        async with self._create_datazone_client() as datazone:
            list_args = {"domainIdentifier": domain_identifier}
            list_args.update(kwargs)
            return await datazone.list_environment_profiles(**list_args)

    async def get_environment_blueprint(self, domain_identifier: str, identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.get_environment_blueprint(
                domainIdentifier=domain_identifier,
                identifier=identifier
            )

    async def list_environment_blueprint_configurations(self, domain_identifier: str, environment_blueprint_identifier: str) -> Dict:
        async with self._create_datazone_client() as datazone:
            return await datazone.list_environment_blueprint_configurations(
                domainIdentifier=domain_identifier,
                environmentBlueprintIdentifier=environment_blueprint_identifier
            )

    async def create_asset(self, create_asset_request: Dict) -> Dict:
        """
        Create a DataZone asset using the standard AWS boto3 API
        
        Parameters:
        - create_asset_request: Dictionary containing the asset creation parameters
          Expected keys: domainIdentifier, owningProjectIdentifier, name, description, 
          formsInput, typeIdentifier, and other optional parameters
        
        Returns:
        Dictionary containing the created asset response
        """
        async with self._create_datazone_client() as datazone:
            return await datazone.create_asset(**create_asset_request)

    async def search(self, search_request: Dict) -> Dict:
        """
        Search for DataZone assets using the standard AWS boto3 API
        
        Parameters:
        - search_request: Dictionary containing the search parameters
          Expected keys: domainIdentifier, searchScope, searchText, searchIn, 
          additionalAttributes, and other optional parameters
        
        Returns:
        Dictionary containing the search results
        """
        async with self._create_datazone_client() as datazone:
            return await datazone.search(**search_request)

    async def delete_asset(self, domain_identifier: str, identifier: str) -> Dict:
        """
        Delete a DataZone asset using the standard AWS boto3 API
        
        Parameters:
        - domain_identifier: The domain identifier
        - identifier: The asset identifier
        
        Returns:
        Dictionary containing the delete response
        """
        async with self._create_datazone_client() as datazone:
            return await datazone.delete_asset(
                domainIdentifier=domain_identifier,
                identifier=identifier
            )

    async def update_asset(self, update_asset_request: Dict) -> Dict:
        """
        Update a DataZone asset by creating a new asset revision using the standard AWS boto3 API
        
        Parameters:
        - update_asset_request: Dictionary containing the asset update parameters
          Expected keys: domainIdentifier, identifier, name (optional), description (optional), 
          formsInput (optional), typeIdentifier (optional), and other optional parameters
        
        Returns:
        Dictionary containing the updated asset response
        """
        async with self._create_datazone_client() as datazone:
            return await datazone.create_asset_revision(**update_asset_request)

    async def get_asset_type(self, domain_identifier: str, identifier: str) -> Dict:
        """
        Get a DataZone asset type using the standard AWS boto3 API
        
        Parameters:
        - domain_identifier: The domain identifier
        - identifier: The asset type identifier
        
        Returns:
        Dictionary containing the asset type details
        """
        async with self._create_datazone_client() as datazone:
            return await datazone.get_asset_type(
                domainIdentifier=domain_identifier,
                identifier=identifier
            )


def get_datazone_client():
    return DataZoneAsyncBotoClient(get_partition(), get_region_name())
