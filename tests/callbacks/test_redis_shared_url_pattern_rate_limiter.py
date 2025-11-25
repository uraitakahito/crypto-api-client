"""Tests for RedisSharedUrlPatternRateLimiter"""

import re
from typing import Any
from unittest.mock import AsyncMock

import pytest
import redis.asyncio as redis
from yarl import URL

from crypto_api_client.callbacks.redis_shared_url_pattern_rate_limiter import (
    RedisSharedUrlPatternRateLimiter,
)
from crypto_api_client.errors.exceptions import RateLimitApproachingError
from crypto_api_client.security.secret_headers import SecretHeaders
from tests.common.mock_helpers import create_mock_http_response_data


def make_response_data(path_url: str = "/v1/ticker"):
    """Create test data in HttpResponseData format"""
    from datetime import timedelta

    return create_mock_http_response_data(
        status_code=200,
        text="{}",
        url=f"https://example.com{path_url}",
        content=b"{}",
        reason="OK",
        elapsed=timedelta(seconds=0.1),
        cookies={},
        encoding="utf-8",
        request_method="GET",
        request_url=f"https://example.com{path_url}",
        request_path=path_url,
    )


class TestRedisSharedUrlPatternRateLimiter:
    """Test class for RedisSharedUrlPatternRateLimiter"""

    @pytest.fixture
    def limiter_factory(
        self, redis_client: redis.Redis
    ) -> callable:  # type: ignore
        """Factory to create limiter in async environment

        Note: RedisSharedUrlPatternRateLimiter must be initialized with create() method.
        """

        async def _create(
            **kwargs: Any,  # type: ignore
        ) -> RedisSharedUrlPatternRateLimiter:
            defaults = {
                "redis_client": redis_client,
                "url_patterns": [".*"],
                "max_safe_count": 200,
            }
            defaults.update(kwargs)
            return await RedisSharedUrlPatternRateLimiter.create(**defaults)

        return _create

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_rate_limit_check(
        self, redis_client: redis.Redis, limiter_factory: callable  # type: ignore
    ) -> None:
        """Async test for rate limit check"""
        redis_client.get.return_value = b"199"  # Just before limit  # type: ignore
        redis_client.ping = AsyncMock(return_value=True)

        limiter = await limiter_factory()

        # Request within limit
        await limiter.before_request(
            URL("https://example.com/api/ticker"), SecretHeaders(), None
        )

        assert not limiter.limit_exceeded

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_count_and_cache(
        self, redis_client: redis.Redis, limiter_factory: callable  # type: ignore
    ) -> None:
        """Test count retrieval and caching functionality"""
        redis_client.get.return_value = b"42"  # type: ignore
        redis_client.ping = AsyncMock(return_value=True)

        limiter = await limiter_factory(
            url_patterns=[re.compile(r"/v1/ticker")],
            window_seconds=60,
            max_safe_count=100,
        )

        # Initially cache is 0
        assert limiter._get_count_sync() == 0  # type: ignore

        # Get count (cache is updated internally)
        count = await limiter.get_count_async()
        assert count == 42

        # Cache has been updated
        assert limiter._get_count_sync()  # type: ignore == 42
        assert limiter.remaining == 58  # 100 - 42

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_pattern_matching(
        self, redis_client: redis.Redis, limiter_factory: callable  # type: ignore
    ) -> None:
        """Test URL pattern matching functionality"""
        redis_client.ping = AsyncMock(return_value=True)

        limiter = await limiter_factory(
            url_patterns=[re.compile(r"/v1/ticker"), "/v1/board"],
        )

        assert limiter._matches_pattern("/v1/ticker")  # type: ignore
        assert limiter._matches_pattern("/v1/board")  # type: ignore
        assert not limiter._matches_pattern("/v1/executions")  # type: ignore

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_after_request_increments(
        self, redis_client: redis.Redis, limiter_factory: callable  # type: ignore
    ) -> None:
        """Test that count is incremented in after_request"""
        # Mock pipeline
        from unittest.mock import MagicMock

        pipeline_mock = MagicMock()  # Use MagicMock instead of AsyncMock
        pipeline_mock.incr.return_value = pipeline_mock
        pipeline_mock.expire.return_value = pipeline_mock
        pipeline_mock.execute = AsyncMock(return_value=[1, True])

        # Mock pipeline method to return pipeline synchronously
        redis_client.pipeline = lambda transaction=True: pipeline_mock  # type: ignore
        redis_client.ping = AsyncMock(return_value=True)

        limiter = await limiter_factory(
            url_patterns=[re.compile(r"/v1/ticker")],
        )

        response_data = make_response_data("/v1/ticker")
        await limiter.after_request(response_data)

        # Verify pipeline was executed
        pipeline_mock.incr.assert_called_once()
        pipeline_mock.expire.assert_called_once()
        pipeline_mock.execute.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_before_request_limit_exceeded(
        self, redis_client: redis.Redis, limiter_factory: callable  # type: ignore
    ) -> None:
        """Test behavior when rate limit is exceeded"""
        redis_client.get.return_value = b"200"  # Equal to limit  # type: ignore
        redis_client.ping = AsyncMock(return_value=True)

        limiter = await limiter_factory(
            url_patterns=[re.compile(r"/v1/ticker")],
            max_safe_count=200,
        )

        url = URL("https://example.com/v1/ticker")
        headers = SecretHeaders()

        # Exception is raised when rate limit is exceeded
        with pytest.raises(RateLimitApproachingError) as exc_info:
            await limiter.before_request(url, headers, None)

        assert "URL pattern limit exceeded: 200/200" in str(exc_info.value)
        assert limiter.is_limit_exceeded

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_string_representation(
        self, redis_client: redis.Redis, limiter_factory: callable  # type: ignore
    ) -> None:
        """Test string representation"""
        redis_client.get.return_value = b"50"  # type: ignore
        redis_client.ping = AsyncMock(return_value=True)

        limiter = await limiter_factory(
            url_patterns=["/v1/.*"],
            max_safe_count=100,
            window_seconds=300,
            label="TEST",
        )

        # Get count and update cache
        await limiter.get_count_async()

        # Verify string representation
        str_repr = str(limiter)
        assert " 50/100" in str_repr
        assert "TEST" in limiter._key()  # type: ignore
        assert "[/v1/.*]" in str_repr

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_label_generation(
        self, redis_client: redis.Redis, limiter_factory: callable  # type: ignore
    ) -> None:
        """Test automatic label generation"""
        from crypto_api_client.callbacks.rate_limit_key_builder import (
            RateLimitKeyBuilder,
        )

        redis_client.ping = AsyncMock(return_value=True)

        limiter = await limiter_factory(
            url_patterns=["/v1/ticker", "/v1/board"],
        )

        # Generate label using RateLimitKeyBuilder
        label = RateLimitKeyBuilder.generate_label_from_patterns(limiter.url_patterns)
        assert label.startswith("PATTERN_")
        assert len(label) == 16  # PATTERN_ + 8-character hash

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_initialization_without_redis_client(self) -> None:
        """Test initialization error without Redis client"""
        with pytest.raises(ValueError) as exc_info:
            await RedisSharedUrlPatternRateLimiter.create(
                redis_client=None,  # type: ignore
                url_patterns=[".*"],
            )

        assert "redis_client is required" in str(exc_info.value)


