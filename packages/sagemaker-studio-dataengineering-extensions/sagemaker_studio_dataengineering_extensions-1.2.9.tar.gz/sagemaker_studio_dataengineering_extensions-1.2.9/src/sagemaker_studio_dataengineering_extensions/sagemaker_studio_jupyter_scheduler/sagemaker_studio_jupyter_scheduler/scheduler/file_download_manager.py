import os
import io
import tarfile
import logging
from typing import Dict, List, Optional, Type

from urllib.parse import urlparse
from jupyter_server.utils import ensure_async

from jupyter_scheduler.exceptions import SchedulerError
from jupyter_scheduler.scheduler import BaseScheduler
from jupyter_scheduler.job_files_manager import JobFilesManager
from jupyter_scheduler.job_files_manager import Downloader as JupyterDownloader

from multiprocessing import Process

from sagemaker_studio_jupyter_scheduler.logging import HOME_DIR
from sagemaker_studio_jupyter_scheduler.util.utils import should_use_jupyter_scheduler
from sagemaker_studio_jupyter_scheduler.util.aws_clients import get_s3_client
from sagemaker_studio_jupyter_scheduler.model.models import RuntimeEnvironmentParameterName

class SageMakerJobFilesManager(JobFilesManager):
    scheduler = None

    def __init__(self, scheduler: Type[BaseScheduler]):
        self.scheduler = scheduler

    async def copy_from_staging(self, job_id: str, redownload: Optional[bool] = False):
        job = await ensure_async(self.scheduler.get_job(job_id, False))
        self.scheduler.log.info(f"[SageMakerScheduler] copy_from_staging: job is {str(job)}")
        staging_paths = await ensure_async(self.scheduler.get_staging_paths(job))
        self.scheduler.log.info(f"[SageMakerScheduler] copy_from_staging: staging_paths is {staging_paths}")
        output_filenames = self.scheduler.get_job_filenames(job)
        self.scheduler.log.info(f"[SageMakerScheduler] copy_from_staging: output_filenames is {output_filenames}")
        output_dir = self.scheduler.get_local_output_path(job, root_dir_relative=True)
        output_dir = HOME_DIR + "/" + output_dir
        self.scheduler.log.info(f"[SageMakerScheduler] copy_from_staging: output_dir is {output_dir}")

        if should_use_jupyter_scheduler(job_id):
            self.scheduler.log.info(f"[SageMakerScheduler] copy_from_staging: Job ID {job_id} is UUID format, delegating to jupyter scheduler downloader")
            p = Process(
                target=JupyterDownloader(
                    output_formats=job.output_formats,
                    output_filenames=output_filenames,
                    staging_paths=staging_paths,
                    output_dir=output_dir,
                    redownload=redownload,
                    include_staging_files=job.package_input_folder,
                ).download
            )
            p.start()
        else: 
            s3_input_uri = job.runtime_environment_parameters.get(RuntimeEnvironmentParameterName.S3_INPUT.value, "")
            training_job_name = job.job_id

            await Downloader(
                output_formats=job.output_formats,
                output_filenames=output_filenames,
                staging_paths=staging_paths,
                output_dir=output_dir,
                redownload=redownload,
                logger=self.scheduler.log,
                s3_input_uri=s3_input_uri,
                training_job_name=training_job_name,
                include_staging_files=job.package_input_folder
            ).download()

