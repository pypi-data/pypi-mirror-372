import asyncio
import json
import logging
import os
import subprocess
from datetime import UTC, datetime

import boto3
import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
from tornado import web

from .workflow_utils import (
    PROJECT_SNAPSHOT_DIR,
    S3_CONFIG_DIR,
    TIMESTAMP_FORMAT,
    WORKFLOW_LOCAL_RUNNER_STATUS_FILE,
    WORKFLOWS_CONFIG_DIR,
    ErrorMessage,
    WorkflowLocalRunnerStatus,
    check_file_exists,
    clone_dir,
    deploy_config_files,
    from_json,
    get_shared_directory_path,
    get_shared_project_s3_path,
    git_clone,
    hash_is_deployed,
    is_git_project,
    parse_datetime,
    remove_directory,
    to_json,
    update_metadata,
    upload_directory_to_s3,
    determine_s3_paths,
)

logger = logging.getLogger(__name__)


class SageMakerWorkflowHandler(ExtensionHandlerMixin, APIHandler):
    @property
    def s3_client(self):
        return boto3.Session().client("s3")

    @tornado.web.authenticated
    async def post(self, command):
        try:
            logger.info(f"received request to {command}")
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, self.dispatcher, "POST", command)
            await self.finish(json.dumps(result))
        except Exception as e:
            logger.exception(e)
            raise e

    @tornado.web.authenticated
    async def get(self, command):
        try:
            logger.info(f"received request to {command}")
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, self.dispatcher, "GET", command)
            await self.finish(json.dumps(result))
        except Exception as e:
            logger.exception(e)
            raise e

    def dispatcher(self, method, command):
        get_command_registry = {
            "get-local-runner-status": self.get_local_runner_status,
        }
        post_command_registry = {
            "update-local-runner-status": self.update_local_runner_status,
            "start-local-runner": self.start_local_runner,
            "stop-local-runner": self.stop_local_runner,
            "deploy-project": self.deploy_project,
        }
        if method == "GET":
            if command not in get_command_registry:
                raise web.HTTPError(405, ErrorMessage.INVALID_REQUEST_API_NOT_FOUND)
            return get_command_registry[command]()
        elif method == "POST":
            if command not in post_command_registry:
                raise web.HTTPError(405, ErrorMessage.INVALID_REQUEST_API_NOT_FOUND)
            return post_command_registry[command](**json.loads(self.request.body))
        else:
            raise web.HTTPError(405, ErrorMessage.INVALID_REQUEST_METHOD_NOT_SUPPORTED)

    def get_local_runner_status(self):
        try:
            if not os.path.exists(WORKFLOW_LOCAL_RUNNER_STATUS_FILE):
                # TODO: Invoke the post-startup status API to get the actual error message
                return {
                    "timestamp": datetime.now(UTC).strftime(TIMESTAMP_FORMAT),
                    "status": "unhealthy",
                    "detailed_status": ErrorMessage.STATUS_FILE_NOT_FOUND,
                }
            elif os.stat(WORKFLOW_LOCAL_RUNNER_STATUS_FILE).st_size == 0:
                # Indicate file is empty and add basic "[]" to file
                to_json([], WORKFLOW_LOCAL_RUNNER_STATUS_FILE)
                return {
                    "timestamp": datetime.now(UTC).strftime(TIMESTAMP_FORMAT),
                    "status": "unhealthy",
                    "detailed_status": ErrorMessage.STATUS_FILE_EMPTY,
                }
            status_log = from_json(WORKFLOW_LOCAL_RUNNER_STATUS_FILE)
            if status_log:
                return max(status_log, key=lambda x: parse_datetime(x["timestamp"]))
            else:
                return {
                    "timestamp": datetime.now(UTC).strftime(TIMESTAMP_FORMAT),
                    "status": "unhealthy",
                }
        except json.JSONDecodeError as e:
            logger.exception(e)
            raise ValueError(ErrorMessage.INVALID_JSON)

    @check_file_exists(WORKFLOW_LOCAL_RUNNER_STATUS_FILE)
    def update_local_runner_status(
        self,
        timestamp: str,
        status: WorkflowLocalRunnerStatus,
        detailed_status: str | None = None,
        **kwargs,
    ):
        try:
            logger.info(f"updating status of workflows local runner to {status}:{detailed_status}")
            status_log = from_json(WORKFLOW_LOCAL_RUNNER_STATUS_FILE)
            # append status to file at current time
            status_log.append(
                {"timestamp": timestamp, "status": status, "detailed_status": detailed_status}
            )
            # only keep last 500 updates
            status_log = status_log[-500:]
            # write back to file
            to_json(status_log, WORKFLOW_LOCAL_RUNNER_STATUS_FILE)
            return {"success": "true"}
        except json.JSONDecodeError as e:
            logger.exception(e)
            raise ValueError(ErrorMessage.INVALID_JSON)

    def start_local_runner(self, **kwargs):
        try:
            # Update status to starting
            self.update_local_runner_status(
                timestamp=datetime.now(UTC).strftime(TIMESTAMP_FORMAT),
                status=WorkflowLocalRunnerStatus.STARTING,
                detailed_status="Startup requested manually",
            )
            # Use Popen to detach process
            subprocess.Popen(
                ["bash", "/etc/sagemaker-ui/workflows/start-workflows-container.sh"],
                cwd="/",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except Exception as e:
            logger.exception(e)
            raise web.HTTPError(500, ErrorMessage.UNEXPECTED_ERROR % e)
        else:
            # supervisord will handle status update to healthy
            # if local runner successfully starts up
            return {"success": "true"}

    def stop_local_runner(self, **kwargs):
        try:
            # Update status to stopping
            self.update_local_runner_status(
                timestamp=datetime.now(UTC).strftime(TIMESTAMP_FORMAT),
                status=WorkflowLocalRunnerStatus.STOPPING,
                detailed_status="Shutdown requested manually",
            )
            # Use Popen to detach process
            subprocess.Popen(
                ["bash", "/etc/sagemaker-ui/workflows/stop-workflows-container.sh"],
                cwd="/",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except Exception as e:
            logger.exception(e)
            # Update status to unhealthy
            self.update_local_runner_status(
                timestamp=datetime.now(UTC).strftime(TIMESTAMP_FORMAT),
                status=WorkflowLocalRunnerStatus.UNHEALTHY,
                detailed_status="Shutdown failed",
            )
            raise web.HTTPError(500, ErrorMessage.UNEXPECTED_ERROR % e)
        else:
            return {"success": "true"}

    def deploy_project(self, **kwargs):
        """API invoked in Toolkit deployProjectToMWAA()
        - For Git projects, this would
            1. clone the Git repository to a temporary PROJECT_SNAPSHOT_DIR, upload to S3
            2. combine the configuration files Workflows team managed in SMD with customers BYO config files in space,
                save to the temp
                and then upload the combined requirements.txt, startup.sh, packed plugins.zip to the
                S3 paths pre-allocated for MWAA env
            3. Update git hash in the project-files-git-history.json file maintained in S3
        - For Non-Git(S3) projects, this would only perform #2 above
        """
        success = False
        try:
            begin = datetime.now(UTC)
            logger.info("Starting workflows deployment")
            
            if is_git_project():
                logger.info("Deploying Git project")
                (project_s3_path, config_s3_path, metadata_filepath) = determine_s3_paths(self.s3_client)
                if hash_is_deployed(metadata_filepath, self.s3_client):
                    success = "all project files have already been deployed"
                else:
                    git_clone(PROJECT_SNAPSHOT_DIR)
                    upload_directory_to_s3(PROJECT_SNAPSHOT_DIR, project_s3_path)
                    deploy_config_files(config_s3_path=config_s3_path)
                    update_metadata(
                        operation="insert",
                        _dir=PROJECT_SNAPSHOT_DIR,
                        metadata_file_path=metadata_filepath,
                        s3_client=self.s3_client,
                    )
                    success = True
            else:
                logger.info("Deploying S3 storage project")
                user_config_dir = get_shared_directory_path() + WORKFLOWS_CONFIG_DIR
                tmp_config_dir = PROJECT_SNAPSHOT_DIR + WORKFLOWS_CONFIG_DIR
                clone_dir(user_config_dir, tmp_config_dir)
                
                mwaa_config_s3_path = get_shared_project_s3_path() + S3_CONFIG_DIR
                deploy_config_files(config_s3_path=mwaa_config_s3_path)
                success = True
                
            elapsed = datetime.now(UTC) - begin
            logger.info(
                "Completed workflows deployment, "
                + f"took {elapsed.seconds:d}.{int(elapsed.microseconds / 1e3):d} seconds"
            )
                
        except RuntimeError as e:
            logger.exception(e)
            raise web.HTTPError(status_code=500, reason=ErrorMessage.COMMAND_FAILED % str(e))
        except Exception as e:
            logger.exception(e)
            raise web.HTTPError(status_code=500, reason=ErrorMessage.UNEXPECTED_ERROR % str(e))
        finally:
            try:
                # Cleanup the cloned directory, if it exists
                remove_directory(PROJECT_SNAPSHOT_DIR)
            except Exception as e:
                logger.error(f"Failed to cleanup directory {PROJECT_SNAPSHOT_DIR}: {str(e)}")
        return {"success": str(success).lower()}
