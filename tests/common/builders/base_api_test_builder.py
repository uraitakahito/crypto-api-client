"""Base test builder class implementing fluent interface pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Type, TypeVar
from unittest.mock import AsyncMock, patch

from crypto_api_client.http.http_response_data import HttpResponseData

from .assertions import Assertion
from .response_builder import ResponseBuilder

T = TypeVar("T")


class BaseApiTestBuilder(ABC, Generic[T]):
    """Base class for API client test builders.

    Provides fluent interface for test setup and execution.
    Subclasses should implement exchange-specific builders.
    """

    def __init__(self, client_class: Type[T], **client_kwargs: Any):
        """Initialize test builder.

        Args:
            client_class: API client class to test
            **client_kwargs: Arguments for client initialization
        """
        self._client_class = client_class
        self._client_kwargs = client_kwargs
        self._client: T | None = None
        self._response_queue: List[HttpResponseData] = []
        self._assertions: List[Assertion] = []
        self._exception_to_raise: Exception | None = None
        self._call_count = 0

    @property
    def response_builder(self) -> ResponseBuilder:
        """Get response builder instance."""
        return ResponseBuilder()

    def with_response(self, response: HttpResponseData) -> BaseApiTestBuilder[T]:
        """Add mock response to queue.

        Args:
            response: HTTP response to return

        Returns:
            Self for method chaining
        """
        self._response_queue.append(response)
        return self

    def with_success_response(
        self,
        body: str,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> BaseApiTestBuilder[T]:
        """Add successful response.

        Args:
            body: Response body (JSON string)
            status_code: HTTP status code (default: 200)
            headers: Response headers

        Returns:
            Self for method chaining
        """
        response = self.response_builder.success(
            http_status_code=status_code, body=body, headers=headers
        )
        return self.with_response(response)

    def with_error_response(
        self, status_code: int, body: str, headers: dict[str, str] | None = None
    ) -> BaseApiTestBuilder[T]:
        """Add error response.

        Args:
            status_code: HTTP error status code
            body: Error response body (already JSON-encoded)
            headers: Response headers

        Returns:
            Self for method chaining
        """
        # Use the success method to avoid double encoding
        response = self.response_builder.success(
            http_status_code=status_code, body=body, headers=headers
        )
        return self.with_response(response)

    def with_exception(self, exception: Exception) -> BaseApiTestBuilder[T]:
        """Configure to raise exception.

        Args:
            exception: Exception to raise

        Returns:
            Self for method chaining
        """
        self._exception_to_raise = exception
        return self

    def expect(self, assertion: Assertion) -> BaseApiTestBuilder[T]:
        """Add assertion to execute after API call.

        Args:
            assertion: Assertion to execute

        Returns:
            Self for method chaining
        """
        self._assertions.append(assertion)
        return self

    async def execute(self, test_method: str, *args: Any, **kwargs: Any) -> Any:
        """Execute test with configured mocks and assertions.

        Args:
            test_method: Name of client method to test
            *args: Positional arguments for method
            **kwargs: Keyword arguments for method

        Returns:
            API response

        Raises:
            RuntimeError: If no mock responses available
        """
        # Initialize client
        self._client = self._client_class(**self._client_kwargs)

        # Setup mock for send_endpoint_request and/or _call_private_api
        # Let validate_response use the real implementation
        mock_contexts = []

        # Check if client has _call_private_api method (for private clients)
        if hasattr(self._client, "_call_private_api"):
            mock_contexts.append(  # type: ignore[reportUnknownMemberType]
                patch.object(self._client, "_call_private_api", new_callable=AsyncMock)  # type: ignore
            )

        # Always mock send_endpoint_request
        mock_contexts.append(  # type: ignore[attr-defined]
            patch.object(self._client, "send_endpoint_request", new_callable=AsyncMock)  # type: ignore
        )

        # Use ExitStack to handle multiple context managers
        from contextlib import ExitStack

        with ExitStack() as stack:
            mocks: List[AsyncMock] = [stack.enter_context(ctx) for ctx in mock_contexts]  # type: ignore

            # Get the primary mock (either _call_private_api or send_endpoint_request)
            mock_send = mocks[0]
            # Configure mock behavior
            if self._exception_to_raise:
                mock_send.side_effect = self._exception_to_raise
            else:

                async def response_with_error_check(
                    *args: Any, **kwargs: Any
                ) -> HttpResponseData:
                    response = await self._get_next_response(*args, **kwargs)
                    # If it's an error response, raise the exception
                    # This simulates the behavior that should happen in the API client
                    if hasattr(response, "http_status_code"):
                        status = response.http_status_code
                        status_int = status
                        if status_int >= 400:
                            # Use the real validate_response method to handle the error
                            if hasattr(self._client, "validate_response"):
                                self._client.validate_response(response)  # type: ignore
                    return response

                mock_send.side_effect = response_with_error_check

            # Execute test method
            method = getattr(self._client, test_method)
            result = await method(*args, **kwargs)

            # Run assertions
            for assertion in self._assertions:
                assertion.validate(result)

            return result

    async def _get_next_response(self, *args: Any, **kwargs: Any) -> HttpResponseData:
        """Get next mock response from queue.

        Returns:
            Next HTTP response

        Raises:
            RuntimeError: If no responses available
        """
        if not self._response_queue:
            raise RuntimeError("No more mock responses available")

        response = self._response_queue.pop(0)
        self._call_count += 1
        return response

    @abstractmethod
    def create_default_client_kwargs(self) -> dict[str, Any]:
        """Create default client initialization arguments.

        Returns:
            Default kwargs for client initialization
        """
        pass
