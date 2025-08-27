import asyncio
import botocore.exceptions

from typing import List
from aws_embedded_metrics.logger.metrics_context import MetricsContext

from sagemaker_studio_jupyter_scheduler.extension.advanced_environments.base_advanced_environments import (
    BaseAdvancedEnvironments,
)
from sagemaker_studio_jupyter_scheduler.util.app_metadata import (
    get_region_name,
    get_domain_id,
    get_user_profile_name,
    get_shared_space_name,
    get_sagemaker_environment,

)
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironment,
)
from sagemaker_studio_jupyter_scheduler.util.aws_config import get_aws_account_id
from sagemaker_studio_jupyter_scheduler.util.aws_clients import (
    get_ec2_client,
    get_sagemaker_client,
    get_s3_client,
)
from sagemaker_studio_jupyter_scheduler.logging import async_with_metrics
from sagemaker_studio_jupyter_scheduler.model.models import (
    AdvancedEnvironment,
    AdvancedEnvironmentResponse,
)

ERROR_CODE = "404"
BUCKET_NOT_EXISTED_MSG = "Not Found"

class SageMakerStudioAdvancedEnvironments(BaseAdvancedEnvironments):
    SAGEMAKER_DEFAULT_S3_PREFIX = "sagemaker-automated-execution"

    def _get_lcc_arns(self, domain_default_user_settings, user_settings, space_settings):
        # Returning all the lcc arns that are related to this user both from Domain Default settings and User Profile level
        domain_default_lcc_arns = []
        user_lcc_arns = []
        space_lcc_arns = []

        if get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB:
            space_lcc_arns = space_settings.get("JupyterLabAppSettings", {}).get(
                "LifecycleConfigArns", []
            )
            user_lcc_arns = user_lcc_arns = user_settings.get("JupyterLabAppSettings", {}).get(
                "LifecycleConfigArns", []
            )
            domain_default_lcc_arns = domain_default_user_settings.get(
                "JupyterLabAppSettings", {}
            ).get("LifecycleConfigArns", [])
        else:
            space_lcc_arns = space_settings.get("JupyterServerAppSettings", {}).get(
                "LifecycleConfigArns", []
            ) + space_settings.get("KernelGatewayAppSettings", {}).get(
                "LifecycleConfigArns", []
            )

            user_lcc_arns = user_settings.get("JupyterServerAppSettings", {}).get(
                "LifecycleConfigArns", []
            ) + user_settings.get("KernelGatewayAppSettings", {}).get(
                "LifecycleConfigArns", []
            )

            domain_default_lcc_arns = domain_default_user_settings.get(
                "JupyterServerAppSettings", {}
            ).get("LifecycleConfigArns", []) + domain_default_user_settings.get(
                "KernelGatewayAppSettings", {}
            ).get(
                "LifecycleConfigArns", []
            )

        return list(set(space_lcc_arns) | set(user_lcc_arns) | set(domain_default_lcc_arns))

    def _merge_security_groups(
        self, domain_default_user_settings, user_settings, space_settings
    ) -> List[str]:
        # SecurityGroups is aggregated when specified in both settings.
        # using set to remove any duplicates
        return list(
            set(
                domain_default_user_settings.get("SecurityGroups", [])
                + user_settings.get("SecurityGroups", [])
                + space_settings.get("SecurityGroups", [])
            )
        )

    def _get_role_arns(self, domain_default_user_settings, user_settings, space_settings):
        role_arn = []
        domain_default_role_arn = domain_default_user_settings.get("ExecutionRole")
        user_role_arn = user_settings.get("ExecutionRole")
        space_role_arn = space_settings.get("ExecutionRole")
        if space_role_arn:
            role_arn.append(space_role_arn)
        elif user_role_arn:
            role_arn.append(user_role_arn)
        elif domain_default_role_arn:
            role_arn.append(domain_default_role_arn)

        return role_arn

    def _does_routes_have_internet_gateway(self, route_details):
        for route in route_details["Routes"]:
            if route.get("GatewayId", "").startswith("igw"):
                return True
        return False

    # TODO: Test with some more data, not sure if I am covering all possible use cases.
    # Also it would be nice to find an easier to way to identify if a subnet is private or public
    async def _get_compatible_subnets(self, vpc_id: str) -> List[str]:
        ec2_client = get_ec2_client()

        subnets = await ec2_client.list_subnets_by_vpc_id(vpc_id)
        route_tables = await ec2_client.list_routetable_by_vpc_id(vpc_id)

        # construct a dictionary for quick access
        subnet_dict = {
            subnet["SubnetId"]: subnet for subnet in subnets.get("Subnets", [])
        }
        route_dict = {
            route["RouteTableId"]: route
            for route in route_tables.get("RouteTables", [])
        }

        ## add 2 fields
        for id in subnet_dict.keys():
            subnet_dict[id][
                "RouteTables"
            ] = (
                []
            )  # if this list is empty then we associate it with main route table of the given vpc
            subnet_dict[id]["IsPublic"] = False

        main_route_table_id = ""
        # update subnet_details with any explict route association
        for id, route in route_dict.items():
            for association in route["Associations"]:
                if association["AssociationState"]["State"] == "associated":
                    subnet_id = association.get("SubnetId")
                    # There can be route associations with subnets that are not shared with the aws account. So the subnets in subnet_dict is the source of truth
                    if subnet_id and subnet_id in subnet_dict:
                        subnet_dict[subnet_id]["RouteTables"].append(
                            route["RouteTableId"]
                        )
                    if association["Main"]:
                        main_route_table_id = route["RouteTableId"]

        # attach main route table to all other subnets, implicit association
        for id in subnet_dict.keys():
            if not subnet_dict[id]["RouteTables"]:
                subnet_dict[id]["RouteTables"].append(main_route_table_id)

        for id in subnet_dict.keys():
            for route_table_id in subnet_dict[id]["RouteTables"]:
                if self._does_routes_have_internet_gateway(
                    route_details=route_dict[route_table_id]
                ):
                    subnet_dict[id]["IsPublic"] = True

        return [
            {"name": v["SubnetId"], "is_selected": False}
            for k, v in subnet_dict.items()
            if not v["IsPublic"]
        ]

    @async_with_metrics("GetAdvancedEnvironment")
    async def get_advanced_environments(self, logger, metrics: MetricsContext):
        sm_client = get_sagemaker_client()

        # empty values if api calls fail
        domain_app_network_access_type = "VpcOnly"
        all_compatible_subnets = []
        security_group_ids = []
        lcc_arns = []
        role_arns = []  # TODO: sync with UI to modify this to a single value
        accountId = await get_aws_account_id()
        s3_bucket_name = (
            f"{self.SAGEMAKER_DEFAULT_S3_PREFIX}-{accountId}-{get_region_name()}"
        )
        s3_uri = f"s3://{s3_bucket_name}/"

        DEFAULT_USER_SETTINGS_KEY = "DefaultUserSettings"
        USER_SETTINGS_KEY = "UserSettings"
        SPACE_SETTINGS_KEY = "SpaceSettings"
        # we could in a shared space app
        # TODO: Refactor shared space as a supported runtime environment
        api_calls = [sm_client.describe_domain(get_domain_id())]

        user_details = {}
        space_details = {}

        if get_user_profile_name():
            api_calls.append(
                sm_client.describe_user_profile(
                    get_domain_id(), get_user_profile_name()
                )
            )
            [domain_details, user_details] = await asyncio.gather(*api_calls)
        else:
            api_calls.append(
                sm_client.describe_space(get_domain_id(), get_shared_space_name())
            )
            [domain_details, space_details] = await asyncio.gather(*api_calls)
            if get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_STUDIO:
                # Only shared Studio spaces will use DefaultSpaceSettings
                DEFAULT_USER_SETTINGS_KEY = "DefaultSpaceSettings"

        logger.info(
            f"domain level details: {domain_details}, user details: {user_details}, space details: {space_details}"
        )

        # Domains created before VpcOnly mode was released will not have AppNetworkAccessType set.
        domain_app_network_access_type = domain_details.get(
            "AppNetworkAccessType", "PublicInternetOnly"
        )

        all_compatible_subnets = await self._get_compatible_subnets(
            vpc_id=domain_details["VpcId"]
        )
        logger.info(
            f"all compatible logs from the vpc - {domain_details['VpcId']}: {all_compatible_subnets}"
        )

        # if the Studio domain subnet is in compatible list then make it true,
        # any subnet that is in domain but not compatible, dont add it to the return value
        for subnet_id in domain_details["SubnetIds"]:
            for index, compatible_subnet in enumerate(all_compatible_subnets):
                if compatible_subnet["name"] == subnet_id:
                    all_compatible_subnets[index]["is_selected"] = True

        # If OwnerUserProfileName exist for space settings, query the user profile name
        owner_user_profile_name = space_details.get("OwnershipSettings", {}).get("OwnerUserProfileName", None)
        if owner_user_profile_name:
            user_details = await sm_client.describe_user_profile(
                get_domain_id(), owner_user_profile_name
            )

        # NOTE: In case of SpaceSettings they dont support security group as part of reInvent 2022,
        # it will be empty, our logic can handle it
        domain_attached_security_group_ids = self._merge_security_groups(
            domain_details.get(DEFAULT_USER_SETTINGS_KEY, {}),
            user_details.get(USER_SETTINGS_KEY, {}),
            space_details.get(SPACE_SETTINGS_KEY, {}),
        )
        for sg_id in domain_attached_security_group_ids:
            security_group_ids.append({"name": sg_id, "is_selected": True})
        if not security_group_ids:
            # If customer choose quick setup, by default Studio is only configured with subnets from default VPC.
            # There is no security group attached by default.
            # Even customer chooses the standard setup, it allows customer to leave the security groups blank.
            # So if we detect that the security group is empty we will make a call to ec2 and get the default security group of the attached VPC
            ec2_client = get_ec2_client()
            security_groups = await ec2_client.list_security_groups_by_vpc_id(
                vpc_id=domain_details["VpcId"]
            )

            for sg in security_groups["SecurityGroups"]:
                security_group_ids.append(
                    {
                        "name": sg["GroupId"],
                        "is_selected": sg["GroupName"] == "default",
                    }
                )
        logger.info(
            f"security group details: {domain_attached_security_group_ids}, Domain VPC ID: {domain_details['VpcId']}, {security_group_ids}"
        )

        lcc_arns = self._get_lcc_arns(
            domain_details.get(DEFAULT_USER_SETTINGS_KEY, {}),
            user_details.get(USER_SETTINGS_KEY, {}),
            space_details.get(SPACE_SETTINGS_KEY, {}),
        )

        # NOTE: In case of SpaceSettings they dont support execution role as part of reInvent 2022,
        # it will be empty, our logic can handle it
        role_arns = self._get_role_arns(
            domain_details.get(DEFAULT_USER_SETTINGS_KEY, {}),
            user_details.get(USER_SETTINGS_KEY, {}),
            space_details.get(SPACE_SETTINGS_KEY, {}),
        )

        try:
            bucket_existed = await get_s3_client().head_bucket(s3_bucket_name)
            logger.info(f"S3 bucket already exists {s3_uri} - {bucket_existed}")
        except botocore.exceptions.ClientError as error:
            error_code = error.response["Error"]["Code"]
            error_message = error.response["Error"]["Message"]
            if error_code == ERROR_CODE and error_message == BUCKET_NOT_EXISTED_MSG:
                try:
                    response = await get_s3_client().create_bucket(
                        s3_bucket_name, get_region_name()
                    )
                    logger.info(f"S3 bucket created succesfully {s3_uri} - {response}")
                    # If the bucket already exists, the versioning & encryption calls is not needed
                    logger.info(f"Enable default server side encryption for {s3_uri}")
                    await get_s3_client().enable_server_side_encryption_with_s3_keys(
                        bucket_name=s3_bucket_name
                    )
                    logger.info(f"Enable versioning for {s3_uri}")
                    await get_s3_client().enable_versioning(bucket_name=s3_bucket_name)

                    logger.info(f"S3 bucket created succesfully {s3_uri} - {response}")
                except botocore.exceptions.ClientError as error:
                    # TODO: Discuss with PM on the desired fail safe mechanism, what if the bucket creation failed due to permission issue
                    # ideally we need the UI to prompt the user to create the bucket
                    # some issue with bucket creation
                    logger.error(
                        f"error when calling S3 bucket creation - {s3_bucket_name} - {error}"
                    )

        default_envs = [
            AdvancedEnvironment(
                name="s3_input",
                label="Input S3",
                description="S3 location to store all notebook related files",
                value=s3_uri,
            ),
            AdvancedEnvironment(
                name="s3_output",
                label="Output S3",
                description="S3 location to store all output artifacts",
                value=s3_uri,
            ),
            AdvancedEnvironment(
                name="role_arn",
                label="Execution Role ARN",
                description="IAM Role to be used by the Notebook Execution Engine",
                value=role_arns,
            ),
            AdvancedEnvironment(
                name="image",
                label="SageMaker Image",
                description="SageMaker Image to execute the notebook in",
                value=f"ecr-location",  # list
            ),
            AdvancedEnvironment(
                name="kernel",
                label="Python Kernel",
                description="Python Kernel to execute the notebook in",
                value=f"kernel name from notebook metadata",
            ),
            AdvancedEnvironment(
                name="lcc_arn",
                label="LCC ARN",
                description="LCC ARN to be executed before execution",
                value=lcc_arns,
            ),
            AdvancedEnvironment(
                name="vpc_security_group_ids",
                label="VPC Config Security Group IDs",
                description="List of Security GroupIDs for the notebook to be executed",
                value=security_group_ids,
            ),
            AdvancedEnvironment(
                name="vpc_subnets",
                label="VPC Config Subnets",
                description="List of Subnets for the notebook to be executed in",
                value=all_compatible_subnets,
            ),
            AdvancedEnvironment(
                name="app_network_access_type",
                label="App Network Access Type",
                description="Access type for the network",
                value=domain_app_network_access_type,
            ),
        ]
        logger.info(f"auto-detected env values - {default_envs}")
        return AdvancedEnvironmentResponse(auto_detected_config=default_envs)
