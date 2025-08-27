import json
from unittest.mock import patch, mock_open, MagicMock
import pytest

from sagemaker_jupyter_server_extension.post_startup_handler import (
    SageMakerPostStartupHandler,
    POST_STARTUP_SCRIPT_FILE,
    POST_STARTUP_SCRIPT_STATUS_FILE,
    POST_STARTUP_SCRIPT_LOG_FILE,
)

class MockSageMakerHandler(SageMakerPostStartupHandler):
    def __init__(self):
        self.application = MagicMock()
        self.request = MagicMock()
        self.request.method = 'GET'
        self._transforms = []
        self.set_status = MagicMock()
        self.finish = MagicMock()
        self._current_user = True
        self.get_current_user = MagicMock(return_value=True)
    @property
    def current_user(self):
        return self._current_user

    def get_argument(self, name, default=None):
        return default

    def get_status(self):
        return 200

@pytest.fixture
def handler():
    return MockSageMakerHandler()

@pytest.mark.asyncio
async def test_get_status_success(handler):
    mock_status = {"status": "success", "message": "test message"}
    with patch.object(handler, '_get_post_startup_status', return_value=mock_status):
        await handler.get()
        handler.set_status.assert_called_once_with(200)
        handler.finish.assert_called_once_with(json.dumps(mock_status))

@pytest.mark.asyncio
async def test_get_status_none(handler):
    with patch.object(handler, '_get_post_startup_status', return_value=None):
        await handler.get()
        handler.set_status.assert_called_once_with(200)
        handler.finish.assert_called_once_with({})

def test_get_status_from_file_not_found(handler):
    with patch('builtins.open', side_effect=FileNotFoundError):
        result = handler._get_status_from_file()
        assert result is None

@pytest.mark.asyncio
async def test_get_post_startup_status_success(handler):
    mock_status = {"status": "success", "message": "test message"}
    with patch.object(handler, '_get_status_from_file', return_value=mock_status):
        result = await handler._get_post_startup_status()
        assert result == mock_status

@pytest.mark.asyncio
async def test_get_post_startup_status_timeout(handler):
    with patch.object(handler, '_get_status_from_file', return_value=None), \
         patch('asyncio.sleep', return_value=None), \
         patch('asyncio.get_event_loop') as mock_get_loop:
        mock_loop = MagicMock()
        mock_loop.time.side_effect = [0, 11]  # First call returns 0, second call returns 11 (> 10 second timeout)
        mock_get_loop.return_value = mock_loop
        result = await handler._get_post_startup_status()
        assert result is None

@pytest.mark.asyncio
async def test_wait_with_backoff(handler):
    with patch('asyncio.sleep') as mock_sleep:
        await handler._wait_with_backoff(1)
        mock_sleep.assert_called_once_with(1)  # First attempt should wait 1 second

def test_validate_status_success(handler):
    valid_status = {"status": "success", "message": "test message"}
    assert handler._validate_status(valid_status) is True

def test_validate_status_invalid(handler):
    invalid_status = {"status": "success"}  # Missing 'message' field
    with pytest.raises(ValueError):
        handler._validate_status(invalid_status)
