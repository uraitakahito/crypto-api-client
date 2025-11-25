from __future__ import annotations

import datetime
import re
import time
from collections.abc import Sequence
from logging import getLogger
from typing import Final

import redis.asyncio as redis
from yarl import URL

from crypto_api_client.errors.exceptions import RateLimitApproachingError
from crypto_api_client.http.http_response_data import HttpResponseData
from crypto_api_client.security.secret_headers import SecretHeaders

from .abstract_request_callback import AbstractRequestCallback
from .rate_limit_key_builder import RateLimitKeyBuilder

logger = getLogger(__name__)


class RedisSharedUrlPatternRateLimiter(AbstractRequestCallback):
    """URL pattern-based rate limiter (fixed window method)

    Shares API call counts for specified URL patterns across multiple clients via Redis.
    Raises RateLimitApproachingError exception when access count is about to exceed `max_safe_count` within `window_seconds`.

    .. warning::
        **Instantiation method**

        Do not call ``__init__()`` directly. Always use the ``create()`` factory method::

            limiter = await RedisSharedUrlPatternRateLimiter.create(
                redis_client=redis_client,
                url_patterns=["v1/ticker"],
            )

    .. note::
        **Design rationale: Why factory method?**

        This class adopts a Fail-fast design. To detect Redis connection problems early,
        it always performs a connection check (``await redis.ping()``) during initialization.

        However, Python's ``__init__()`` is a synchronous method and cannot directly execute async operations.
        Therefore, we provide ``create()`` as an ``async`` factory method that executes health checks
        and returns a fully initialized instance.

    .. warning::
        **Retry configuration recommendation**

        redis-py retries 3 times by default (4 total attempts).
        When creating multiple instances, disabling retries can shorten startup time when Redis connection fails::

            from redis.asyncio.retry import Retry
            from redis.backoff import NoBackoff

            redis_client = redis.Redis(
                host='localhost',
                port=6379,
                retry=Retry(NoBackoff(), 0),  # Disable retries
                socket_connect_timeout=3.0,    # 3 second connection timeout
            )
    """

    DEFAULT_KEY_PREFIX: Final[str] = "RATE_LIMIT:URL_PATTERN"
    DEFAULT_WINDOW_SECONDS: Final[int] = 300
    DEFAULT_MAX_SAFE_COUNT: Final[int] = 200

    def __init__(
        self,
        *,
        redis_client: redis.Redis,
        url_patterns: Sequence[str | re.Pattern[str]],
        window_seconds: int | None = None,
        max_safe_count: int | None = None,
        label: str | None = None,
        key_prefix: str | None = None,
        _skip_health_check: bool = False,
    ) -> None:
        """Internal constructor (do not call directly)

        .. danger::
            Do not call this method directly.
            Use ``await RedisSharedUrlPatternRateLimiter.create(...)`` instead.

        :param redis_client: Redis client
        :type redis_client: redis.Redis
        :param url_patterns: URL patterns to monitor (regex or string)
        :type url_patterns: Sequence[str | re.Pattern[str]]
        :param window_seconds: Rate limit window in seconds
        :type window_seconds: int | None
        :param max_safe_count: Maximum call count allowed within window
        :type max_safe_count: int | None
        :param label: Optional label
        :type label: str | None
        :param key_prefix: Redis key prefix
        :type key_prefix: str | None
        :param _skip_health_check: Skip health check (internal use only)
        :type _skip_health_check: bool
        :raises RuntimeError: If called with _skip_health_check=False
        :raises ValueError: If redis_client is None
        """
        if not _skip_health_check:
            raise RuntimeError(
                "Do not instantiate RedisSharedUrlPatternRateLimiter directly. "
                "Use `await RedisSharedUrlPatternRateLimiter.create(...)` instead."
            )

        if not redis_client:
            raise ValueError("redis_client is required")

        self._redis = redis_client
        self.url_patterns = [
            p if isinstance(p, re.Pattern) else re.compile(p) for p in url_patterns
        ]
        self.window_seconds = (
            window_seconds
            if window_seconds is not None
            else self.DEFAULT_WINDOW_SECONDS
        )
        self.max_safe_count = (
            max_safe_count
            if max_safe_count is not None
            else self.DEFAULT_MAX_SAFE_COUNT
        )
        self.key_prefix = key_prefix or self.DEFAULT_KEY_PREFIX
        self.label = label
        self.limit_exceeded = False
        self._last_known_count = 0  # Cache last retrieved count value

    @classmethod
    async def create(
        cls,
        *,
        redis_client: redis.Redis,
        url_patterns: Sequence[str | re.Pattern[str]],
        window_seconds: int | None = None,
        max_safe_count: int | None = None,
        label: str | None = None,
        key_prefix: str | None = None,
    ) -> RedisSharedUrlPatternRateLimiter:
        """Create rate limiter

        This method is the only official initialization method for ``RedisSharedUrlPatternRateLimiter``.

        :param redis_client: Redis client
        :type redis_client: redis.Redis
        :param url_patterns: URL patterns to monitor (regex or string)
        :type url_patterns: Sequence[str | re.Pattern[str]]
        :param window_seconds: Rate limit window in seconds. Uses DEFAULT_WINDOW_SECONDS if not specified
        :type window_seconds: int | None
        :param max_safe_count: Maximum call count allowed within window. Uses DEFAULT_MAX_SAFE_COUNT if not specified
        :type max_safe_count: int | None
        :param label: Optional label. Auto-generated from patterns if not specified
        :type label: str | None
        :param key_prefix: Redis key prefix. Uses DEFAULT_KEY_PREFIX if not specified
        :type key_prefix: str | None
        :return: Initialized rate limiter (Redis connection verified)
        :rtype: RedisSharedUrlPatternRateLimiter
        :raises redis.ConnectionError: On Redis connection error
        :raises redis.TimeoutError: On Redis connection timeout
        :raises redis.RedisError: On other Redis errors

        Basic usage

        .. code-block:: python

            import redis.asyncio as redis
            from crypto_api_client.callbacks import RedisSharedUrlPatternRateLimiter

            redis_client = redis.Redis(host='localhost', port=6379)

            limiter = await RedisSharedUrlPatternRateLimiter.create(
                redis_client=redis_client,
                url_patterns=["v1/ticker"],
                window_seconds=300,
                max_safe_count=100,
            )

            client = BitFlyerClient(callbacks=[limiter])
        """
        # Skip health check
        instance = cls(
            redis_client=redis_client,
            url_patterns=url_patterns,
            window_seconds=window_seconds,
            max_safe_count=max_safe_count,
            label=label,
            key_prefix=key_prefix,
            _skip_health_check=True,
        )

        await instance._perform_health_check()

        return instance

    async def get_count_async(self) -> int:
        """Get count asynchronously

        :return: Call count in current window
        :rtype: int
        """
        redis_key = self._key()

        # Since decode_responses=False, val is returned as bytes
        val = await self._redis.get(redis_key)
        # int() can directly convert byte strings (UTF-8 encoded) to integers, correctly reading numeric strings saved by non-Python languages
        count = int(val) if val else 0
        self._last_known_count = count  # Update cache

        return count

    async def _incr_count_async(self) -> None:
        """Increment count asynchronously"""
        redis_key = self._key()

        # Transaction processing with pipeline
        pipe = self._redis.pipeline(transaction=True)
        # Best practice: Using INCR command saves numbers as strings while Redis automatically
        # performs numeric conversion internally, ensuring consistent behavior across all languages
        pipe.incr(redis_key, 1)
        pipe.expire(redis_key, self.window_seconds * 2)
        results = await pipe.execute()

        logger.debug(
            "Redis INCR result: key=%s, new_count=%s, expire_set=%s, label=%s, patterns=%s",
            redis_key,
            results[0] if results else "unknown",
            results[1] if len(results) > 1 else "unknown",
            self.label or "auto",
            [p.pattern for p in self.url_patterns],
        )

    async def _perform_health_check(self) -> None:
        """Redis connection health check

        :raises redis.ConnectionError: On Redis connection error
        :raises redis.TimeoutError: On Redis connection timeout
        :raises redis.RedisError: On other Redis errors
        """
        logger.debug(
            "Redis health check start: label=%s, patterns=%s",
            self.label or "auto",
            [p.pattern for p in self.url_patterns],
        )

        try:
            # Explicitly receive ping() return value (for type checker)
            _: bool = await self._redis.ping()  # type: ignore[assignment]

            logger.debug(
                "Redis health check passed: label=%s, key_prefix=%s",
                self.label or "auto",
                self.key_prefix,
            )
        except Exception as e:
            logger.error(
                "Redis health check FAILED: label=%s, error=%s",
                self.label or "auto",
                e,
            )
            raise

    def _key(self) -> str:
        """Generate key for fixed window

        :return: Redis key name corresponding to current window
        :rtype: str
        """
        label = self.label or RateLimitKeyBuilder.generate_label_from_patterns(
            self.url_patterns
        )
        return RateLimitKeyBuilder.build_key(
            self.key_prefix, label, self.window_seconds
        )

    def _matches_pattern(self, path: str) -> bool:
        """Check if path matches pattern

        :param path: Path to check
        :type path: str
        :return: True if matches pattern
        :rtype: bool
        """
        return any(pattern.search(path) for pattern in self.url_patterns)

    async def before_request(
        self,
        url: URL,
        headers: SecretHeaders,
        data: str | None,
    ) -> None:
        """Asynchronous check before request

        :param url: Request URL
        :param headers: Request headers
        :param data: Request body
        :raises RateLimitApproachingError: When rate limit exceeded
        """
        path = url.path
        if not self._matches_pattern(path):
            logger.debug(
                "Rate limit check skipped: url_path=%s (no pattern match), patterns=%s",
                path,
                [p.pattern for p in self.url_patterns],
            )
            return

        count = await self.get_count_async()
        redis_key = self._key()

        if self.max_safe_count <= count:
            self.limit_exceeded = True
            # Include URL pattern information in message
            patterns_str = ", ".join(p.pattern for p in self.url_patterns)

            # Rate limit exceeded log
            logger.debug(
                "Rate limit EXCEEDED: url_path=%s, key=%s, count=%d/%d, window=%ds",
                path,
                redis_key,
                count,
                self.max_safe_count,
                self.window_seconds,
            )

            raise RateLimitApproachingError(
                error_description=(
                    f"URL pattern limit exceeded: {count}/{self.max_safe_count} "
                    f"in {self.window_seconds}s window. Patterns: {patterns_str}"
                )
            )

        self.limit_exceeded = False

        # Rate limit check passed log
        logger.debug(
            "Rate limit check passed: url_path=%s, key=%s, count=%d/%d",
            path,
            redis_key,
            count,
            self.max_safe_count,
        )

    async def after_request(
        self,
        response_data: HttpResponseData,
    ) -> None:
        """Asynchronous processing after response

        :param response_data: Response data
        :type response_data: HttpResponseData
        """
        path = response_data.request_path
        if not self._matches_pattern(path):
            logger.debug(
                "Rate limit increment skipped: request_path=%s (no pattern match), patterns=%s",
                path,
                [p.pattern for p in self.url_patterns],
            )
            return

        redis_key = self._key()
        logger.debug(
            "Rate limit increment: request_path=%s, key=%s, status_code=%d",
            path,
            redis_key,
            response_data.http_status_code,
        )

        await self._incr_count_async()

    def __str__(self) -> str:
        return self._to_string(reset_time=self.reset)

    def __repr__(self) -> str:
        return self._to_string(reset_time=self.reset)

    def _to_string(self, reset_time: datetime.datetime | None) -> str:
        """Convert current state to string"""
        reset_str = reset_time.strftime("%H:%M:%S") if reset_time else "None"
        patterns_str = "[" + ", ".join(p.pattern for p in self.url_patterns) + "]"
        return (
            f"{self._get_count_sync():>3}/{self.max_safe_count:>3},"
            f" period={self.period:>3}, reset={reset_str}, {self.is_limit_exceeded}, patterns={patterns_str},"
            f" {self._key()}"
        )

    def _get_count_sync(self) -> int:
        """Get count synchronously (for display)"""
        # Note: This is for display purposes only, not used for actual rate limit decisions
        return self._last_known_count  # Return cached value

    @property
    def period(self) -> int:
        """Remaining seconds in window"""
        now = int(time.time())
        window_start = (now // self.window_seconds) * self.window_seconds
        return self.window_seconds - (now - window_start)

    @property
    def remaining(self) -> int:
        """Remaining callable count (estimated)"""
        # Calculate from cached value
        return max(0, self.max_safe_count - self._last_known_count)

    @property
    def reset(self) -> datetime.datetime:
        """Next window end time (UTC)"""
        now = int(time.time())
        window_end = ((now // self.window_seconds) + 1) * self.window_seconds
        return datetime.datetime.fromtimestamp(window_end, tz=datetime.UTC)

    @property
    def is_limit_exceeded(self) -> bool:
        """Rate limit exceeded flag"""
        return self.limit_exceeded
