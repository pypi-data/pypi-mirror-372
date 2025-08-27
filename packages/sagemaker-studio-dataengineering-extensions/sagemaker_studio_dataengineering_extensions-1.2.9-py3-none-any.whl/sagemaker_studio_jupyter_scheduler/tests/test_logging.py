import json
import os
import pytest
import logging
from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironmentDetector,
    JupyterLabEnvironment,
)
from unittest.mock import Mock, MagicMock, mock_open, patch, AsyncMock
import botocore
from jupyter_scheduler.exceptions import SchedulerError
from sagemaker_studio_jupyter_scheduler.util.error_util import SageMakerSchedulerError, NoCredentialsSchedulerError, BotoClientSchedulerError
from sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter import InternalMetadataAdapter

from sagemaker_studio_jupyter_scheduler.logging import (
    LOG_FILE_PATH,
    async_with_metrics,
    init_api_operation_logger
)

from sagemaker_studio_jupyter_scheduler.util.constants import (
    LOGGER_NAME,
    LOG_FILE_NAME,
    STUDIO_LOG_FILE_NAME,
    STUDIO_LOG_FILE_PATH,
)
from tornado import web

@patch("logging.FileHandler", autospec=True)
@patch("os.makedirs")
@patch(
    "sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_environment",
    return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
)
def test_log_file_location_standalone(mock_get_sagemaker_environment, mock_makedirs, mock_file_handler):
    init_api_operation_logger(MagicMock())
    mock_file_handler.assert_called_with(os.path.join(LOG_FILE_PATH, LOG_FILE_NAME))
    logging.getLogger(LOGGER_NAME).handlers.clear()
    mock_makedirs.assert_called_with(LOG_FILE_PATH, exist_ok=True)


@patch(
    "sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_environment",
    return_value=JupyterLabEnvironment.SAGEMAKER_STUDIO,
)
@patch("logging.FileHandler", autospec=True)
@patch("os.makedirs")
def test_log_file_location_studio(mock_makedirs, mock_file_handler, mock_detector):
    init_api_operation_logger(MagicMock())
    mock_file_handler.assert_called_with(
        os.path.join(STUDIO_LOG_FILE_PATH, STUDIO_LOG_FILE_NAME)
    )
    logging.getLogger(LOGGER_NAME).handlers.clear()
    mock_makedirs.assert_called_with(STUDIO_LOG_FILE_PATH, exist_ok=True)


@patch(
    "sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_environment",
    return_value=JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB,
)
@patch("logging.FileHandler", autospec=True)
@patch("os.makedirs")
def test_log_file_location_jupyterlab(mock_makedirs, mock_file_handler, mock_detector):
    init_api_operation_logger(MagicMock())
    mock_file_handler.assert_called_with(
        os.path.join(STUDIO_LOG_FILE_PATH, STUDIO_LOG_FILE_NAME)
    )
    logging.getLogger(LOGGER_NAME).handlers.clear()
    mock_makedirs.assert_called_with(STUDIO_LOG_FILE_PATH, exist_ok=True)

MOCK_SAGEMAKER_IMAGE = "jupyter-server-3"
MOCK_NETWORK_ACCESS_TYPE = "VpcOnly"
MOCK_USER_PROFILE_NAME = "sunp"
MOCK_DOMAIN_ID = "d-1a2b3c4d5e6f"
MOCK_ACCOUNT_ID = "123456789012"

TEST_SERVICE_EXCEPTION_CODE = "SomeServiceException"
TEST_HTTP_CODE = 400
TEST_BOTOCORE_EXCEPTION = botocore.exceptions.ClientError(
    {
        "Error": {"Code": TEST_SERVICE_EXCEPTION_CODE, "Message": "No resource found"},
        "ResponseMetadata": {
            "RequestId": "1234567890ABCDEF",
            "HostId": "host ID data will appear here as a hash",
            "HTTPStatusCode": TEST_HTTP_CODE,
            "HTTPHeaders": {"header metadata key/values will appear here"},
            "RetryAttempts": 0,
        },
    },
    "describe_pipeline",
)

NO_CREDS_ERROR_CODE, NO_CREDS_HTTP_CODE = "NoCredentials", "403"
TEST_NO_CREDENTIALS_EXCEPTION = botocore.exceptions.NoCredentialsError()

