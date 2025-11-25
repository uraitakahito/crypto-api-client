"""Tests for error classes."""

import pytest

from crypto_api_client.errors.exceptions import (
    CryptoApiClientError,
    ExchangeApiError,
    RateLimitApproachingError,
    RetryLimitExceededError,
)


class TestCryptoApiClientError:
    """Tests for CryptoApiClientError base class."""

    def test_custom_error_initialization(self) -> None:
        """Verify that error is correctly initialized with custom message."""
        message = "Custom error message"

        error = CryptoApiClientError(error_description=message)

        assert error.error_description == "Custom error message"
        assert str(error) == "Custom error message"

    def test_error_initialization_with_defaults(self) -> None:
        """Verify that error is initialized with default values."""
        error = CryptoApiClientError("Crypto API Client Error")

        assert error.error_description == "Crypto API Client Error"
        assert str(error) == "Crypto API Client Error"

    def test_error_initialization_with_message_only(self) -> None:
        """Verify that error is initialized with message only."""
        message = "Error occurred"

        error = CryptoApiClientError(error_description=message)

        assert error.error_description == message
        assert str(error) == message

    def test_error_hierarchy(self) -> None:
        """Verify that error inherits from Exception."""
        error = CryptoApiClientError("Test error")

        assert isinstance(error, Exception)
        assert isinstance(error, CryptoApiClientError)

    def test_error_with_context_data(self) -> None:
        """Verify that error works correctly when raised and caught."""
        message = "Test exception"

        with pytest.raises(CryptoApiClientError) as exc_info:
            raise CryptoApiClientError(error_description=message)

        caught_error = exc_info.value
        assert caught_error.error_description == "Test exception"
        assert str(caught_error) == "Test exception"


class TestRetryLimitExceededError:
    """Tests for RetryLimitExceededError."""

    def test_retry_limit_error_initialization(self) -> None:
        """Verify that error is initialized with default message."""
        error = RetryLimitExceededError("Retry limit exceeded")

        assert error.error_description == "Retry limit exceeded"
        assert str(error) == "Retry limit exceeded"

    def test_retry_limit_error_with_custom_message(self) -> None:
        """Verify that error is initialized with custom message."""
        message = "Max retries (5) exceeded"

        error = RetryLimitExceededError(error_description=message)

        assert error.error_description == "Max retries (5) exceeded"
        assert str(error) == "Max retries (5) exceeded"

    def test_retry_limit_error_inheritance(self) -> None:
        """Verify that error inherits from CryptoApiClientError."""
        error = RetryLimitExceededError("test")

        assert isinstance(error, CryptoApiClientError)
        assert isinstance(error, RetryLimitExceededError)
        assert isinstance(error, Exception)


class TestRateLimitApproachingError:
    """Tests for RateLimitApproachingError."""

    def test_rate_limit_error_initialization(self) -> None:
        """Verify that error is initialized with default message."""
        error = RateLimitApproachingError("Rate limit approaching.")

        assert error.error_description == "Rate limit approaching."
        assert str(error) == "Rate limit approaching."

    def test_rate_limit_error_with_custom_message(self) -> None:
        """Verify that error is initialized with custom message."""
        message = "API rate limit: 90% used"

        error = RateLimitApproachingError(error_description=message)

        assert error.error_description == "API rate limit: 90% used"
        assert str(error) == "API rate limit: 90% used"

    def test_rate_limit_error_inheritance(self) -> None:
        """Verify that error inherits from CryptoApiClientError."""
        error = RateLimitApproachingError("test")

        assert isinstance(error, CryptoApiClientError)
        assert isinstance(error, RateLimitApproachingError)
        assert isinstance(error, Exception)

    def test_multiple_rate_limit_errors_with_different_messages(self) -> None:
        """Verify that multiple errors with different messages can be distinguished."""
        error1 = RateLimitApproachingError(error_description="Rate limit for endpoint1")
        error2 = RateLimitApproachingError(error_description="Rate limit for endpoint2")

        assert str(error1) != str(error2)


class TestExchangeApiError:
    """Tests for ExchangeApiError."""

    def test_exchange_api_error_with_all_params(self) -> None:
        """Verify that error is initialized with all parameters."""
        error = ExchangeApiError(
            error_description="API error occurred",
            http_status_code=400,
            api_status_code_1="ERROR_001",
            api_status_code_2="INVALID_REQUEST",
            api_error_message_1="Invalid parameter",
            api_error_message_2="The provided parameter is not valid",
            response_body='{"error": "Invalid request"}',
        )

        assert error.error_description == "API error occurred"
        assert error.http_status_code == 400
        assert error.api_status_code_1 == "ERROR_001"
        assert error.api_status_code_2 == "INVALID_REQUEST"
        assert error.api_error_message_1 == "Invalid parameter"
        assert error.api_error_message_2 == "The provided parameter is not valid"
        assert error.response_body == '{"error": "Invalid request"}'
        assert str(error) == "API error occurred"

    def test_exchange_api_error_with_minimal_params(self) -> None:
        """Verify that error is initialized with minimal parameters."""
        error = ExchangeApiError("Simple API error")

        assert error.error_description == "Simple API error"
        assert error.http_status_code is None
        assert error.api_status_code_1 is None
        assert error.api_status_code_2 is None
        assert error.api_error_message_1 is None
        assert error.api_error_message_2 is None
        assert error.response_body is None

    def test_exchange_api_error_inheritance(self) -> None:
        """Verify that error inherits from CryptoApiClientError."""
        error = ExchangeApiError("test")

        assert isinstance(error, CryptoApiClientError)
        assert isinstance(error, ExchangeApiError)
        assert isinstance(error, Exception)
