"""Tests for retry_strategy."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from crypto_api_client.errors.exceptions import RetryLimitExceededError
from crypto_api_client.http._retry_strategy import ExponentialBackoffRetryStrategy


class TestExponentialBackoffRetryStrategy:
    """Tests for ExponentialBackoffRetryStrategy class."""

    def test_init_default_values(self) -> None:
        """Test initialization with default values."""
        strategy: ExponentialBackoffRetryStrategy[Any] = (
            ExponentialBackoffRetryStrategy()
        )
        assert strategy.max_retries == 3
        assert strategy.initial_delay_seconds == 1
        assert strategy.max_delay == 60
        assert strategy.backoff_factor == 2.0
        assert strategy.jitter is True
        assert strategy.exceptions == ()

    def test_init_custom_values(self) -> None:
        """Test initialization with custom values."""
        strategy: ExponentialBackoffRetryStrategy[Any] = (
            ExponentialBackoffRetryStrategy(
                max_retries=5,
                initial_delay_seconds=2,
                max_delay=120,
                backoff_factor=3.0,
                jitter=False,
                exceptions=(ValueError, KeyError),
            )
        )
        assert strategy.max_retries == 5
        assert strategy.initial_delay_seconds == 2
        assert strategy.max_delay == 120
        assert strategy.backoff_factor == 3.0
        assert strategy.jitter is False
        assert strategy.exceptions == (ValueError, KeyError)

    @pytest.mark.asyncio
    async def test_execute_success_first_attempt(self) -> None:
        """Test when first attempt succeeds."""
        strategy: ExponentialBackoffRetryStrategy[Any] = (
            ExponentialBackoffRetryStrategy()
        )
        async_func = AsyncMock(return_value="success")

        result = await strategy.execute(async_func, "arg1", key="value")

        assert result == "success"
        async_func.assert_called_once_with("arg1", key="value")

    @pytest.mark.asyncio
    async def test_execute_retry_on_exception(self) -> None:
        """Test retry on exception."""
        strategy: ExponentialBackoffRetryStrategy[Any] = (
            ExponentialBackoffRetryStrategy(
                max_retries=3,
                initial_delay_seconds=0.1,
                jitter=False,
                exceptions=(ValueError,),
            )
        )

        async_func = AsyncMock()
        async_func.side_effect = [ValueError("error1"), ValueError("error2"), "success"]

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await strategy.execute(async_func)

        assert result == "success"
        assert async_func.call_count == 3
        assert mock_sleep.call_count == 2
        # Verify delay times (jitter=False)
        mock_sleep.assert_any_call(0.1)  # First retry
        mock_sleep.assert_any_call(0.2)  # Second retry (0.1 * 2.0)

    @pytest.mark.asyncio
    async def test_execute_max_retries_exceeded(self) -> None:
        """Test when max retries are exceeded."""
        strategy: ExponentialBackoffRetryStrategy[Any] = (
            ExponentialBackoffRetryStrategy(
                max_retries=2,
                initial_delay_seconds=0.1,
                jitter=False,
                exceptions=(ValueError,),
            )
        )

        async_func = AsyncMock()
        async_func.side_effect = ValueError("persistent error")

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(RetryLimitExceededError) as exc_info:
                await strategy.execute(async_func)

        assert "max retries 2" in str(exc_info.value)
        assert async_func.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_non_retryable_exception(self) -> None:
        """Test non-retryable exception."""
        strategy: ExponentialBackoffRetryStrategy[Any] = (
            ExponentialBackoffRetryStrategy(
                exceptions=(ValueError,)  # Only ValueError is retryable
            )
        )

        async_func = AsyncMock()
        async_func.side_effect = KeyError("not retryable")

        with pytest.raises(KeyError) as exc_info:
            await strategy.execute(async_func)

        assert str(exc_info.value) == "'not retryable'"
        async_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_jitter(self) -> None:
        """Test with jitter enabled."""
        strategy: ExponentialBackoffRetryStrategy[Any] = (
            ExponentialBackoffRetryStrategy(
                max_retries=3,
                initial_delay_seconds=1.0,
                jitter=True,
                exceptions=(ValueError,),
            )
        )

        async_func = AsyncMock()
        async_func.side_effect = [ValueError("error"), "success"]

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            with patch("secrets.SystemRandom.uniform", return_value=0.5):
                result = await strategy.execute(async_func)

        assert result == "success"
        mock_sleep.assert_called_once_with(0.5)  # Value from jitter

    @pytest.mark.asyncio
    async def test_execute_max_delay_cap(self) -> None:
        """Test max delay cap."""
        strategy: ExponentialBackoffRetryStrategy[Any] = (
            ExponentialBackoffRetryStrategy(
                max_retries=5,
                initial_delay_seconds=10,
                max_delay=20,
                backoff_factor=3.0,
                jitter=False,
                exceptions=(ValueError,),
            )
        )

        async_func = AsyncMock()
        async_func.side_effect = [
            ValueError("error1"),
            ValueError("error2"),
            ValueError("error3"),
            "success",
        ]

        delays: list[float] = []

        async def mock_sleep(delay: float) -> None:
            delays.append(delay)

        with patch("asyncio.sleep", side_effect=mock_sleep):
            result = await strategy.execute(async_func)

        assert result == "success"
        assert delays == [10, 20, 20]  # Capped at max delay
