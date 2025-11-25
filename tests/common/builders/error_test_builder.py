"""Error handling test builder for unified error testing pattern."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Type

import pytest

from crypto_api_client.http.http_response_data import HttpResponseData

from .base_api_test_builder import BaseApiTestBuilder


class ErrorTestBuilder(BaseApiTestBuilder[Any]):
    """Builder for error handling tests across all exchanges.

    This builder provides a fluent interface for testing error handling
    behavior consistently across different exchange implementations.
    """

    def __init__(self, client_class: Type[Any], **client_kwargs: Any):
        """Initialize error test builder.

        Args:
            client_class: API client class to test
            **client_kwargs: Arguments for client initialization
        """
        super().__init__(client_class, **client_kwargs)
        self._expected_exception: Type[Exception] | None = None
        self._expected_message: str | None = None
        self._expected_http_status: int | None = None
        self._expected_api_status: int | None = None
        self._expected_api_message: str | None = None
        self._response_validator_class: Type[Any] | None = None

    def create_default_client_kwargs(self) -> dict[str, Any]:
        """Create default client initialization arguments."""
        return {}

    def with_response_validator(self, validator_class: Type[Any]) -> ErrorTestBuilder:
        """Set the ResponseValidator class to test.

        Args:
            validator_class: ResponseValidator class

        Returns:
            Self for method chaining
        """
        self._response_validator_class = validator_class
        return self

    def expect_exception(
        self, exception_type: Type[Exception], message_contains: str | None = None
    ) -> ErrorTestBuilder:
        """Expect specific exception to be raised.

        Args:
            exception_type: Expected exception type
            message_contains: String that should be in error message

        Returns:
            Self for method chaining
        """
        self._expected_exception = exception_type
        self._expected_message = message_contains
        return self

    def expect_http_status(self, status: int) -> ErrorTestBuilder:
        """Expect specific HTTP status in error.

        Args:
            status: Expected HTTP status (int)

        Returns:
            Self for method chaining
        """
        self._expected_http_status = status
        return self

    def expect_api_status(
        self, status: int, message: str | None = None
    ) -> ErrorTestBuilder:
        """Expect specific API status and message.

        Args:
            status: Expected API-specific status code
            message: Expected API-specific error message

        Returns:
            Self for method chaining
        """
        self._expected_api_status = status
        self._expected_api_message = message
        return self

    def expect_api_message(self, message: str) -> ErrorTestBuilder:
        """Expect specific API error message.

        Args:
            message: Expected API-specific error message

        Returns:
            Self for method chaining
        """
        self._expected_api_message = message
        return self

    def with_rate_limit_error(
        self, retry_after: int | None = None, message: str = "Rate limit exceeded"
    ) -> ErrorTestBuilder:
        """Add rate limit error response.

        Args:
            retry_after: Retry-After header value in seconds
            message: Error message

        Returns:
            Self for method chaining
        """
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)

        response = self.response_builder.rate_limit_error(message=message)
        return self.with_response(response)  # type: ignore

    def with_authentication_error(
        self, message: str = "Authentication failed"
    ) -> ErrorTestBuilder:
        """Add authentication error response.

        Args:
            message: Error message

        Returns:
            Self for method chaining
        """
        response = self.response_builder.error(http_status_code=401, message=message)
        return self.with_response(response)  # type: ignore

    def with_validation_error(
        self, message: str = "Validation failed", field: str | None = None
    ) -> ErrorTestBuilder:
        """Add validation error response.

        Args:
            message: Error message
            field: Field that failed validation

        Returns:
            Self for method chaining
        """
        body = {"error": message}
        if field:
            body["field"] = field

        response = self.response_builder.error(http_status_code=400, message=message)
        return self.with_response(response)  # type: ignore

    def with_server_error(
        self, message: str = "Internal server error"
    ) -> ErrorTestBuilder:
        """Add server error response.

        Args:
            message: Error message

        Returns:
            Self for method chaining
        """
        response = self.response_builder.server_error(message=message)
        return self.with_response(response)  # type: ignore

    async def assert_raises(self, test_method: str, *args: Any, **kwargs: Any) -> None:
        """Execute test and assert that expected exception is raised.

        Args:
            test_method: Name of client method to test
            *args: Positional arguments for method
            **kwargs: Keyword arguments for method

        Raises:
            AssertionError: If expected exception is not raised
        """
        if not self._expected_exception:
            raise ValueError("Expected exception not set. Use expect_exception().")

        with pytest.raises(self._expected_exception) as exc_info:
            await self.execute(test_method, *args, **kwargs)

        # Validate exception attributes
        exception = exc_info.value

        if self._expected_message:
            assert self._expected_message in str(exception), (
                f"Expected message '{self._expected_message}' not found in '{str(exception)}'"
            )

        # Check HTTP status if exception has it
        if self._expected_http_status and hasattr(exception, "http_status"):
            assert getattr(exception, "http_status") == self._expected_http_status, (
                f"Expected HTTP status {self._expected_http_status}, got {getattr(exception, 'http_status')}"
            )

        # Check API status if exception has it
        if self._expected_api_status is not None and hasattr(exception, "api_status"):
            assert getattr(exception, "api_status") == self._expected_api_status, (
                f"Expected API status {self._expected_api_status}, got {getattr(exception, 'api_status')}"
            )

        if self._expected_api_message and hasattr(exception, "api_message"):
            assert getattr(exception, "api_message") == self._expected_api_message, (
                f"Expected API message '{self._expected_api_message}', got '{getattr(exception, 'api_message')}'"
            )

    def test_response_validator(self, response: HttpResponseData) -> None:
        """Test ResponseValidator directly.

        Args:
            response: HTTP response to test

        Raises:
            ValueError: If response validator class not set
        """
        if not self._response_validator_class:
            raise ValueError("Response validator class not set. Use with_response_validator().")

        validator = self._response_validator_class()

        if self._expected_exception:
            with pytest.raises(self._expected_exception) as exc_info:
                validator.validate_response(response)

            # Validate exception
            exception = exc_info.value
            if self._expected_message:
                assert self._expected_message in str(exception)
        else:
            # Should not raise for success responses
            validator.validate_response(response)


class ExchangeErrorTestBuilder(ErrorTestBuilder):
    """Base class for exchange-specific error test builders.

    Subclasses should implement exchange-specific error response formats.
    """

    @abstractmethod
    def with_exchange_error_response(
        self, status_code: int, **kwargs: Any
    ) -> ExchangeErrorTestBuilder:
        """Add exchange-specific error response.

        Args:
            status_code: HTTP status code
            **kwargs: Exchange-specific error fields

        Returns:
            Self for method chaining
        """
        pass
