import os
from sagemaker_studio_jupyter_scheduler.util.aws_clients import (
    get_iam_client, get_sts_client,
)
from async_lru import alru_cache


@alru_cache(maxsize=1)
async def get_aws_account_id():
    accountId = os.environ.get("AWS_ACCOUNT_ID")
    if accountId is None:
        # we are in standalone jupyterlab
        get_caller_identity_response = await get_sts_client().get_caller_identity()
        accountId = get_caller_identity_response.get("Account")
    return accountId


@alru_cache(maxsize=1)
async def get_role_arn_from_caller_identity():
    """Get role ARN from STS caller identity"""
    get_caller_identity_response = await get_sts_client().get_caller_identity()
    return get_caller_identity_response.get("Arn")


async def get_execution_role_arn(project_id: str, env_id: str, partition: str = "aws") -> str:
    """Get execution role ARN from caller identity or construct from metadata
    
    Args:
        project_id: Project identifier for fallback role construction
        env_id: Environment identifier for fallback role construction
        partition: AWS partition (default: "aws")
        
    Returns:
        Role ARN string
    """
    try:
        # Try to get role ARN from caller identity first
        caller_identity_arn = await get_role_arn_from_caller_identity()
        
        if caller_identity_arn:
            # If we get a role ARN from caller identity, use it
            if ":role/" in caller_identity_arn:
                return caller_identity_arn
            
            # Handle assumed role ARN - convert to role ARN format
            if ":assumed-role/" in caller_identity_arn:
                # Extract account ID and role name from assumed role ARN
                # Format: arn:aws:sts::ACCOUNT:assumed-role/ROLE_NAME/SESSION_NAME
                parts = caller_identity_arn.split(":")
                if len(parts) >= 6:
                    account_id = parts[4]
                    role_info = parts[5]  # assumed-role/ROLE_NAME/SESSION_NAME
                    if role_info.startswith("assumed-role/"):
                        role_name = role_info.split("/")[1]  # Extract ROLE_NAME
                        iam_client = get_iam_client()
                        return await iam_client.get_role_arn_by_role_name(role_name)
        
        # Fallback: construct role ARN from environment metadata
        account_id = await get_aws_account_id()
        role_name = f"datazone_usr_role_{project_id}_{env_id}"
        return f"arn:{partition}:iam::{account_id}:role/{role_name}"
        
    except Exception as e:
        # Fallback: construct role ARN from environment metadata
        account_id = await get_aws_account_id()
        role_name = f"datazone_usr_role_{project_id}_{env_id}"
        return f"arn:{partition}:iam::{account_id}:role/{role_name}"
