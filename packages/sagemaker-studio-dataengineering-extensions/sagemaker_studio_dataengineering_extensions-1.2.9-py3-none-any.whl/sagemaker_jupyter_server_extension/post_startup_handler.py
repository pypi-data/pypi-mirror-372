import json
import logging
import subprocess
import asyncio
from typing import Any, Dict, Optional
from urllib.error import HTTPError

from jupyter_server.extension.handler import ExtensionHandlerMixin
from jupyter_server.base.handlers import APIHandler
import tornado

from functools import lru_cache

from .workflow_utils import (
    check_file_exists
)

logger = logging.getLogger(__name__)
POST_STARTUP_SCRIPT_FILE = "/etc/sagemaker-ui/sagemaker_ui_post_startup.sh"
POST_STARTUP_SCRIPT_STATUS_FILE = "/tmp/.post-startup-status.json"
POST_STARTUP_SCRIPT_LOG_FILE = "/var/log/apps/post_startup_default.log"


class SageMakerPostStartupHandler(ExtensionHandlerMixin, APIHandler):
    """
    This class handles reading from a file that contains a notification written from
    the post-startup script. The post-startup script is run once on space start, with
    status ("in-progress", "error", "success") being written to file in four cases:
    
    1. On start of post startup script execution, "in-progress" is written to file. 
    2. If an error occurs when fetching domain execution role credentials, "error" status
    is written to file with the message: "Network issue detected. Your domain may be using 
    a public subnet, which affects IDE functionality. Please contact your administrator."
    3. If an error occurs elsewhere within the script execution, "error" status is written to
    file with the message "An unexpected error occurred. Please restart your space"
    4. If the post-startup script executes successfully, "success" is written to file.


    """
    CHECK_FOR_STATUS_FILE_TIMEOUT_SECONDS = 10
    STATUS_FILE_POLL_INTERVAL_SECONDS = 1.0
    CHECK_FOR_STATUS_FILE_MAX_RETRIES = 10
    @tornado.web.authenticated
    async def post(self):
        logger.info("received request to execute post startup script")
        result = await self.run_post_startup_script()
        await self.finish(json.dumps(result))

    @check_file_exists(POST_STARTUP_SCRIPT_FILE)
    async def run_post_startup_script(self):
        """
        If POST_STARTUP_SCRIPT_FILE doesn't exist, it will throw FileNotFoundError (404)
        If exists, it will start the execution and add the execution logs in POST_STARTUP_SCRIPT_LOG_FILE.
        """
        try:
            with open(POST_STARTUP_SCRIPT_LOG_FILE, "w+") as log_file:
                subprocess.Popen(
                    ["bash", POST_STARTUP_SCRIPT_FILE],
                    cwd="/",
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                )
        except Exception as e:
            logger.exception("encountered error when attempting to execute post startup script", e)
            raise web.HTTPError(
                500,  ErrorMessage.UNEXPECTED_ERROR % e)
        else:
            logger.info("successfully triggered post startup script")
            return {"success": "true"}
        
    @tornado.web.authenticated
    async def get(self):
        """
        Upon IDE load, sagemaker_post_startup_notification_plugin will make a GET
        request to this handler to check for the presence of a status message
        written to .post_startup_status.json file. It will check for the presence of this
        file for a configured timeout period, and if no file exists after the timeout, 
        will return and log an INFO message. 
        """
        logging.info(f"received request to check status of post startup script")
        try:

            post_startup_status = await self._get_post_startup_status()
            self.set_status(200)
            if post_startup_status is not None: 
                self.finish(json.dumps(post_startup_status))
            else:
                self.finish({})
        except Exception as e:
            logging.exception("Internal Service Error: ", e)
            self.set_status(500)
            self.finish({})

    def _get_status_from_file(self) -> Optional[Dict[str, Any]]:
        try:
            with open(POST_STARTUP_SCRIPT_STATUS_FILE, 'r') as json_file:
                status = json.load(json_file)
                self._validate_status(status)
                return status
        except FileNotFoundError:
            logging.debug("Status file not found")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in status file: {e}")
            return None
        except Exception as e:
            logging.exception(f"Error reading status file: {e}")
            return None

    async def _get_post_startup_status(self):
        """Wait for status file with timeout."""
        start_time = asyncio.get_event_loop().time()
        attempts = 0

        async def _read_status_file():
            return await asyncio.to_thread(self._get_status_from_file)

        while attempts < self.CHECK_FOR_STATUS_FILE_MAX_RETRIES:
            # Run file reading in a separate thread
            status = await _read_status_file()
            
            if status:
                logging.debug(f"Status received: {status}")
                return status

            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > self.CHECK_FOR_STATUS_FILE_TIMEOUT_SECONDS:
                logging.warning(
                    f"Status timeout reached. No status file available after "
                    f"{self.CHECK_FOR_STATUS_FILE_TIMEOUT_SECONDS} seconds"
                )
                return None

            attempts += 1
            await self._wait_with_backoff(attempts)

        return None

    async def _wait_with_backoff(self, attempt: int) -> None:
        """
        Implement exponential backoff for polling.
        Backoff in seconds: 0.5, 1, 2, 4, and 5 afterwards
        """
        wait_time = min(self.STATUS_FILE_POLL_INTERVAL_SECONDS * (2 ** (attempt - 1)), 5)
        await asyncio.sleep(wait_time)

    def _validate_status(self, status: Dict[str, Any]) -> bool:
        """Validate status format."""
        required_fields = ['status', 'message']
        if not all(field in status for field in required_fields):
            raise ValueError("Invalid status format")
        return True
    