class TestRedisConnectionFailureDetection:
    """Test class for Redis connection failure detection"""

    @pytest.mark.unit
    def test_direct_init_raises_error(self) -> None:
        """Test that calling __init__() directly raises RuntimeError"""
        from unittest.mock import MagicMock

        mock_redis = MagicMock(spec=redis.Redis)

        with pytest.raises(
            RuntimeError,
            match="Do not instantiate RedisSharedUrlPatternRateLimiter directly",
        ):
            RedisSharedUrlPatternRateLimiter(
                redis_client=mock_redis,
                url_patterns=[".*"],
            )

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_calls_health_check(self) -> None:
        """Test that create() calls health check"""
        from unittest.mock import MagicMock

        mock_redis = MagicMock(spec=redis.Redis)
        mock_redis.ping = AsyncMock(return_value=True)

        limiter = await RedisSharedUrlPatternRateLimiter.create(
            redis_client=mock_redis,
            url_patterns=[".*"],
        )

        # Verify PING was called
        mock_redis.ping.assert_called_once()
        assert limiter is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_propagates_connection_error(self) -> None:
        """Test that create() propagates ConnectionError"""
        from unittest.mock import MagicMock

        mock_redis = MagicMock(spec=redis.Redis)
        mock_redis.ping = AsyncMock(
            side_effect=redis.ConnectionError("Connection refused")
        )

        with pytest.raises(redis.ConnectionError, match="Connection refused"):
            await RedisSharedUrlPatternRateLimiter.create(
                redis_client=mock_redis,
                url_patterns=[".*"],
            )

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_propagates_timeout_error(self) -> None:
        """Test that create() propagates TimeoutError"""
        from unittest.mock import MagicMock

        mock_redis = MagicMock(spec=redis.Redis)
        mock_redis.ping = AsyncMock(side_effect=redis.TimeoutError("Timeout"))

        with pytest.raises(redis.TimeoutError, match="Timeout"):
            await RedisSharedUrlPatternRateLimiter.create(
                redis_client=mock_redis,
                url_patterns=[".*"],
            )

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_count_async_propagates_errors(self) -> None:
        """Test that get_count_async propagates Redis errors"""
        from unittest.mock import MagicMock

        mock_redis = MagicMock(spec=redis.Redis)
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.get = AsyncMock(
            side_effect=redis.ConnectionError("Connection lost")
        )

        # Initialize with create() (health check executed)
        limiter = await RedisSharedUrlPatternRateLimiter.create(
            redis_client=mock_redis,
            url_patterns=[".*"],
        )

        # Error is propagated in get_count_async
        with pytest.raises(redis.ConnectionError, match="Connection lost"):
            await limiter.get_count_async()


