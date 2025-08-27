import json
import os
import uuid
from unittest.mock import patch, MagicMock

import pytest
import tornado.httpclient
from sagemaker_jupyter_server_extension.debugging_info_handler import (
    SageMakerConnectionDebuggingInfoHandler,
    SUCCESS_FILE_NAME,
    DEBUGGING_INFO_FILE_NAME,
    DEFAULT_DEBUGGING_DIR_TEMPLATE,
)


async def test_debugging_info_handler_invalid_uuid(jp_fetch):
    """Test when cell_id is not a valid UUID."""
    cell_id = "not-a-uuid"
    
    # When
    with pytest.raises(tornado.httpclient.HTTPClientError) as excinfo:
        await jp_fetch("api", "debugging", "info", cell_id)
    
    # Then
    assert excinfo.value.code == 400
    response_json = json.loads(excinfo.value.response.body.decode('utf-8'))
    assert response_json == {"error": "Invalid cell id."}


async def test_debugging_info_handler_folder_not_exists(jp_fetch):
    """Test when debugging folder doesn't exist."""
    cell_id = str(uuid.uuid4())
    
    with patch('os.path.exists', return_value=False):
        # When
        with pytest.raises(tornado.httpclient.HTTPClientError) as excinfo:
            await jp_fetch("api", "debugging", "info", cell_id)
        
        # Then
        assert excinfo.value.code == 404
        response_json = json.loads(excinfo.value.response.body.decode('utf-8'))
        assert response_json == {"error": f"Cannot find debugging path."}


async def test_debugging_info_handler_ready_state(jp_fetch):
    """Test when both success file and debugging file exist."""
    cell_id = str(uuid.uuid4())
    
    def path_exists_side_effect(path):
        if path == DEFAULT_DEBUGGING_DIR_TEMPLATE.format(cell_id=cell_id):
            return True
        elif path.endswith(SUCCESS_FILE_NAME) or path.endswith(DEBUGGING_INFO_FILE_NAME):
            return True
        return False
    
    with patch('os.path.exists', side_effect=path_exists_side_effect):
        # When
        response = await jp_fetch("api", "debugging", "info", cell_id)
        
        # Then
        assert response.code == 200
        payload = json.loads(response.body)
        assert payload == {"status": "ready"}


async def test_debugging_info_handler_in_progress_state(jp_fetch):
    """Test when only debugging file exists but success file doesn't."""
    cell_id = str(uuid.uuid4())
    
    def path_exists_side_effect(path):
        if path == DEFAULT_DEBUGGING_DIR_TEMPLATE.format(cell_id=cell_id):
            return True
        elif path.endswith(SUCCESS_FILE_NAME):
            return False
        elif path.endswith(DEBUGGING_INFO_FILE_NAME):
            return True
        return False
    
    with patch('os.path.exists', side_effect=path_exists_side_effect):
        # When
        response = await jp_fetch("api", "debugging", "info", cell_id)
        
        # Then
        assert response.code == 200
        payload = json.loads(response.body)
        assert payload == {"status": "in_progress"}


async def test_debugging_info_handler_files_removed(jp_fetch):
    """Test when debugging folder exists but files are removed."""
    cell_id = str(uuid.uuid4())
    
    def path_exists_side_effect(path):
        if path == DEFAULT_DEBUGGING_DIR_TEMPLATE.format(cell_id=cell_id):
            return True
        elif path.endswith(SUCCESS_FILE_NAME) or path.endswith(DEBUGGING_INFO_FILE_NAME):
            return False
        return False
    
    with patch('os.path.exists', side_effect=path_exists_side_effect):
        # When
        with pytest.raises(tornado.httpclient.HTTPClientError) as excinfo:
            await jp_fetch("api", "debugging", "info", cell_id)
        
        # Then
        assert excinfo.value.code == 404
        response_json = json.loads(excinfo.value.response.body.decode('utf-8'))
        assert response_json == {"error": "Debugging file has been removed."}


async def test_debugging_info_handler_exception(jp_fetch):
    """Test when an exception occurs during processing."""
    cell_id = str(uuid.uuid4())
    
    with patch('os.path.exists', side_effect=Exception("Test exception")):
        # When
        with pytest.raises(tornado.httpclient.HTTPClientError) as excinfo:
            await jp_fetch("api", "debugging", "info", cell_id)
        
        # Then
        assert excinfo.value.code == 500
        response_json = json.loads(excinfo.value.response.body.decode('utf-8'))
        assert "error" in response_json
        assert "Test exception" in response_json["error"]
