"""
ECR Account ID mapping for SageMaker Distribution images by region.

This module provides the mapping between AWS regions and their corresponding
ECR account IDs for SageMaker Distribution container images.

Based on: https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks-available-images.html
"""

# Mapping of AWS regions to ECR account IDs for SageMaker Distribution images
ECR_ACCOUNT_MAPPING = {
    "us-east-1": "885854791233",
    "us-east-2": "137914896644", 
    "us-west-1": "053634841547",
    "us-west-2": "542918446943",
    "af-south-1": "238384257742",
    "ap-east-1": "523751269255",
    "ap-south-1": "245090515133",
    "ap-southeast-1": "022667117163",
    "ap-southeast-2": "648430277019",
    "ap-southeast-3": "370607712162",
    "ap-northeast-1": "010972774902",
    "ap-northeast-2": "064688005998",
    "ap-northeast-3": "564864627153",
    "ca-central-1": "481561238223",
    "eu-central-1": "545423591354",
    "eu-west-1": "819792524951",
    "eu-west-2": "021081402939",
    "eu-west-3": "856416204555",
    "eu-north-1": "175620155138",
    "eu-south-1": "810671768855",
    "me-south-1": "523774347010",
    "me-central-1": "358593528301",
    "sa-east-1": "567556641782"
}


def get_ecr_account_id(region: str) -> str:
    """
    Get the ECR account ID for a given AWS region.
    
    Args:
        region: AWS region name (e.g., 'us-east-1')
        
    Returns:
        ECR account ID for the region
        
    Raises:
        KeyError: If the region is not supported
    """
    if region not in ECR_ACCOUNT_MAPPING:
        raise KeyError(f"Unsupported region: {region}")
    
    return ECR_ACCOUNT_MAPPING[region]


def build_sagemaker_distribution_uri(region: str, stage: str, version: str, processor_type: str = None) -> str:
    """
    Build the complete ECR URI for SageMaker Distribution image.
    
    Args:
        region: AWS region name (e.g., 'us-east-1')
        stage: Environment stage (e.g., 'prod', 'dev')
        version: SMD version (e.g., '2.2', '3.0', '3.1')
        processor_type: Processor type ('cpu' or 'gpu'), optional for some versions
        
    Returns:
        Complete ECR URI
        
    Examples:
        >>> build_sagemaker_distribution_uri('us-east-1', 'prod', '3.1', 'cpu')
        '885854791233.dkr.ecr.us-east-1.amazonaws.com/sagemaker-distribution-prod:3.1-cpu'
        >>> build_sagemaker_distribution_uri('us-east-1', 'prod', '2.2', 'cpu')
        '885854791233.dkr.ecr.us-east-1.amazonaws.com/sagemaker-distribution-embargoed-prod:2.2-reinvent2024-cpu'
    """
    account_id = get_ecr_account_id(region)
    
    # For versions 2.2 and 3.0, use embargoed format with reinvent2024 tag
    if version in ['2.2', '3.0']:
        repo_name = f"sagemaker-distribution-embargoed-{stage}"
        if processor_type:
            tag = f"{version}-reinvent2024-{processor_type}"
        else:
            tag = f"{version}-reinvent2024"
    else:
        # For other versions, use regular format
        repo_name = f"sagemaker-distribution-{stage}"
        if processor_type:
            tag = f"{version}-{processor_type}"
        else:
            tag = version
    
    return f"{account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}:{tag}"