class TestLogging:
    def _assert_basic_metrics(self, log, error_code, http_code, error, fault):
        log_record = json.loads(log.getMessage())
        assert log_record["AccountId"] == MOCK_ACCOUNT_ID
        assert log_record["UserProfileName"] == MOCK_USER_PROFILE_NAME
        assert log_record["DomainId"] == MOCK_DOMAIN_ID
        assert log_record["HTTPErrorCode"] == http_code
        assert log_record["BotoErrorCode"] == error_code
        assert log_record["Error"] == error
        assert log_record["Fault"] == fault
        assert log_record["Image"] == MOCK_SAGEMAKER_IMAGE
        assert log_record["AppNetworkAccessType"] == MOCK_NETWORK_ACCESS_TYPE

    @patch('sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_image', new_callable=Mock, return_value=MOCK_SAGEMAKER_IMAGE)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_aws_account_id", new_callable=AsyncMock, return_value=MOCK_ACCOUNT_ID)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_user_profile_name", new_callable=Mock, return_value=MOCK_USER_PROFILE_NAME)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_domain_id", new_callable=Mock, return_value=MOCK_DOMAIN_ID)
    @patch('sagemaker_studio_jupyter_scheduler.logging.InternalMetadataAdapter')
    @patch(
        "sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_environment",
        return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
    )
    @pytest.mark.asyncio
    async def test_boto_exception_in_metrics(self, mock_get_sagemaker_environment, mock_adaptor_class, mock_domain_id, mock_user_profile_name, mock_get_account_id, mock_image, caplog):
        # Initialize logger
        init_api_operation_logger(MagicMock())
        logging.getLogger(LOGGER_NAME).propagate = True

        # Set up the return value directly on the method chain
        mock_adaptor_class.return_value.get_app_network_access_type.return_value = MOCK_NETWORK_ACCESS_TYPE

        @async_with_metrics("TestOperation")
        async def test_function(metrics):
            raise TEST_BOTOCORE_EXCEPTION

        try:
            await test_function()
        except Exception as e:
            assert isinstance(e, SchedulerError)
            # swallow the exception, the goal is to test the logs published
            pass
        finally:
            print(caplog.records)
            self._assert_basic_metrics(
                caplog.records[1],
                TEST_SERVICE_EXCEPTION_CODE,
                str(TEST_HTTP_CODE),
                0,
                1,
            )

    @patch('sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_image', new_callable=Mock,
           return_value=MOCK_SAGEMAKER_IMAGE)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_aws_account_id", new_callable=AsyncMock,
           return_value=MOCK_ACCOUNT_ID)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_user_profile_name", new_callable=Mock,
           return_value=MOCK_USER_PROFILE_NAME)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_domain_id", new_callable=Mock,
           return_value=MOCK_DOMAIN_ID)
    @patch('sagemaker_studio_jupyter_scheduler.logging.InternalMetadataAdapter')
    @patch(
        "sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_environment",
        return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
    )
    @pytest.mark.asyncio
    async def test_any_exception_in_metrics(self, mock_get_sagemaker_environment, mock_adaptor_class, mock_domain_id, mock_user_profile_name, mock_get_account_id, mock_image, caplog):
        init_api_operation_logger(MagicMock())
        logging.getLogger(LOGGER_NAME).propagate = True

        # Set up the return value directly on the method chain
        mock_adaptor_class.return_value.get_app_network_access_type.return_value = MOCK_NETWORK_ACCESS_TYPE

        @async_with_metrics("TestOperation")
        async def test_function(metrics):
            1 / 0

        try:
            await test_function()
        except Exception as e:
            # swallow the exception, the goal is to test the logs published
            assert isinstance(e, SchedulerError)
            pass
        finally:
            self._assert_basic_metrics(
                caplog.records[1], "<class 'ZeroDivisionError'>", "500", 0, 1
            )

    @patch('sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_image', new_callable=Mock,
           return_value=MOCK_SAGEMAKER_IMAGE)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_aws_account_id", new_callable=AsyncMock,
           return_value=MOCK_ACCOUNT_ID)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_user_profile_name", new_callable=Mock,
           return_value=MOCK_USER_PROFILE_NAME)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_domain_id", new_callable=Mock,
           return_value=MOCK_DOMAIN_ID)
    @patch('sagemaker_studio_jupyter_scheduler.logging.InternalMetadataAdapter')
    @patch(
        "sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_environment",
        return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
    )
    @pytest.mark.asyncio
    async def test_no_creds_exception_in_metrics(self, mock_get_sagemaker_environment, mock_adaptor_class, mock_domain_id, mock_user_profile_name, mock_get_account_id, mock_image, caplog):
        init_api_operation_logger(MagicMock())
        logging.getLogger(LOGGER_NAME).propagate = True

        # Set up the return value directly on the method chain
        mock_adaptor_class.return_value.get_app_network_access_type.return_value = MOCK_NETWORK_ACCESS_TYPE

        @async_with_metrics("TestOperation")
        async def test_function(metrics):
            raise TEST_NO_CREDENTIALS_EXCEPTION

        try:
            await test_function()
        except Exception as e:
            assert isinstance(e, NoCredentialsSchedulerError)
            # swallow the exception, the goal is to test the logs published
            pass
        finally:
            self._assert_basic_metrics(
                caplog.records[1],
                NO_CREDS_ERROR_CODE,
                str(NO_CREDS_HTTP_CODE),
                0,
                1,
            )

    @patch('sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_image', new_callable=Mock,
           return_value=MOCK_SAGEMAKER_IMAGE)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_aws_account_id", new_callable=AsyncMock,
           return_value=MOCK_ACCOUNT_ID)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_user_profile_name", new_callable=Mock,
           return_value=MOCK_USER_PROFILE_NAME)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_domain_id", new_callable=Mock,
           return_value=MOCK_DOMAIN_ID)
    @patch('sagemaker_studio_jupyter_scheduler.logging.InternalMetadataAdapter')
    @patch(
        "sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_environment",
        return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
    )
    @pytest.mark.asyncio
    async def test_web_http_error_in_metrics(self, mock_get_sagemaker_environment, mock_adaptor_class, mock_domain_id, mock_user_profile_name, mock_get_account_id, mock_image, caplog):
        init_api_operation_logger(MagicMock())
        logging.getLogger(LOGGER_NAME).propagate = True

        # Set up the return value directly on the method chain
        mock_adaptor_class.return_value.get_app_network_access_type.return_value = MOCK_NETWORK_ACCESS_TYPE

        @async_with_metrics("TestOperation")
        async def test_function(metrics):
            raise web.HTTPError(
                401,
                "AccessDeniedException:IAM Role does not have required permission",
            )

        try:
            await test_function()
        except Exception as e:
            # swallow the exception, the goal is to test the logs published
            assert isinstance(e, SchedulerError)
            pass
        finally:
            self._assert_basic_metrics(
                caplog.records[1], "AccessDeniedException", "401", 1, 0
            )

    @pytest.mark.asyncio
    @patch('sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_image', new_callable=Mock,
           return_value=MOCK_SAGEMAKER_IMAGE)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_aws_account_id", new_callable=AsyncMock,
           return_value=MOCK_ACCOUNT_ID)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_user_profile_name", new_callable=Mock,
           return_value=MOCK_USER_PROFILE_NAME)
    @patch("sagemaker_studio_jupyter_scheduler.logging.get_domain_id", new_callable=Mock,
           return_value=MOCK_DOMAIN_ID)
    @patch('sagemaker_studio_jupyter_scheduler.logging.InternalMetadataAdapter')
    @patch(
        "sagemaker_studio_jupyter_scheduler.logging.get_sagemaker_environment",
        return_value=JupyterLabEnvironment.VANILLA_JUPYTERLAB,
    )
    async def test_scheduler_error_in_metrics(self, mock_get_sagemaker_environment, mock_adaptor_class, mock_domain_id, mock_user_profile_name, mock_get_account_id, mock_image, caplog):
        init_api_operation_logger(MagicMock())
        logging.getLogger(LOGGER_NAME).propagate = True

        # Set up the return value directly on the method chain
        mock_adaptor_class.return_value.get_app_network_access_type.return_value = MOCK_NETWORK_ACCESS_TYPE

        @async_with_metrics("TestOperation")
        async def test_function(metrics):
            raise SageMakerSchedulerError(
                "S3RegionMismatch: S3 bucket s3://bucket-name/path must be in region us-east-1, but found in us-west-2"
            )

        try:
            await test_function()
        except Exception as e:
            # swallow the exception, the goal is to test the logs published
            assert isinstance(e, SchedulerError)
            pass
        finally:
            self._assert_basic_metrics(
                caplog.records[1], "S3RegionMismatch", "500", 1, 0
            )
