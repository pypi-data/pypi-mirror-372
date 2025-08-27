import os
from unittest.mock import patch

import pytest

from sagemaker_studio_jupyter_scheduler.util.aws_config import get_aws_account_id
from sagemaker_studio_jupyter_scheduler.util.aws_clients import STSAsyncBotoClient


TEST_AWS_ACCOUNT_ID_STUDIO = "898989898989"


@pytest.mark.asyncio
async def test_async_cache_studio_base():
    # Remember old value
    old_aws_account_id = os.getenv("AWS_ACCOUNT_ID")
    # Update environment
    os.environ["AWS_ACCOUNT_ID"] = TEST_AWS_ACCOUNT_ID_STUDIO
    try:
        get_aws_account_id.cache_clear()
        assert await get_aws_account_id() == TEST_AWS_ACCOUNT_ID_STUDIO
    finally:
        # Revert environment back to original state after test
        if old_aws_account_id is None:
            del os.environ["AWS_ACCOUNT_ID"]
        else:
            os.environ["AWS_ACCOUNT_ID"] = old_aws_account_id


@pytest.mark.asyncio
@patch.object(STSAsyncBotoClient, "get_caller_identity")
async def test_async_cache_standalone_multiple_call(mock_sts_identity):
    TEST_ACCOUNT_ID_STANDALONE = 888888888888
    get_aws_account_id.cache_clear()
    mock_sts_identity.return_value = {"Account": TEST_ACCOUNT_ID_STANDALONE}
    assert await get_aws_account_id() == TEST_ACCOUNT_ID_STANDALONE

    # future calls should return from cache and not call aws account
    await get_aws_account_id()
    await get_aws_account_id()

    assert 1 == mock_sts_identity.call_count

    get_aws_account_id.cache_clear()
