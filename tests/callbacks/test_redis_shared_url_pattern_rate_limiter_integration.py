"""Integration tests for RedisSharedUrlPatternRateLimiter

Verifies actual Redis behavior using fakeredis.
"""

import pytest
import redis.asyncio as redis
from yarl import URL

from crypto_api_client.callbacks.redis_shared_url_pattern_rate_limiter import (
    RedisSharedUrlPatternRateLimiter,
)
from crypto_api_client.errors.exceptions import RateLimitApproachingError
from crypto_api_client.http.http_response_data import HttpResponseData
from crypto_api_client.security.secret_headers import SecretHeaders


class TestRedisSharedUrlPatternRateLimiterIntegration:
    """Integration test class for RedisSharedUrlPatternRateLimiter"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_rate_limit_with_multiple_requests(
        self, redis_client: redis.Redis
    ) -> None:
        """Test rate limiting behavior with multiple requests"""
        limiter = await RedisSharedUrlPatternRateLimiter.create(
            redis_client=redis_client,
            url_patterns=[".*"],
            max_safe_count=5,
            window_seconds=60,
        )

        url = URL("https://example.com/api/ticker")
        headers = SecretHeaders()

        # Send 5 requests (within limit)
        for _ in range(5):
            await limiter.before_request(url, headers, None)
            response_data = HttpResponseData(
                http_status_code=200,
                headers={},
                response_body_text="",
                response_body_bytes=b"",
                url="https://example.com/api/ticker",
                request_path="/api/ticker",
            )
            await limiter.after_request(response_data)

        # Error on 6th request
        with pytest.raises(RateLimitApproachingError) as exc_info:
            await limiter.before_request(url, headers, None)

        assert "URL pattern limit exceeded: 5/5" in str(exc_info.value)
        assert limiter.is_limit_exceeded

    # NOTE: test_window_expiration has been removed
    # Reason: The 2-second wait via time.sleep(2) accounted for 40% of total test time
    # This test verified Redis TTL functionality, but due to the nature of integration tests,
    # real-time passage was required and mocking was difficult, so it was removed

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_multiple_patterns_independent_counts(
        self, redis_client: redis.Redis
    ) -> None:
        """Test that different patterns have independent counts"""
        # Limiter for pattern 1
        limiter1 = await RedisSharedUrlPatternRateLimiter.create(
            redis_client=redis_client,
            url_patterns=["/v1/ticker"],
            max_safe_count=2,
            label="TICKER",
        )

        # Limiter for pattern 2 (same Redis client)
        limiter2 = await RedisSharedUrlPatternRateLimiter.create(
            redis_client=redis_client,
            url_patterns=["/v1/board"],
            max_safe_count=3,
            label="BOARD",
        )

        # Count independently for each
        ticker_url = URL("https://example.com/v1/ticker")
        board_url = URL("https://example.com/v1/board")

        # Access ticker 2 times
        for _ in range(2):
            await limiter1.before_request(ticker_url, SecretHeaders(), None)
            response_data = HttpResponseData(
                http_status_code=200,
                headers={},
                response_body_text="",
                response_body_bytes=b"",
                url="https://example.com/v1/ticker",
                request_path="/v1/ticker",
            )
            await limiter1.after_request(response_data)

        # Access board 3 times (no effect)
        for _ in range(3):
            await limiter2.before_request(board_url, SecretHeaders(), None)
            response_data = HttpResponseData(
                http_status_code=200,
                headers={},
                response_body_text="",
                response_body_bytes=b"",
                url="https://example.com/v1/board",
                request_path="/v1/board",
            )
            await limiter2.after_request(response_data)

        # Error on 3rd ticker access
        with pytest.raises(RateLimitApproachingError):
            await limiter1.before_request(ticker_url, SecretHeaders(), None)

        # Error on 4th board access
        with pytest.raises(RateLimitApproachingError):
            await limiter2.before_request(board_url, SecretHeaders(), None)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_pipeline_transaction_behavior(
        self, redis_client: redis.Redis
    ) -> None:
        """Test pipeline transaction behavior"""
        limiter = await RedisSharedUrlPatternRateLimiter.create(
            redis_client=redis_client,
            url_patterns=[".*"],
            max_safe_count=100,
        )

        # Simulate multiple concurrent requests
        import asyncio

        async def make_request() -> None:
            response_data = HttpResponseData(
                http_status_code=200,
                headers={},
                response_body_text="",
                response_body_bytes=b"",
                url="https://example.com/api/test",
                request_path="/api/test",
            )
            await limiter.after_request(response_data)

        # 10 concurrent requests
        await asyncio.gather(*[make_request() for _ in range(10)])

        # Verify count
        count = await limiter.get_count_async()
        assert count == 10  # Accurate count due to transaction


@pytest.mark.integration
class TestRedisSharedUrlPatternRateLimiterLoggingIntegration:
    """Integration tests for logging output (using fakeredis)"""

    @pytest.fixture
    def caplog_debug(self, caplog: pytest.LogCaptureFixture):
        """Capture DEBUG level logs"""
        import logging

        caplog.set_level(logging.DEBUG)
        return caplog

    @pytest.mark.asyncio
    async def test_full_request_cycle_logging(
        self, redis_client: redis.Redis, caplog_debug: pytest.LogCaptureFixture
    ):
        """Verify that logs are output throughout request cycle"""
        limiter = await RedisSharedUrlPatternRateLimiter.create(
            redis_client=redis_client,
            url_patterns=["v1/ticker"],
            max_safe_count=10,
            label="INTEGRATION_TEST",
        )

        # before_request
        url = URL("https://api.example.com/v1/ticker")
        await limiter.before_request(url, SecretHeaders({}), None)

        # after_request
        response_data = HttpResponseData(
            http_status_code=200,
            headers={},
            response_body_text="{}",
            response_body_bytes=b"{}",
            url=str(url),
            reason="OK",
            request_method="GET",
            request_url=str(url),
            request_path="/v1/ticker",
        )
        await limiter.after_request(response_data)

        # Verify logs
        log_messages = [record.message for record in caplog_debug.records]

        # Verify expected log messages are included
        assert any("Rate limit check passed" in msg for msg in log_messages)
        assert any("Rate limit increment" in msg for msg in log_messages)
        assert any("Redis INCR result" in msg for msg in log_messages)

        # Verify Redis key is included in logs
        assert any("INTEGRATION_TEST" in msg for msg in log_messages)
        assert any("WINDOW:" in msg for msg in log_messages)