class Downloader:
    def __init__(
        self,
        output_formats: List[str],
        output_filenames: Dict[str, str],
        staging_paths: Dict[str, str],
        output_dir: str,
        redownload: bool,
        logger: logging.Logger,
        s3_input_uri: str,
        training_job_name: str,
        include_staging_files: bool = False,
    ):
        self.output_formats = output_formats
        self.output_filenames = output_filenames
        self.staging_paths = staging_paths
        self.output_dir = output_dir
        self.redownload = redownload
        self.s3_client = get_s3_client()
        self.log = logger
        self.s3_input_uri = s3_input_uri
        self.training_job_name = training_job_name
        self.include_staging_files = include_staging_files

    def generate_filepaths(self):
        """A generator that produces filepaths"""
        output_formats = self.output_formats + ["input"]

        for output_format in output_formats:
            input_filepath = self.staging_paths[output_format]
            output_filepath = os.path.join(self.output_dir, self.output_filenames[output_format])
            if not os.path.exists(output_filepath) or self.redownload:
                yield input_filepath, output_filepath

    async def get_packaged_file_paths(self):
        s3_bucket_name, s3_object_key = self.parse_s3_url(self.s3_input_uri)
        prefix = f"{self.training_job_name}/input/"
        if s3_object_key:
            prefix = f"{s3_object_key}/"
        input_s3_objects = await self.s3_client.list_objects(bucket=s3_bucket_name, prefix=prefix)
        packaged_files = []
        output_files = []
        for file in input_s3_objects:
            if self.staging_paths["input"] != file[len(prefix):]:
                packaged_filepath = file
                output_filepath = os.path.join(self.output_dir, file[len(prefix):])
                packaged_files.append(packaged_filepath)
                output_files.append(output_filepath)

        return packaged_files, output_files, s3_bucket_name

    def parse_s3_url(self, url):
        parsed_url = urlparse(url, allow_fragments=False)
        bucket_name = parsed_url.netloc
        key = parsed_url.path.lstrip('/')
        if parsed_url.query:
            key += '?' + parsed_url.query
        return bucket_name, key

    async def download_tar(self, archive_format: str = "tar"):
        try:
            self.log.info(f"[SageMakerScheduler] download_tar: archive_format is {archive_format}")
            archive_filepath = self.staging_paths[archive_format]
            read_mode = "r:gz" if archive_format == "tar.gz" else "tar"
            s3_bucket_name, s3_object_key = self.parse_s3_url(archive_filepath)


            self.log.info(f"[SageMakerScheduler] download_tar: s3_bucket_name is {s3_bucket_name}, s3_object_key is {s3_object_key}")
            archive_file = await self.s3_client.get_object_content(bucket=s3_bucket_name, key=s3_object_key)
            archive_file_obj = io.BytesIO(archive_file)
            with tarfile.open(fileobj=archive_file_obj, mode=read_mode) as tar:
                filepaths = self.generate_filepaths()
                for input_filepath, output_filepath in filepaths:
                        self.log.info(f"[SageMakerScheduler] download_tar: input_filepath is {input_filepath}, output_filepath is {output_filepath}")
                        input_file = tar.extractfile(member=input_filepath)
                        with open(output_filepath, mode="wb") as output_file:
                            output_file.write(input_file.read())
        except Exception as e:
            self.log.exception(f"Error downloading job output files: {e}")

    async def download(self):
        self.log.info(f"[SageMakerScheduler] download: staging_paths is {self.staging_paths}")
        # ensure presence of staging paths
        if not self.staging_paths:
            return


        # ensure presence of output dir
        output_dir = self.output_dir
        if not os.path.exists(output_dir):
            self.log.info(f"[SageMakerScheduler] makedirs: output_dir is {self.output_dir}")
            os.makedirs(output_dir)
        
        self.log.info(f"[SageMakerScheduler] download: output_dir is {self.output_dir}")

        if "tar" in self.staging_paths:
            self.log.info(f"[SageMakerScheduler] download: download_tar")
            await self.download_tar()
        elif "tar.gz" in self.staging_paths:
            self.log.info(f"[SageMakerScheduler] download: download_tar.gz")
            await self.download_tar("tar.gz")
        else:
            self.log.info(f"[SageMakerScheduler] download: fallback")
            filepaths = self.generate_filepaths()
            for input_filepath, output_filepath in filepaths:
                try:
                    s3_bucket_name, s3_bucket_key = self.parse_s3_url(input_filepath)
                    input_file = await self.s3_client.get_object_content(bucket=s3_bucket_name, key=s3_bucket_key)
                    dir_name = os.path.dirname(output_filepath)
                    if not os.path.exists(dir_name):
                        os.makedirs(dir_name)
                    with open(output_filepath, 'wb') as output_file:
                        output_file.write(input_file)
                except Exception as e:
                    self.log.exception(f"Error downloading job output file {input_filepath}: {e}")

        if self.include_staging_files:
            input_filepaths, output_filepaths, s3_bucket_name = await self.get_packaged_file_paths()
            for input_filepath, output_filepath in zip(input_filepaths, output_filepaths):
                try:
                    input_file = await self.s3_client.get_object_content(bucket=s3_bucket_name, key=input_filepath)
                    dir_name = os.path.dirname(output_filepath)
                    if not os.path.exists(dir_name):
                        os.makedirs(dir_name)
                    with open(output_filepath, 'wb') as output_file:
                        output_file.write(input_file)
                except Exception as e:
                    self.log.exception(f"Error downloading job input file {input_filepath} from bucket {s3_bucket_key}: {e}")
