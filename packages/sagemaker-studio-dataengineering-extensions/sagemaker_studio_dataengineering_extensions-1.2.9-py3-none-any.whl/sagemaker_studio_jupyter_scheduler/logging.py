from functools import wraps
import inspect
import os
import sys
import logging
import logging.handlers
import datetime
from tornado import web
import botocore
import traceback

from aws_embedded_metrics.sinks.stdout_sink import StdoutSink, Sink
from aws_embedded_metrics.logger.metrics_logger import MetricsLogger
from aws_embedded_metrics.logger.metrics_context import MetricsContext
from aws_embedded_metrics.environment.local_environment import LocalEnvironment
from sagemaker_studio_jupyter_scheduler.util.aws_config import get_aws_account_id

from sagemaker_studio_jupyter_scheduler.util.error_util import ErrorMatcher, NoCredentialsSchedulerError, BotoClientSchedulerError, BotoEndpointConnectionSchedulerError
from sagemaker_studio_jupyter_scheduler.util.app_metadata import (
    get_domain_id,
    get_sagemaker_environment,
    get_shared_space_name,
    get_user_profile_name,
    get_sagemaker_image,
)
from sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter import (
    InternalMetadataAdapter,
)

from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironmentDetector,
    JupyterLabEnvironment,
)
from jupyter_scheduler.exceptions import SchedulerError

from sagemaker_studio_jupyter_scheduler.util.stack_trace_filter import StackTraceFilter
from sagemaker_studio_jupyter_scheduler.util.constants import LOGGER_NAME, LOG_FILE_NAME, STUDIO_LOG_FILE_PATH, \
    STUDIO_LOG_FILE_NAME, UNIFIED_STUDIO_LOG_FILE_PATH

HOME_DIR = os.path.expanduser("~")
LOG_FILE_PATH = os.path.join(HOME_DIR, ".sagemaker")

stack_trace_filter = StackTraceFilter()

def init_api_operation_logger(server_log):
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_file_location = os.path.join(LOG_FILE_PATH, LOG_FILE_NAME)
    if (
        get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_STUDIO
        or get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB
    ):
        os.makedirs(STUDIO_LOG_FILE_PATH, exist_ok=True)
        log_file_location = os.path.join(STUDIO_LOG_FILE_PATH, STUDIO_LOG_FILE_NAME)
    elif (get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_UNIFIED_STUDIO):
        os.makedirs(UNIFIED_STUDIO_LOG_FILE_PATH, exist_ok=True)
        log_file_location = os.path.join(UNIFIED_STUDIO_LOG_FILE_PATH, STUDIO_LOG_FILE_NAME)
    else:
        os.makedirs(LOG_FILE_PATH, exist_ok=True)
    server_log.info(f"API file handler Location - {log_file_location}")
    file_handler = logging.FileHandler(log_file_location)
    logger.addHandler(file_handler)
    logger.propagate = False


class LogFileSink(StdoutSink):
    def accept(self, context: MetricsContext) -> None:
        for serialized_content in self.serializer.serialize(context):
            if serialized_content:
                logging.getLogger(LOGGER_NAME).info(serialized_content)

    @staticmethod
    def name() -> str:
        return "LogFileSink"


class LogFileEnvironment(LocalEnvironment):
    def get_sink(self) -> Sink:
        return LogFileSink()


async def resolve_environment():
    return LogFileEnvironment()


