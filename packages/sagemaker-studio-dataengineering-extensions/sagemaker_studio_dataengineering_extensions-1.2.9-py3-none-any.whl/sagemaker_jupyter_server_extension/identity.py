"""SageMaker Identity Provider Class

This extends jupyter_server IdentityProvider interface
to provide the github user name as the user name in SageMaker Unified Studio's IDE.
See link for details on git user name setting in SageMaker Unified Studio:
https://github.com/aws/private-sagemaker-distribution-staging/blob/reinvent-2024-embargoed-release/reinvent-2024-artifacts/build_artifacts/v2/v2.2/v2.2.0/v2.2.0-reinvent2024/dirs/etc/sagemaker-ui/sagemaker_ui_post_startup.sh#L42
"""

import functools
import logging
import subprocess

from jupyter_server.auth.identity import IdentityProvider, User
from jupyter_server.base.handlers import JupyterHandler

logger = logging.getLogger(__name__)

class SageMakerIdentityProvider(IdentityProvider):
    @functools.lru_cache()
    def get_user(self, _handler: JupyterHandler) -> User:
        """Get User Info
        Get Git username and return it as a User type. If not available, fall back to 
        "User" and return as a User type.
        """

        git_username = self.__get_git_username()

        user_id = name = display_name = git_username
        initials = git_username[0].upper()
        color = None
        return User(user_id, name, display_name, initials, None, color)


    @functools.lru_cache()
    def __get_git_username(self):
        try:
            result = subprocess.run(["git", "config", "--get", "user.name"], capture_output=True, text=True, check=True)

            username = result.stdout.strip()
        except subprocess.CalledProcessError as e:
                # only log without throwing
                logger.exception(f"An error occurred while getting user name from git config: {e}")
                username = ""
        
        if not username:
            logger.info("Setting default user name")
            return "User"
        else:
             return username
