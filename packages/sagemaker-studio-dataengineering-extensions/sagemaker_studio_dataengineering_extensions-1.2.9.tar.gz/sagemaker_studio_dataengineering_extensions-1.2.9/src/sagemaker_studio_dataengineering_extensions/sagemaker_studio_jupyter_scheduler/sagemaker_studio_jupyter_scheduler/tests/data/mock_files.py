MOCK_RESOURCE_METADATA = """
{
  "AppType": "JupyterLab",
  "ResourceArn": "arn:aws:sagemaker:us-west-2:112233445566:app/d-1a2b3c4d5e6f/fake-user/JupyterServer/default",
  "UserProfileName": "sunp",
  "DomainId": "d-1a2b3c4d5e6f"
}
"""

MOCK_INTERNAL_METADATA = """
{
  "LldsEndpoint": "",
  "AppNetworkAccessType": "PublicInternetOnly",
  "SharingSettings": {
    "S3Uri": "s3://sagemaker-studio-748478975813-60ixnr2yawj/sharing",
    "AllowIncludeNotebookOutput": "true"
  },
  "CustomImages": [
    {
      "ImageOrVersionArn": "arn:aws:sagemaker:us-east-1:177118115371:image/multi-py-conda-image",
      "AppImageConfig": {
        "KernelSpecs": [
          {
            "Name": "conda-env-py310-py",
            "DisplayName": "conda env py310"
          },
          {
            "Name": "conda-env-py39-py",
            "DisplayName": "conda env py39"
          },
          {
            "Name": "conda-env-py37-py",
            "DisplayName": "conda env py37"
          },
          {
            "Name": "conda-env-py38-py",
            "DisplayName": "conda env py38"
          }
        ]
      }
    },
    {
      "ImageOrVersionArn": "arn:aws:sagemaker:us-east-1:177118115371:image-version/multi-py-conda-image/2",
      "AppImageConfig": {
        "KernelSpecs": [
          {
            "Name": "conda-env-py310-py",
            "DisplayName": "conda env py310"
          },
          {
            "Name": "conda-env-py39-py",
            "DisplayName": "conda env py39"
          },
          {
            "Name": "conda-env-py37-py",
            "DisplayName": "conda env py37"
          },
          {
            "Name": "conda-env-py38-py",
            "DisplayName": "conda env py38"
          }
        ]
      }
    }
  ],
  "Stage": "prod",
  "FirstPartyImages": [
    {
      "ImageOrVersionArn": "arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0",
      "AppImageUri": "236514542706.dkr.ecr.us-west-2.amazonaws.com/sagemaker-data-science-environment:1.0",
      "ImageMetadata": {
        "ImageDisplayName": "Data Science",
        "ImageDescription": "Anaconda Individual Edition https://www.anaconda.com/distribution/"
      },
      "IsGpuOptimized": false,
      "AppImageConfig": {
        "FileSystemConfig": {
          "MountPath": "/root",
          "DefaultUid": "0",
          "DefaultGid": "0"
        },
        "KernelSpecs": [
          { "Name": "python3", "DisplayName": "Python 3 (Data Science)" }
        ]
      },
      "FirstPartyImageOwner": "Studio",
      "IsVisibleInLauncher": "true"
    },
    {
      "ImageOrVersionArn": "arn:aws:sagemaker:us-west-2:123456789012:image/sagemaker-distribution-gpu-v0",
      "AppImageUri": "123456789012.dkr.ecr.us-west-2.amazonaws.com/sagemaker-distribution-prod:0.4.1-gpu",
      "ImageMetadata": {
        "ImageDisplayName": "SageMaker Distribution v0 GPU",
        "ImageDescription": "Latest version 0.4.1 https://github.com/aws/sagemaker-distribution"
      },
      "IsGpuOptimized": true,
      "AppImageConfig": {
        "FileSystemConfig": {
          "MountPath": "/home/sagemaker-user",
          "DefaultUid": "1000",
          "DefaultGid": "100"
        },
        "KernelSpecs": [
          { "Name": "python3", "DisplayName": "Python 3 (SageMaker Distribution v0 GPU)" }
        ]
      },
      "FirstPartyImageOwner": "Studio",
      "IsVisibleInLauncher": true
    }
  ]
}
"""

MOCK_VANILLA_METADATA = """
{
    "us-west-2":[
      {
         "ImageOrVersionArn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-base-python-38",
         "AppImageUri": "236514542706.dkr.ecr.us-west-2.amazonaws.com/sagemaker-base-python-38@sha256:27779e7604272e1d15ba19f5de70baa31dcceb246d5021f8c2c5d9db39c208cc",
         "ImageMetadata": {
            "ImageDisplayName": "Base Python 2.0",
            "ImageDescription": "Official Python3.8 image from DockerHub https://hub.docker.@@DOMAIN_STUFFIX@@/_/python"
         },
         "IsGpuOptimized": false,
         "AppImageConfig": {
            "FileSystemConfig": {
               "MountPath": "/root",
               "DefaultUid": "0",
               "DefaultGid": "0"
            },
            "KernelSpecs": [
               {
                  "Name": "python3",
                  "DisplayName": "Python 3 (Base Python 2.0)"
               }
            ]
         },
         "FirstPartyImageOwner": "Studio",
         "IsVisibleInLauncher": true
      }
   ]
}
"""

MOCK_STORAGE_METADATA = """
{
  "smusProjectDirectory": "/home/sagemaker-user/shared",
  "isGitProject": false
}
"""