def _extract_codes(excep):
    http_code = "500"
    error_code = "InternalError"

    try:
        if isinstance(excep, SchedulerError):
            # this will catch also SagemakerSchedulerError
            # TODO: Add http error code
            # for sagemaker scheduler error we use the following format
            # f"{boto_error.response['Error']['Code']}: {boto_error.response['Error']['Message']}"
            error_code = str(excep).split(":")[0]
        elif isinstance(excep, web.HTTPError):
            http_code = f"{excep.status_code}"
            # we construct the log_message from boto ClientError in error_utils function, so no risk of viewing customer information
            # we always add the delimiter :
            # f"{error.response['Error']['Code']}: {error.response['Error']['Message']}",
            error_code = excep.log_message.split(":")[0]
        elif isinstance(excep, botocore.exceptions.ClientError):
            # we dont wrap all api error in web.HTTPError, so catching it here
            error_code = f"{excep.response['Error']['Code']}"
            http_code = f"{excep.response['ResponseMetadata']['HTTPStatusCode']}"
        elif isinstance(excep, botocore.exceptions.EndpointConnectionError):
            error_code = "503"
            http_code = "EndpointConnectionError"
        elif isinstance(excep, botocore.exceptions.NoCredentialsError):
            http_code = "403"
            error_code = "NoCredentials"
        else:
            http_code = "500"
            error_code = str(type(excep))
    except Exception as e:
        # Logging should not impact main functionality
        # silently fail indicating Internal Error
        error_code = "InternalErrorLogging"
        pass

    return http_code, error_code


if get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_UNIFIED_STUDIO:
    metricNamespace = "SagemakerUnifiedStudioScheduler-JupyterLab"
elif get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB:
    metricNamespace = "SagemakerStudioScheduler-JupyterLab"
else:
    metricNamespace = "SagemakerStudioScheduler"

def async_with_metrics(operation):
    def decorate(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = datetime.datetime.now()
            error = fault = 0
            http_code = "200"
            error_code = "Success"
            is_exception = False
            em = ErrorMatcher()

            context = MetricsContext().empty()
            metrics_logger = MetricsLogger(resolve_environment, context)
            if "metrics" in inspect.signature(func).parameters:
                kwargs["metrics"] = metrics_logger

            try:
                return await func(*args, **kwargs)
            except Exception as excep:
                http_code, error_code = _extract_codes(excep)
                is_exception = True
                # convert to Schedule Error and pass the error message, this will ensure the customers can see the exact error message
                logging.getLogger(LOGGER_NAME).info(excep)
                if isinstance(excep, botocore.exceptions.ClientError):
                    raise BotoClientSchedulerError(excep)
                if isinstance(excep, botocore.exceptions.NoCredentialsError):
                    raise NoCredentialsSchedulerError(excep)
                if isinstance(excep, botocore.exceptions.EndpointConnectionError):
                    raise BotoEndpointConnectionSchedulerError(excep)
                if not isinstance(excep, SchedulerError):
                    raise SchedulerError(excep)
                raise excep
            finally:
                if is_exception:
                    if em.is_fault(str(error_code)):
                        fault = 1
                    else:
                        error = 1
                    stack_trace = traceback.format_exc()
                    context.set_property("StackTrace", stack_trace_filter.filter(stack_trace))
                try:
                    context.namespace = metricNamespace
                    context.should_use_default_dimensions = False
                    context.put_dimensions({"Operation": operation})
                    context.set_property("AccountId", await get_aws_account_id())
                    context.set_property("UserProfileName", get_user_profile_name())
                    context.set_property("SharedSpaceName", get_shared_space_name())
                    context.set_property("DomainId", get_domain_id())
                    context.set_property("HTTPErrorCode", http_code)
                    context.set_property("BotoErrorCode", error_code)
                    context.set_property("Image", get_sagemaker_image())
                    context.set_property("AppNetworkAccessType", InternalMetadataAdapter().get_app_network_access_type())
                    context.put_metric("Error", error, "Count")
                    context.put_metric("Fault", fault, "Count")
                    elapsed = datetime.datetime.now() - start_time
                    context.put_metric(
                        "Latency", int(elapsed.total_seconds() * 1000), "Milliseconds"
                    )
                    await metrics_logger.flush()
                except Exception as excep:
                    # we log and silently fail for the extra information that we add
                    # and not affect any api operations
                    logging.getLogger(LOGGER_NAME).info(excep)
                    pass

        return wrapper

    return decorate
