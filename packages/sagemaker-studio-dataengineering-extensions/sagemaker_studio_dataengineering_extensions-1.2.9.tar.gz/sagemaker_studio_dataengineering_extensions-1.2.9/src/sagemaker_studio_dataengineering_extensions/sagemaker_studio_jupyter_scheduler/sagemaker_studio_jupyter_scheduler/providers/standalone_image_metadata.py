import re
from sagemaker_studio_jupyter_scheduler.model.models import ImageMetadata

# These details are going to be the same for all images, so avoiding the maintenance of a json file with extra details
# Only these fields are needed from sagemaker base python image, if more information is needed in the future we can add it

STANDALONE_DEFAULT_UID = "0"
STANDALONE_DEFAULT_GUID = "0"
STANDALONE_DEFAULT_MOUNT_PATH = "/root"
STANDALONE_DEFAULT_IMAGE_OWNER = "Studio"
STANDALONE_KERNEL_NAME = "python3"
STANDALONE_IMAGEARN_KEY = "ImageOrVersionArn"
STANDALONE_ECR_URI_KEY = "AppImageUri"

# TODO: we only need image name and the account id for each region to get the latest ecr uri. We eventually have to move away from maintaining static information.
# makes it harder to keep them upto date

standalone_image_map = {
    "af-south-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:af-south-1:559312083959:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "559312083959.dkr.ecr.af-south-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "ap-east-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:ap-east-1:493642496378:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "493642496378.dkr.ecr.ap-east-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "ap-northeast-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:ap-northeast-1:102112518831:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "102112518831.dkr.ecr.ap-northeast-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "ap-northeast-2": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:ap-northeast-2:806072073708:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "806072073708.dkr.ecr.ap-northeast-2.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "ap-northeast-3": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:ap-northeast-3:792733760839:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "792733760839.dkr.ecr.ap-northeast-3.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "ap-south-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:ap-south-1:394103062818:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "394103062818.dkr.ecr.ap-south-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "ap-southeast-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:ap-southeast-1:492261229750:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "492261229750.dkr.ecr.ap-southeast-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "ap-southeast-2": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:ap-southeast-2:452832661640:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "452832661640.dkr.ecr.ap-southeast-2.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "ap-southeast-3": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:ap-southeast-3:276181064229:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "276181064229.dkr.ecr.ap-southeast-3.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "ca-central-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:ca-central-1:310906938811:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "310906938811.dkr.ecr.ca-central-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "cn-north-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:cn-north-1:390048526115:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "390048526115.dkr.ecr.cn-north-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "cn-northwest-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:cn-northwest-1:390780980154:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "390780980154.dkr.ecr.cn-northwest-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "eu-central-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:eu-central-1:936697816551:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "936697816551.dkr.ecr.eu-central-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "eu-north-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:eu-north-1:243637512696:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "243637512696.dkr.ecr.eu-north-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "eu-south-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:eu-south-1:592751261982:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "592751261982.dkr.ecr.eu-south-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "eu-west-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:eu-west-1:470317259841:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "470317259841.dkr.ecr.eu-west-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "eu-west-2": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:eu-west-2:712779665605:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "712779665605.dkr.ecr.eu-west-2.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "eu-west-3": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:eu-west-3:615547856133:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "615547856133.dkr.ecr.eu-west-3.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "me-south-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:me-south-1:117516905037:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "117516905037.dkr.ecr.me-south-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "sa-east-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:sa-east-1:782484402741:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "782484402741.dkr.ecr.sa-east-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "us-east-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:us-east-1:081325390199:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "081325390199.dkr.ecr.us-east-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "us-east-2": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:us-east-2:429704687514:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "429704687514.dkr.ecr.us-east-2.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "us-west-1": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:us-west-1:742091327244:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "742091327244.dkr.ecr.us-west-1.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
    "us-west-2": {
        STANDALONE_IMAGEARN_KEY: "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-base-python-38",
        STANDALONE_ECR_URI_KEY: "236514542706.dkr.ecr.us-west-2.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
    },
}


def get_default_image_arn_standalone(aws_region: str):
    return standalone_image_map.get(aws_region, {}).get(STANDALONE_IMAGEARN_KEY, "")


def get_default_ecr_uri_standalone(aws_region: str):
    return standalone_image_map.get(aws_region, {}).get(STANDALONE_ECR_URI_KEY, "")


# same kernel will be used for all regions
def get_default_image_kernel_name_standalone():
    return STANDALONE_KERNEL_NAME


async def get_image_metadata_standalone(image_arn: str, region: str):
    # TODO: add a better regex to validate the ecr image
    if "dkr.ecr" in image_arn:
        return ImageMetadata(ecr_uri=image_arn, image_arn=image_arn)

    # we will use basepython 2.0 studio image as default for customers to get started
    return ImageMetadata(
        ecr_uri=get_default_ecr_uri_standalone(region),
        image_arn=get_default_image_arn_standalone(region),
        image_owner=STANDALONE_DEFAULT_IMAGE_OWNER,
        mount_path=STANDALONE_DEFAULT_MOUNT_PATH,
        uid=STANDALONE_DEFAULT_UID,
        gid=STANDALONE_DEFAULT_GUID,
    )
