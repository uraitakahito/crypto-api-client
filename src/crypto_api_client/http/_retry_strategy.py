from __future__ import annotations

import asyncio
import secrets
from collections.abc import Callable, Coroutine
from logging import getLogger
from typing import Any, TypeVar

from crypto_api_client.errors.exceptions import RetryLimitExceededError

logger = getLogger(__name__)

T = TypeVar("T")


class ExponentialBackoffRetryStrategy[T]:
    """Class implementing asynchronous exponential backoff retry strategy."""

    def __init__(
        self,
        *,
        max_retries: int = 3,
        initial_delay_seconds: float = 1,
        max_delay: float = 60,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        exceptions: tuple[type[BaseException], ...] = (),
    ) -> None:
        """Initialize asynchronous exponential backoff retry strategy.

        :param max_retries: Maximum number of retries
        :type max_retries: int
        :param initial_delay_seconds: Initial delay in seconds
        :type initial_delay_seconds: float
        :param max_delay: Maximum delay in seconds
        :type max_delay: float
        :param backoff_factor: Exponential multiplier for delay
        :type backoff_factor: float
        :param jitter: Whether to add random element to delay
        :type jitter: bool
        :param exceptions: Exception classes to retry (specified as tuple)
        :type exceptions: tuple[type[BaseException], ...]
        """
        self.max_retries = max_retries
        self.initial_delay_seconds = initial_delay_seconds
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.exceptions = exceptions

    async def execute(
        self,
        func: Callable[..., Coroutine[Any, Any, T]],
        *args: object,
        **kwargs: object,
    ) -> T:
        """Execute specified asynchronous function with exponential backoff.

        :param func: Asynchronous function to execute
        :type func: Callable[..., Coroutine[Any, Any, T]]
        :param args: Positional arguments for the function
        :type args: object
        :param kwargs: Keyword arguments for the function
        :type kwargs: object
        :return: Return value of the function
        :rtype: T
        :raises RetryLimitExceededError: When maximum retries exceeded
        """
        delay = self.initial_delay_seconds

        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if not isinstance(e, self.exceptions):
                    raise

                logger.debug(
                    "Attempt %d/%d failed with exception: %s. Retrying in %.2f seconds...",
                    attempt + 1,
                    self.max_retries,
                    e,
                    delay,
                )

                if attempt == self.max_retries - 1:
                    msg = (
                        f"max retries {self.max_retries}/initial delay {self.initial_delay_seconds}/"
                        f"max delay {self.max_delay}/backoff factor {self.backoff_factor}/jitter {self.jitter}"
                    )
                    raise RetryLimitExceededError(
                        msg,
                    ) from e

                sleep_time = delay
                if self.jitter:
                    sleep_time = secrets.SystemRandom().uniform(0, delay)

                await asyncio.sleep(sleep_time)
                delay = min(delay * self.backoff_factor, self.max_delay)

        # Should never reach here
        error_msg = "Unexpected end of retry loop"
        raise RetryLimitExceededError(error_msg)
