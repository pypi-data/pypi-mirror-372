import re
import shutil
from enum import Enum
from functools import wraps

from tornado.web import HTTPError


class StrEnum(str, Enum):
    def __str__(self):
        return str(self.value)

    def _generate_next_value_(self, *_):
        return self


class ErrorMessage(StrEnum):
    UNEXPECTED_ERROR = "An unexpected error occurred: %s"


def check_sm_spark_cli_exists():
    """
    Decorator to check if the sm-spark-cli command exists.
    This indicates that the Spark history server is installed in the user space.
    If sm-spark-cli exists, continue; otherwise, raise an HTTP 500 error.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            command = 'sm-spark-cli'
            if shutil.which(command) is not None:
                return func(*args, **kwargs)
            else:
                raise HTTPError(500, f"{command} does not exist in the PATH.")

        return wrapper

    return decorator

def is_valid_s3_uri_dir(s3_path):
    s3_uri_dir_regex = re.compile(r'^s3://([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)(?:/([^/]+/)*)?$')
    match = s3_uri_dir_regex.match(s3_path)
    return True if match else False