@pytest.mark.unit
class TestRedisSharedUrlPatternRateLimiterLogging:
    """Tests for logging functionality"""

    @pytest.fixture
    def mock_logger(self):
        """Mock logger"""
        from unittest.mock import patch

        with patch(
            "crypto_api_client.callbacks.redis_shared_url_pattern_rate_limiter.logger"
        ) as mock:
            yield mock

    async def test_incr_count_async_logs_debug(
        self, mock_logger: Any, redis_client: redis.Redis
    ):
        """Verify that _incr_count_async() outputs DEBUG logs"""
        from unittest.mock import MagicMock

        limiter = await RedisSharedUrlPatternRateLimiter.create(
            redis_client=redis_client,
            url_patterns=["v1/ticker"],
            label="TEST",
        )

        # Setup Redis mock
        mock_pipeline = MagicMock()
        mock_pipeline.execute = AsyncMock(return_value=[6, True])
        redis_client.pipeline = MagicMock(return_value=mock_pipeline)  # type: ignore

        await limiter._incr_count_async()

        # Verify DEBUG logs are called (after operation only)
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        assert any("Redis INCR result" in str(call) for call in debug_calls)

    async def test_before_request_logs_debug_on_limit_exceeded(
        self, mock_logger: Any, redis_client: redis.Redis
    ):
        """Verify that DEBUG logs are output when rate limit is exceeded"""
        limiter = await RedisSharedUrlPatternRateLimiter.create(
            redis_client=redis_client,
            url_patterns=["v1/ticker"],
            max_safe_count=5,
            label="TEST",
        )

        # Setup Redis mock (return value exceeding limit)
        redis_client.get = AsyncMock(return_value=b"10")  # type: ignore

        url = URL("https://api.example.com/v1/ticker")

        with pytest.raises(RateLimitApproachingError):
            await limiter.before_request(url, SecretHeaders({}), None)

        # Verify "EXCEEDED" is recorded in DEBUG logs
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        assert any("Rate limit EXCEEDED" in str(call) for call in debug_calls)

    async def test_before_request_logs_passed_when_under_limit(
        self, mock_logger: Any, redis_client: redis.Redis
    ):
        """Verify that DEBUG logs are output when within rate limit"""
        limiter = await RedisSharedUrlPatternRateLimiter.create(
            redis_client=redis_client,
            url_patterns=["v1/ticker"],
            max_safe_count=100,
            label="TEST",
        )

        # Setup Redis mock (return value within limit)
        redis_client.get = AsyncMock(return_value=b"5")  # type: ignore

        url = URL("https://api.example.com/v1/ticker")

        await limiter.before_request(url, SecretHeaders({}), None)

        # Verify "passed" is recorded in DEBUG logs
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        assert any("Rate limit check passed" in str(call) for call in debug_calls)

    async def test_health_check_logs_on_success(
        self, mock_logger: Any, redis_client: redis.Redis
    ):
        """Verify that DEBUG logs are output on successful health check"""
        redis_client.ping = AsyncMock(return_value=True)  # type: ignore

        await RedisSharedUrlPatternRateLimiter.create(
            redis_client=redis_client,
            url_patterns=["v1/ticker"],
            label="TEST",
        )

        # Verify "health check passed" is recorded in DEBUG logs
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        assert any("Redis health check start" in str(call) for call in debug_calls)
        assert any("Redis health check passed" in str(call) for call in debug_calls)

    async def test_health_check_logs_on_failure(
        self, mock_logger: Any, redis_client: redis.Redis
    ):
        """Verify that ERROR logs are output on failed health check"""
        redis_client.ping = AsyncMock(  # type: ignore
            side_effect=redis.ConnectionError("Connection refused")
        )

        with pytest.raises(redis.ConnectionError):
            await RedisSharedUrlPatternRateLimiter.create(
                redis_client=redis_client,
                url_patterns=["v1/ticker"],
                label="TEST",
            )

        # Verify ERROR logs are called
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Redis health check FAILED" in error_call
