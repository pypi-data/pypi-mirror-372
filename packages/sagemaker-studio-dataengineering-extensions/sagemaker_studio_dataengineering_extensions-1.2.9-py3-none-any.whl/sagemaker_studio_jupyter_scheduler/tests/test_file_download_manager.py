import os
import logging
from typing import Optional
import pytest
from unittest.mock import MagicMock, Mock, patch, AsyncMock
from jupyter_scheduler.models import DescribeJob
from sagemaker_studio_jupyter_scheduler.logging import HOME_DIR
from sagemaker_studio_jupyter_scheduler.scheduler import (
    SageMakerJobFilesManager,
    Downloader
)
from sagemaker_studio_jupyter_scheduler.model.models import RuntimeEnvironmentParameterName
from sagemaker_studio_jupyter_scheduler.util.aws_clients import S3AsyncBoto3Client

MOCK_JOB_ID = "a-b-c-d"
MOCK_STAGING_PATHS = {
        "tar.gz": "s3://s3-output-uri/job_files/helloworld.tar.gz",
        "ipynb": "helloworld-2024-05-10.ipynb",
        "input": "helloworld.ipynb",
        "files": [],
        "log": "helloworld-2024-05-10.log",
    }
MOCK_JOB_FILENAMES = {
        "ipynb": "helloworld-2024-05-10.ipynb",
        "input": "helloworld.ipynb",
        "log": "helloworld-2024-05-10.log",
    }
MOCK_OUTPUT_DIR = "jobs/a-b-c-d"
MOCK_S3_CONTENT = b"object-content"
MOCK_OUTPUT_FORMATS = ["input", "ipynb", "log"]
MOCK_S3_INPUT_BUCKET_NAME = "s3-input-uri"
MOCK_S3_INPUT_URI_CREATE_JOB = f"s3://{MOCK_S3_INPUT_BUCKET_NAME}"
MOCK_PACKAGED_FILE_PATHS = [f"{MOCK_JOB_ID}/input/abc.txt", f"{MOCK_JOB_ID}/input/def.csv"]
MOCK_PACKAGED_OUTPUT_FILE_PATHS = [f"{HOME_DIR}/{MOCK_OUTPUT_DIR}/abc.txt", f"{HOME_DIR}/{MOCK_OUTPUT_DIR}/def.csv"]
MOCK_S3_LIST_OBJECTS = [f"{MOCK_JOB_ID}/input/abc.txt", f"{MOCK_JOB_ID}/input/def.csv", f"{MOCK_JOB_ID}/input/helloworld.ipynb"]

def get_mock_describe_job(package_input_folder: Optional[bool] = None):
    mock_job = DescribeJob(
        name="my-job",
        input_filename="mock-input-filename",
        runtime_environment_name="mock-runtime-environment-name",
        job_id=MOCK_JOB_ID,
        url="mock-url",
        create_time=123,
        update_time=456,
        output_formats=MOCK_OUTPUT_FORMATS,
        runtime_environment_parameters={RuntimeEnvironmentParameterName.S3_INPUT.value: MOCK_S3_INPUT_URI_CREATE_JOB},
        package_input_folder=package_input_folder
    )

    return mock_job


def get_mock_downloader(include_staging_files: Optional[bool] = False, s3_uri: str = MOCK_S3_INPUT_URI_CREATE_JOB):
    logger = logging.getLogger()

    mock_downloader = Downloader(
        output_formats=MOCK_OUTPUT_FORMATS,
        output_filenames=MOCK_JOB_FILENAMES,
        staging_paths=MOCK_STAGING_PATHS,
        output_dir=HOME_DIR + "/" + MOCK_OUTPUT_DIR,
        redownload=False,
        include_staging_files=include_staging_files,
        logger=logger,
        s3_input_uri=s3_uri,
        training_job_name=MOCK_JOB_ID,
    )

    return mock_downloader


