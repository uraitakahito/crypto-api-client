"""Test builder for callback-related tests."""

import asyncio
from typing import Any, Dict, List, Tuple
from unittest.mock import Mock

from yarl import URL

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.errors.exceptions import RateLimitApproachingError
from crypto_api_client.http.http_response_data import HttpResponseData
from crypto_api_client.security.secret_headers import SecretHeaders


class CallbackTestBuilder:
    """Builder for testing callback functionality."""

    def __init__(self) -> None:
        """Initialize callback test builder."""
        self._callbacks: Tuple[AbstractRequestCallback, ...] = ()
        self._execution_log: List[str] = []
        self._request_url = URL("https://api.example.com/test")
        self._request_headers = SecretHeaders()
        self._request_data: Any | None = None
        self._response_data = HttpResponseData(
            http_status_code=200,
            headers={},
            response_body_text="OK",
            url="https://api.example.com/test",
        )

    def with_logging_callback(self, name: str = "callback") -> "CallbackTestBuilder":
        """Add a logging callback that records execution order.

        Args:
            name: Name prefix for logging entries

        Returns:
            Self for method chaining
        """

        class LoggingCallback(AbstractRequestCallback):
            def __init__(self, log: List[str], prefix: str):
                self.log = log
                self.prefix = prefix

            async def before_request(
                self, url: URL, headers: SecretHeaders, data: str | None
            ) -> None:
                self.log.append(f"{self.prefix}_before")

            async def after_request(self, response_data: HttpResponseData) -> None:  # type: ignore[override]
                self.log.append(f"{self.prefix}_after")

        callback = LoggingCallback(self._execution_log, name)
        self._callbacks = self._callbacks + (callback,)
        return self

    def with_error_callback(
        self,
        error_type: type = ValueError,
        error_message: str = "Callback error",
        on_phase: str = "before",
    ) -> "CallbackTestBuilder":
        """Add a callback that raises an error.

        Args:
            error_type: Type of error to raise
            error_message: Error message
            on_phase: Phase to raise error on ("before" or "after")

        Returns:
            Self for method chaining
        """

        class ErrorCallback(AbstractRequestCallback):
            def __init__(self, err_type: type, err_msg: str, phase: str):
                self.err_type = err_type
                self.err_msg = err_msg
                self.phase = phase

            async def before_request(
                self, url: URL, headers: SecretHeaders, data: str | None
            ) -> None:
                if self.phase == "before":
                    raise self.err_type(self.err_msg)

            async def after_request(self, response_data: HttpResponseData) -> None:  # type: ignore[override]
                if self.phase == "after":
                    raise self.err_type(self.err_msg)

        callback = ErrorCallback(error_type, error_message, on_phase)
        self._callbacks = self._callbacks + (callback,)
        return self

    def with_custom_callback(
        self, callback: AbstractRequestCallback
    ) -> "CallbackTestBuilder":
        """Add a custom callback.

        Args:
            callback: Custom callback instance

        Returns:
            Self for method chaining
        """
        self._callbacks = self._callbacks + (callback,)
        return self

    def with_request_url(self, url: str | URL) -> "CallbackTestBuilder":
        """Set the request URL.

        Args:
            url: Request URL

        Returns:
            Self for method chaining
        """
        self._request_url = URL(url) if isinstance(url, str) else url
        return self

    def with_response_data(
        self,
        status_code: int = 200,
        text: str = "OK",
        headers: Dict[str, str] | None = None,
    ) -> "CallbackTestBuilder":
        """Set the response data.

        Args:
            status_code: HTTP status code
            text: Response text
            headers: Response headers

        Returns:
            Self for method chaining
        """
        self._response_data = HttpResponseData(
            http_status_code=status_code,
            headers=headers or {},
            response_body_text=text,
            url=str(self._request_url),
        )
        return self

    async def execute_callbacks(self) -> List[str]:
        """Execute all callbacks in order.

        Returns:
            Execution log
        """
        # Execute before_request callbacks
        for callback in self._callbacks:
            await callback.before_request(
                self._request_url, self._request_headers, self._request_data
            )

        # Execute after_request callbacks
        for callback in self._callbacks:
            await callback.after_request(self._response_data)

        return self._execution_log

    async def execute_before_callbacks(self) -> List[str]:
        """Execute only before_request callbacks.

        Returns:
            Execution log
        """
        for callback in self._callbacks:
            await callback.before_request(
                self._request_url, self._request_headers, self._request_data
            )

        return self._execution_log

    async def execute_after_callbacks(self) -> List[str]:
        """Execute only after_request callbacks.

        Returns:
            Execution log
        """
        for callback in self._callbacks:
            await callback.after_request(self._response_data)

        return self._execution_log

    def get_callbacks(self) -> Tuple[AbstractRequestCallback, ...]:
        """Get the tuple of callbacks.

        Returns:
            Tuple of callbacks
        """
        return self._callbacks

    def get_execution_log(self) -> List[str]:
        """Get the execution log.

        Returns:
            Execution log
        """
        return self._execution_log


