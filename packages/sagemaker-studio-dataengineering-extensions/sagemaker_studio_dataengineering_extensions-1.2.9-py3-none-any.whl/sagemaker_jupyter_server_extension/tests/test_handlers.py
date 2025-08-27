import asyncio
import json
import time
from unittest.mock import MagicMock, patch

from sagemaker_jupyter_server_extension.tests.test_connection_utils import (
    get_json_from_file,
    load_test_file_path,
    ordered,
)


async def test_ping(jp_fetch):
    # When
    response = await jp_fetch("sagemaker", "ping")

    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "data": "pong"
    }


async def test_get_connection(jp_fetch):
    with open(load_test_file_path('connection_utils_test/test_metadata.json')) as f:
        metadata_file = f.read()

    with patch('sagemaker_jupyter_server_extension.connection_utils.connection_utils.create_datazone_internal_client') as mock_create_client, \
        patch('sagemaker_jupyter_server_extension.env_handlers.SageMakerEnvHandler.read_metadata_file') as mock_read_metadata_file:
        mock_read_metadata_file.read.return_value = metadata_file
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        list_connection_api_output = get_json_from_file(
            load_test_file_path('connection_utils_test/connection_api_output/list_connection.json'))
        mock_client.list_connections = MagicMock(return_value=list_connection_api_output)

        connection_api_output = get_json_from_file(load_test_file_path('connection_utils_test/connection_api_output/get_connection_emr_ec2.json'))
        mock_client.get_connection = MagicMock(return_value=connection_api_output)

        await assert_get_connection(jp_fetch, connection_api_output)

async def test_list_connections(jp_fetch):
    with open(load_test_file_path('connection_utils_test/test_metadata.json')) as f:
        metadata_file = f.read()

    with patch('sagemaker_jupyter_server_extension.connection_utils.connection_utils.create_datazone_internal_client') as mock_create_client, \
        patch('sagemaker_jupyter_server_extension.env_handlers.SageMakerEnvHandler.read_metadata_file') as mock_read_metadata_file:
        mock_read_metadata_file.read.return_value = metadata_file
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        list_connection_api_output = get_json_from_file(
            load_test_file_path('connection_utils_test/connection_api_output/list_connection.json'))
        mock_client.list_connections = MagicMock(return_value=list_connection_api_output)

        await assert_list_connection(jp_fetch, list_connection_api_output)

def delayed_get_connection(*args, **kwargs):
    time.sleep(3)  # Delay for 3 seconds
    connection_api_output = get_json_from_file(
        load_test_file_path('connection_utils_test/connection_api_output/get_connection_emr_ec2.json'))
    return connection_api_output

def delayed_list_connection(*args, **kwargs):
    time.sleep(3)  # Delay for 3 seconds
    list_connection_api_output = get_json_from_file(
        load_test_file_path('connection_utils_test/connection_api_output/list_connection.json'))
    return list_connection_api_output

async def test_async_handler(jp_fetch):
    with open(load_test_file_path('connection_utils_test/test_metadata.json')) as f:
        metadata_file = f.read()

    with patch('sagemaker_jupyter_server_extension.connection_utils.connection_utils.create_datazone_internal_client') as mock_create_client, \
        patch('sagemaker_jupyter_server_extension.env_handlers.SageMakerEnvHandler.read_metadata_file') as mock_read_metadata_file:
        mock_read_metadata_file.read.return_value = metadata_file
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        list_connection_api_output = get_json_from_file(
            load_test_file_path('connection_utils_test/connection_api_output/list_connection.json'))
        mock_client.list_connections = MagicMock(side_effect=delayed_list_connection)

        connection_api_output = get_json_from_file(
            load_test_file_path('connection_utils_test/connection_api_output/get_connection_emr_ec2.json'))
        mock_client.get_connection = MagicMock(side_effect=delayed_get_connection)

        # Run sequentially
        start_time = time.time()
        await assert_get_connection(jp_fetch, connection_api_output)
        await assert_list_connection(jp_fetch, list_connection_api_output)
        sequential_time = time.time() - start_time

        # Run concurrently
        start_time = time.time()
        await asyncio.gather(assert_get_connection(jp_fetch, connection_api_output), assert_list_connection(jp_fetch, list_connection_api_output))
        concurrent_time = time.time() - start_time

        # Check if concurrent execution is significantly faster
        assert concurrent_time < sequential_time / 1.5, "Functions may not be truly asynchronous"

        print(f"Sequential time: {sequential_time:.2f}s")
        print(f"Concurrent time: {concurrent_time:.2f}s")

async def assert_get_connection(jp_fetch, connection_api_output):
    r = await jp_fetch("api", "aws", "datazone", "connection", method="GET", params={'name': 'default.spark_emr_ec2'})
    response = json.loads(r.body.decode())
    assert ordered(response) == ordered(connection_api_output)

async def assert_list_connection(jp_fetch, list_connection_api_output):
    r = await jp_fetch("api", "aws", "datazone", "connections", method="GET")
    response = json.loads(r.body.decode())
    assert ordered(response) == ordered(list_connection_api_output)

# TODO: Figure out how to set env variables in test.
# async def test_get_session_env(jp_fetch):
#     # When
#     response = await jp_fetch("api", "env")

#     # Then
#     assert response.code == 200
#     payload = json.loads(response.body)
#     assert payload == {'domain_id': "dzd_d3xxovcphmcpzk", 'project_id': "50d2vxs0avlj80", "aws_region": 'us-east-1', 'environment_id': 'dummy_Env_id', 'repository_name': 'dummy_repo', 'user_id': 'dummy_dz_user_id', "dz_endpoint": "https://gateway.us-west-2.beta.api.niceland.aws.dev"}

# TODO: Add test for credential handler. Currently facing issues with: get_frozen_credentials
