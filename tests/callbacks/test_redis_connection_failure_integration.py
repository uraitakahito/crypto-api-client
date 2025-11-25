"""Integration tests for Redis connection failures"""

import time

import pytest
import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import NoBackoff

from crypto_api_client.callbacks.redis_shared_url_pattern_rate_limiter import (
    RedisSharedUrlPatternRateLimiter,
)


class TestRedisConnectionFailureIntegration:
    """Integration test class for Redis connection failures"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_redis_host_raises_connection_error(self) -> None:
        """Test that ConnectionError occurs with invalid Redis host

        Note: health check is executed because initialization happens in async context
        """
        # Connect to non-existent host (no retry, 1 second timeout)
        redis_client = redis.Redis(
            host="nonexistent-redis-host.invalid",
            port=6379,
            retry=Retry(NoBackoff(), 0),  # No retry
            socket_connect_timeout=1.0,  # 1 second timeout
        )

        # ConnectionError or TimeoutError occurs during initialization
        with pytest.raises((redis.ConnectionError, redis.TimeoutError)):
            await RedisSharedUrlPatternRateLimiter.create(
                redis_client=redis_client,
                url_patterns=[".*"],
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_multiple_instances_with_retry_disabled(self) -> None:
        """Performance test for creating multiple instances without retry

        Verify each instance creation fails in about 1 second
        """
        # Redis client without retry
        redis_client = redis.Redis(
            host="nonexistent-redis-host.invalid",
            port=6379,
            retry=Retry(NoBackoff(), 0),  # No retry
            socket_connect_timeout=1.0,  # 1 second timeout
        )

        start = time.time()

        # Attempt to create 3 instances (all fail)
        for i in range(3):
            with pytest.raises((redis.ConnectionError, redis.TimeoutError)):
                await RedisSharedUrlPatternRateLimiter.create(
                    redis_client=redis_client,
                    url_patterns=[f"pattern_{i}"],
                )

        elapsed = time.time() - start

        # Without retry, completes within 4 seconds (1 second each × 3 + margin)
        assert elapsed < 4.0, f"Expected < 4s, got {elapsed:.2f}s"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_connection_refused_error(self) -> None:
        """Test that connection refused error propagates correctly

        Attempt to connect to a port that cannot actually be connected to
        """
        # Port 1 is usually not in use, so connection is refused
        redis_client = redis.Redis(
            host="127.0.0.1",
            port=1,  # Port where connection is refused
            retry=Retry(NoBackoff(), 0),  # No retry
            socket_connect_timeout=1.0,  # 1 second timeout
        )

        # ConnectionError occurs
        with pytest.raises(redis.ConnectionError):
            await RedisSharedUrlPatternRateLimiter.create(
                redis_client=redis_client,
                url_patterns=[".*"],
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fast_failure_with_no_retry(self) -> None:
        """Verify fast failure without retry

        Note: DNS resolution failure occurs immediately,
        so it may fail faster than the actual timeout
        """
        # Client without retry
        client_no_retry = redis.Redis(
            host="nonexistent-redis-host.invalid",
            port=6379,
            retry=Retry(NoBackoff(), 0),
            socket_connect_timeout=1.0,
        )

        # Verify fast failure (within 2 seconds)
        start = time.time()
        with pytest.raises((redis.ConnectionError, redis.TimeoutError)):
            await RedisSharedUrlPatternRateLimiter.create(
                redis_client=client_no_retry,
                url_patterns=[".*"],
            )
        elapsed = time.time() - start

        # Fails within 2 seconds (1 second timeout + margin)
        assert elapsed < 2.0, f"Expected fast failure < 2s, got {elapsed:.2f}s"