class RedisRateLimiterTestBuilder:
    """Builder for testing Redis-based rate limiter."""

    def __init__(self) -> None:
        """Initialize Redis rate limiter test builder."""
        self._redis_mock = Mock()
        self._url_patterns = [".*"]
        self._window_seconds = 60
        self._max_safe_count = 10
        self._current_count = 0
        self._redis_error: Exception | None = None
        self._setup_redis_mock()

    def _setup_redis_mock(self) -> None:
        """Set up the Redis mock with default behavior."""
        self._redis_mock.get = Mock(return_value=None)

        # Pipeline mock
        pipeline_mock = Mock()
        pipeline_mock.incr = Mock(return_value=pipeline_mock)
        pipeline_mock.expire = Mock(return_value=pipeline_mock)
        pipeline_mock.execute = Mock(return_value=[1, True])

        self._redis_mock.pipeline = Mock(return_value=pipeline_mock)

    def with_url_patterns(self, patterns: List[str]) -> "RedisRateLimiterTestBuilder":
        """Set URL patterns for rate limiting.

        Args:
            patterns: List of regex patterns

        Returns:
            Self for method chaining
        """
        self._url_patterns = patterns
        return self

    def with_window_config(
        self, window_seconds: int, max_safe_count: int
    ) -> "RedisRateLimiterTestBuilder":
        """Configure rate limit window.

        Args:
            window_seconds: Time window in seconds
            max_safe_count: Maximum safe request count

        Returns:
            Self for method chaining
        """
        self._window_seconds = window_seconds
        self._max_safe_count = max_safe_count
        return self

    def with_current_count(self, count: int) -> "RedisRateLimiterTestBuilder":
        """Set the current request count in Redis.

        Args:
            count: Current request count

        Returns:
            Self for method chaining
        """
        self._current_count = count
        self._redis_mock.get.return_value = str(count) if count > 0 else None
        return self

    def with_redis_error(self, error: Exception) -> "RedisRateLimiterTestBuilder":
        """Configure Redis to raise an error.

        Args:
            error: Exception to raise

        Returns:
            Self for method chaining
        """
        self._redis_error = error
        self._redis_mock.get.side_effect = error
        return self

    def with_incremental_counts(
        self, counts: List[int]
    ) -> "RedisRateLimiterTestBuilder":
        """Configure Redis to return incremental counts for successive calls.

        Args:
            counts: List of counts to return

        Returns:
            Self for method chaining
        """

        def get_side_effect(*args: Any) -> str:
            if counts:
                return str(counts.pop(0))
            return str(self._max_safe_count + 1)  # Over limit

        self._redis_mock.get.side_effect = get_side_effect
        return self

    def build_limiter(self) -> Any:
        """Build the rate limiter with current configuration.

        Returns:
            Configured RedisSharedUrlPatternRateLimiter instance
        """
        from crypto_api_client.callbacks import RedisSharedUrlPatternRateLimiter

        return RedisSharedUrlPatternRateLimiter(
            redis_client=None,  # type: ignore[arg-type]
            url_patterns=self._url_patterns,
            window_seconds=self._window_seconds,
            max_safe_count=self._max_safe_count,
        )

    async def test_request(
        self,
        url: str | URL = "https://api.example.com/test",
        expect_error: bool = False,
    ) -> bool:
        """Test a request against the rate limiter.

        Args:
            url: URL to test
            expect_error: Whether to expect a rate limit error

        Returns:
            True if request succeeded, False if rate limited
        """
        limiter = self.build_limiter()
        url = URL(url) if isinstance(url, str) else url

        try:
            await limiter.before_request(url, SecretHeaders(), None)
            return not expect_error
        except RateLimitApproachingError:
            return expect_error
        except RuntimeError as e:
            if self._redis_error and "Failed to connect to Redis" in str(e):
                raise
            raise

    async def test_concurrent_requests(
        self, num_requests: int, base_url: str = "https://api.example.com/test"
    ) -> Dict[str, int]:
        """Test multiple concurrent requests.

        Args:
            num_requests: Number of concurrent requests
            base_url: Base URL for requests

        Returns:
            Dictionary with success and failure counts
        """
        limiter = self.build_limiter()

        async def make_request(i: int) -> bool:
            url = URL(f"{base_url}{i}")
            try:
                await limiter.before_request(url, SecretHeaders(), None)
                return True
            except RateLimitApproachingError:
                return False

        results = await asyncio.gather(
            *[make_request(i) for i in range(num_requests)], return_exceptions=True
        )

        success_count = sum(1 for r in results if r is True)
        fail_count = sum(1 for r in results if r is False)

        return {"success": success_count, "failed": fail_count, "total": num_requests}

    def get_redis_mock(self) -> Mock:
        """Get the Redis mock for assertions.

        Returns:
            Redis mock object
        """
        return self._redis_mock
