from unittest.mock import patch

import botocore.exceptions
from jupyter_scheduler.exceptions import SchedulerError

from sagemaker_studio_jupyter_scheduler.util.error_util import ACCESS_DENIED_ERROR_MESSAGE, ErrorMatcher, \
    SageMakerSchedulerError, UNRECOGNIZED_CLIENT_EXCEPTION_ERROR_MESSAGE, \
    NoCredentialsSchedulerError, BotoClientSchedulerError, VPC_ONLY_CONNECTION_ERROR_MESSAGE
from sagemaker_studio_jupyter_scheduler.util.internal_metadata_adapter import InternalMetadataAdapter
from sagemaker_studio_jupyter_scheduler.tests.test_logging import MOCK_NETWORK_ACCESS_TYPE


def test_NoCredentialsSchedulerError():
    # Mock a botocore.exceptions.NoCredentialsError
    no_creds_error = botocore.exceptions.NoCredentialsError(endpoint_url='https://example.com')
 
    # Create a NoCredentialsSchedulerError instance
    error = NoCredentialsSchedulerError(no_creds_error)
 
    # Assert the attributes of the error
    assert error.status_code == 403
    assert error.error_code == "NoCredentials"
    assert error.error_message == f"NoCredentialsError: {no_creds_error}"
    assert str(error) == f"NoCredentialsError: {no_creds_error}"
 
def test_BotoClientSchedulerError():
    # Mock a botocore.exceptions.ClientError
    boto_error = botocore.exceptions.ClientError({
        'Error': {
            'Code': 'AccessDeniedException',
            'Message': 'Access denied'
        },
        'ResponseMetadata': {
            'HTTPStatusCode': 403
        }
    }, 'operation_name')
 
    # Create a BotoClientSchedulerError instance
    error = BotoClientSchedulerError(boto_error)
 
    # Assert the attributes of the error
    assert error.status_code == 403
    assert error.error_code == 'AccessDeniedException'
    assert error.error_message == 'Access denied'
    assert str(error) == 'Access denied'
 
def test_SchedulerError_inheritance():
    # Ensure that the custom errors inherit from the SchedulerError
    assert issubclass(NoCredentialsSchedulerError, SchedulerError)
    assert issubclass(BotoClientSchedulerError, SchedulerError)
 

def test_training_job_validation_error():
    error = botocore.exceptions.ClientError(
        {
            "Error": {
                "Code": "ValidationException",
                "Message": "The request was rejected because the training job is in status Failed",
            }
        },
        "StopTrainingJob",
    )

    assert ErrorMatcher().is_training_job_status_validation_error(error)


def test_scheduler_error_from_boto_error():
    TEST_OPERATION = "CreateTrainingJob"
    TEST_ERROR_CODE = "ValidationException"
    TEST_MESSAGE = "Access denied for repository: sagemaker-base-python-310 in registry ID: 236514542706. Please check if your ECR repository and image exist and role arn:aws:iam::344324978117:role/manual-ui-tests-EMR-SageMakerExecutionRole has proper pull permissions for SageMaker: ecr:BatchCheckLayerAvailability, ecr:BatchGetImage, ecr:GetDownloadUrlForLayer"
    error = botocore.exceptions.ClientError(
        {
            "Error": {
                "Code": TEST_ERROR_CODE,
                "Message": TEST_MESSAGE,
            }
        },
        TEST_OPERATION,
    )
    actual_helpful_message = str(SageMakerSchedulerError.from_boto_error(error))
    assert ACCESS_DENIED_ERROR_MESSAGE in actual_helpful_message
    assert TEST_OPERATION in actual_helpful_message
    assert TEST_MESSAGE in actual_helpful_message


@patch.object(InternalMetadataAdapter, "__init__", return_value=None)
@patch.object(InternalMetadataAdapter, "get_app_network_access_type", return_value=MOCK_NETWORK_ACCESS_TYPE)
def test_scheduler_error_from_connection_error(mock_internal_adaptor_network, mock_internal_adaptor_init):
    # Mock the connection error
    connection_error = botocore.exceptions.ConnectionError(error="Connection refused")

    # Test VPC Only scenario
    error_message = str(SageMakerSchedulerError.from_connection_error(connection_error))

    # Assert VPC specific message is included
    assert "ConnectionError" in error_message
    assert VPC_ONLY_CONNECTION_ERROR_MESSAGE in error_message
    assert str(connection_error) in error_message


@patch.object(InternalMetadataAdapter, "__init__", return_value=None)
@patch.object(InternalMetadataAdapter, "get_app_network_access_type", return_value=MOCK_NETWORK_ACCESS_TYPE)
def test_fault_classification(mock_internal_adaptor_network, mock_internal_adaptor_init):
    FAULT = True
    NOT_FAULT = False
    actual_boto_error_codes_from_prod = {
        "UnauthorizedOperation": NOT_FAULT,
        "Unable to find metadata for image arn in region": FAULT, # needs further investigation to understand the exact cause, till that time it will be marked fault
        "Connect timeout on endpoint URL": FAULT, # needs further investigation to understand the exact cause, till that time it will be marked fault
        "ResourceNotFound": NOT_FAULT,
        "ResourceNotFoundException": NOT_FAULT,
        "Error when retrieving credentials from container-role": FAULT,
        "ExpiredTokenException": FAULT, # ideally customer should never get into this expired token, Studio manages credentials for customers
        "NoSuchBucket": NOT_FAULT,
        "<class 'RuntimeError'>": FAULT,
        "ConnectionError": NOT_FAULT,
    }
    for error_code, expected_fault in actual_boto_error_codes_from_prod.items():
        assert ErrorMatcher().is_fault(error_code) == expected_fault

def test_scheduler_error_from_boto_error_unrecognized_client_exception():
    TEST_OPERATION = "CreateTrainingJob"
    TEST_ERROR_CODE = "UnrecognizedClientException"
    TEST_MESSAGE = "The security token included in the request is invalid."
    error = botocore.exceptions.ClientError(
        {
            "Error": {
                "Code": TEST_ERROR_CODE,
                "Message": TEST_MESSAGE,
            }
        },
        TEST_OPERATION,
    )
    actual_helpful_message = str(SageMakerSchedulerError.from_boto_error(error))
    assert UNRECOGNIZED_CLIENT_EXCEPTION_ERROR_MESSAGE in actual_helpful_message
    assert TEST_ERROR_CODE in actual_helpful_message
    assert TEST_MESSAGE in actual_helpful_message
    assert TEST_OPERATION not in actual_helpful_message