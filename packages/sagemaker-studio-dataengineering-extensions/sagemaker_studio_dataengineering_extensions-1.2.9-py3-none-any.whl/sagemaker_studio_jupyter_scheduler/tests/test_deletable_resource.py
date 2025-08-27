import pytest
from unittest.mock import Mock, AsyncMock

from sagemaker_studio_jupyter_scheduler.util.deletable_resource import (
    DeletableResourceContainer,
    DeletableResource,
)


@pytest.mark.asyncio
async def test_deletable_resource__multiple_resources__deletes_all():
    # Given
    log = Mock()
    lambda_container = AsyncMock()

    deletable_resources = DeletableResourceContainer(log)
    deletable_resources.add_resource(
        DeletableResource("pipeline", lambda_container.delete_pipeline)
    )
    deletable_resources.add_resource(
        DeletableResource("rule", lambda_container.delete_rule)
    )

    # When
    await deletable_resources.delete_all()

    # Then
    lambda_container.delete_pipeline.assert_called()
    lambda_container.delete_rule.assert_called()


@pytest.mark.asyncio
async def test_deletable_resource__resource_deletion_error__all_resources_deleted():
    # Given
    log = Mock()
    lambda_container = AsyncMock(
        **{"delete_pipeline.side_effect": Exception("Failed to delete pipeline")}
    )

    deletable_resources = DeletableResourceContainer(log)
    deletable_resources.add_resource(
        DeletableResource("pipeline", lambda_container.delete_pipeline)
    )
    deletable_resources.add_resource(
        DeletableResource("rule", lambda_container.delete_rule)
    )

    # When
    await deletable_resources.delete_all()

    # Then
    lambda_container.delete_pipeline.assert_called()
    lambda_container.delete_rule.assert_called()


@pytest.mark.asyncio
async def test_deletable_resource__cleared__no_resources_deleted():
    # Given
    log = Mock()
    lambda_container = AsyncMock()

    deletable_resources = DeletableResourceContainer(log)
    deletable_resources.add_resource(
        DeletableResource("pipeline", lambda_container.delete_pipeline)
    )
    deletable_resources.add_resource(
        DeletableResource("rule", lambda_container.delete_rule)
    )

    # When
    deletable_resources.clear()
    await deletable_resources.delete_all()

    # Then
    lambda_container.delete_pipeline.assert_not_called()
    lambda_container.delete_rule.assert_not_called()
