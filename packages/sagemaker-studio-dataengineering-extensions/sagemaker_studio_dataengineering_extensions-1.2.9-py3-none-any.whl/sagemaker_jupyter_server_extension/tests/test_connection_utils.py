import json
import os
import unittest
from unittest.mock import MagicMock, patch

from sagemaker_jupyter_server_extension.connection_utils.connection_utils import get_connection, list_connection


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def get_json_from_file(filepath):
    with open(filepath) as file:
        data = json.load(file)
    return data


def load_test_file_path(filename):
    """Loads the path to a test file.

    Args:
        filename: The name of the test file.

    Returns:
        The absolute path to the test file.
    """

    # Construct the path to the test file
    file_path = os.path.dirname(__file__) + '/test_data/' + filename

    # Check if the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Test file not found: {file_path}")

    return file_path

class TestConnectionUtils(unittest.TestCase):

    def setUp(self):
        with open(load_test_file_path('connection_utils_test/test_metadata.json')) as f:
            self.metadata_file = f.read()

        self.patch_read_metadata_file = patch(
            'sagemaker_jupyter_server_extension.env_handlers.SageMakerEnvHandler.read_metadata_file')
        self.addCleanup(self.patch_read_metadata_file.stop)
        self.mock_read_metadata_file = self.patch_read_metadata_file.start()
        self.mock_read_metadata_file.return_value = json.loads(self.metadata_file)

        with open(load_test_file_path('connection_utils_test/test_storage_metadata.json')) as f:
            self.storage_metadata_file = f.read()

        self.patch_read_storage_metadata_file = patch(
            'sagemaker_jupyter_server_extension.env_handlers.SageMakerEnvHandler.read_storage_metadata_file')
        self.addCleanup(self.patch_read_storage_metadata_file.stop)
        self.mock_read_storage_metadata_file = self.patch_read_storage_metadata_file.start()
        self.mock_read_storage_metadata_file.return_value = json.loads(self.storage_metadata_file)

    @patch('sagemaker_jupyter_server_extension.connection_utils.connection_utils.create_datazone_internal_client')
    def test_list_connection_api(self, mock_create_client):
        connection_api_output = get_json_from_file(load_test_file_path('connection_utils_test/connection_api_output/list_connection.json'))
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_client.list_connections = MagicMock(return_value=connection_api_output)

        res = list_connection()
        self.assertEqual(ordered(res), ordered(connection_api_output))

    def get_connection_api(self, mock_create_client,
                           connection_api_output_file,
                           connection_api_output_with_secret_file,
                           connection_name):
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        list_connection_api_output = get_json_from_file(load_test_file_path('connection_utils_test/connection_api_output/list_connection.json'))
        mock_client.list_connections = MagicMock(return_value=list_connection_api_output)

        connection_api_output = get_json_from_file(connection_api_output_file)
        mock_client.get_connection = MagicMock(return_value=connection_api_output)

        res = get_connection(connection_name)
        self.assertEqual(ordered(res), ordered(connection_api_output))

        # with secret output
        connection_api_output = get_json_from_file(
            connection_api_output_with_secret_file)
        mock_client.get_connection = MagicMock(return_value=connection_api_output)

        res = get_connection(connection_name)
        self.assertEqual(ordered(res), ordered(connection_api_output))

    @patch('sagemaker_jupyter_server_extension.connection_utils.connection_utils.create_datazone_internal_client')
    def test_get_emr_ec2_connection_api(self, mock_create_client):
        self.get_connection_api(mock_create_client,
                                load_test_file_path('connection_utils_test/connection_api_output/get_connection_emr_ec2.json'),
                                load_test_file_path('connection_utils_test/connection_api_output/get_connection_emr_ec2_with_secret.json'),
                                'default.spark_emr_ec2')

    @patch('sagemaker_jupyter_server_extension.connection_utils.connection_utils.create_datazone_internal_client')
    def test_get_emr_serverless_connection_api(self, mock_create_client):
        self.get_connection_api(mock_create_client,
                                load_test_file_path('connection_utils_test/connection_api_output/get_connection_emr_serverless.json'),
                                load_test_file_path('connection_utils_test/connection_api_output/get_connection_emr_serverless_with_secret.json'),
                                'default.spark_emr_serverless')

    @patch('sagemaker_jupyter_server_extension.connection_utils.connection_utils.create_datazone_internal_client')
    def test_get_glue_connection_api(self, mock_create_client):
        self.get_connection_api(mock_create_client,
                                load_test_file_path('connection_utils_test/connection_api_output/get_connection_glue.json'),
                                load_test_file_path('connection_utils_test/connection_api_output/get_connection_glue_with_secret.json'),
                                'default.spark_glue')