@pytest.mark.asyncio
@patch("sagemaker_studio_jupyter_scheduler.scheduler.scheduler.SageMakerScheduler")
@patch("sagemaker_studio_jupyter_scheduler.scheduler.file_download_manager.Downloader")
@patch.object(S3AsyncBoto3Client, "get_object_content", return_value=MOCK_S3_CONTENT)
async def test_copy_from_staging(mock_s3_content, mock_downloader, mock_scheduler):

    mock_downloader.return_value = AsyncMock()
    mock_downloader.return_value.download = AsyncMock()

    mock_job = get_mock_describe_job()
    mock_scheduler.get_job.return_value = mock_job
    mock_scheduler.get_staging_paths.return_value = MOCK_STAGING_PATHS
    mock_scheduler.get_local_output_path.return_value = MOCK_OUTPUT_DIR
    mock_scheduler.get_job_filenames.return_value = MOCK_JOB_FILENAMES

    manager = SageMakerJobFilesManager(scheduler=mock_scheduler)
    await manager.copy_from_staging("a-b-c-d")

    mock_downloader.assert_called_once_with(
        output_formats=mock_job.output_formats,
        output_filenames=MOCK_JOB_FILENAMES,
        staging_paths=MOCK_STAGING_PATHS,
        output_dir=HOME_DIR + "/" + MOCK_OUTPUT_DIR,
        redownload=False,
        include_staging_files=None,
        logger=mock_scheduler.log,
        s3_input_uri=mock_job.runtime_environment_parameters.get(
            RuntimeEnvironmentParameterName.S3_INPUT.value
        ),
        training_job_name=mock_job.job_id,
    )


@pytest.mark.asyncio
@patch.object(S3AsyncBoto3Client, "get_object_content", return_value=MOCK_S3_CONTENT)
async def test_download__with_tar_gz_staging_path_and_packaged_files(mock_s3_content):

    mock_downloader = get_mock_downloader(include_staging_files=True)
    mock_downloader.download_tar = AsyncMock()
    mock_downloader.get_packaged_file_paths = AsyncMock(return_value=[MOCK_PACKAGED_FILE_PATHS, MOCK_PACKAGED_OUTPUT_FILE_PATHS, MOCK_S3_INPUT_BUCKET_NAME])

    await mock_downloader.download()

    mock_downloader.download_tar.assert_called_once_with("tar.gz")
    assert os.path.exists(f"{HOME_DIR}/{MOCK_OUTPUT_DIR}")
    for path in MOCK_PACKAGED_OUTPUT_FILE_PATHS:
        assert os.path.exists(path)


@pytest.mark.asyncio
@patch.object(S3AsyncBoto3Client, "list_objects", return_value=MOCK_S3_LIST_OBJECTS)
async def test_get_packaged_file_paths(mock_list_objects):

    mock_downloader = get_mock_downloader(include_staging_files=True)
    packaged_files, output_files, s3_bucket_name = await mock_downloader.get_packaged_file_paths()

    assert s3_bucket_name==MOCK_S3_INPUT_BUCKET_NAME
    assert output_files==MOCK_PACKAGED_OUTPUT_FILE_PATHS
    assert packaged_files==MOCK_PACKAGED_FILE_PATHS


@pytest.mark.asyncio
@patch.object(S3AsyncBoto3Client, "list_objects", return_value=MOCK_S3_LIST_OBJECTS)
async def test_get_packaged_file_paths__with_create_job_definition_uri(mock_list_objects):
    MOCK_S3_INPUT_URI_CREATE_JOB_DEFINITION = f"s3://{MOCK_S3_INPUT_BUCKET_NAME}/{MOCK_JOB_ID}/input"
    mock_downloader = get_mock_downloader(include_staging_files=True, s3_uri=MOCK_S3_INPUT_URI_CREATE_JOB_DEFINITION)
    packaged_files, output_files, s3_bucket_name = await mock_downloader.get_packaged_file_paths()

    assert s3_bucket_name==MOCK_S3_INPUT_BUCKET_NAME
    assert output_files==MOCK_PACKAGED_OUTPUT_FILE_PATHS
    assert packaged_files==MOCK_PACKAGED_FILE_PATHS
