"""Test Redis client factory.

Provides factory functions for creating Redis clients to use in test environments.
Adopts a hybrid approach, allowing selection of fakeredis or AsyncMock depending on test purpose.
"""

from typing import Any
from unittest.mock import AsyncMock

import redis.asyncio as redis


def create_test_redis_client(use_fake: bool = True) -> redis.Redis:
    """Create a Redis client for testing.

    Adopts a hybrid approach, allowing selection of fakeredis or
    AsyncMock depending on test purpose.

    :param use_fake: Return fakeredis if True, AsyncMock if False
    :type use_fake: bool
    :return: Test Redis client
    :rtype: redis.Redis

    Why choose a hybrid approach:
    1. Unit tests: AsyncMock for fast execution and error case control
    2. Integration tests: fakeredis to verify actual Redis behavior
    3. Leverage both benefits to build a robust test suite

    Usage examples::

        # For integration tests (fakeredis)
        integration_redis = create_test_redis_client(use_fake=True)

        # For unit tests (AsyncMock)
        unit_redis = create_test_redis_client(use_fake=False)

        # Test error cases
        error_redis = create_test_redis_client(use_fake=False)
        error_redis.get.side_effect = Exception("Connection error")
    """
    if use_fake:
        from fakeredis import FakeAsyncRedis

        return FakeAsyncRedis()
    else:
        # Mock client using AsyncMock
        mock: Any = AsyncMock()
        mock.get.return_value = None
        mock.ping.return_value = True  # For health check

        # Mock setup for pipeline
        pipeline_mock = AsyncMock()
        pipeline_mock.incr.return_value = pipeline_mock
        pipeline_mock.expire.return_value = pipeline_mock
        pipeline_mock.execute.return_value = [1, True]

        mock.pipeline.return_value = pipeline_mock
        return mock
