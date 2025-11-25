"""Mock helper for simplifying HTTP request mocking in tests."""

from typing import Any, List
from unittest.mock import AsyncMock, patch

from crypto_api_client.http.http_response_data import HttpResponseData


class MockHelper:
    """Helper class for mocking HTTP requests.

    Provides mock functionality through simple composition without using inheritance.
    """

    def __init__(self):
        """Initialize MockHelper."""
        self.response_queue: List[HttpResponseData] = []
        self.call_count: int = 0
        self.captured_requests: List[dict[str, Any]] = []

    def add_response(self, response: HttpResponseData) -> "MockHelper":
        """Add response to queue.

        Args:
            response: HTTP response to add

        Returns:
            Self for method chaining
        """
        self.response_queue.append(response)
        return self

    def add_responses(self, *responses: HttpResponseData) -> "MockHelper":
        """Add multiple responses to queue at once.

        Args:
            *responses: HTTP responses to add

        Returns:
            Self for method chaining
        """
        self.response_queue.extend(responses)
        return self

    async def get_next_response(self, *args: Any, **kwargs: Any) -> HttpResponseData:
        """Get next mock response.

        Args:
            *args: Request arguments (for recording)
            **kwargs: Request keyword arguments (for recording)

        Returns:
            Next HTTP response

        Raises:
            RuntimeError: When no responses remain
        """
        if not self.response_queue:
            raise RuntimeError(
                f"No more mock responses available. "
                f"Called {self.call_count} times so far."
            )

        # Record request
        self.captured_requests.append(
            {"args": args, "kwargs": kwargs, "call_index": self.call_count}
        )

        self.call_count += 1
        return self.response_queue.pop(0)

    def create_mock_client_method(
        self, client: Any, method_name: str = "send_endpoint_request"
    ) -> AsyncMock:
        """Create mock of client method.

        Args:
            client: Client to mock
            method_name: Method name to mock

        Returns:
            Configured AsyncMock
        """
        mock = AsyncMock()
        mock.side_effect = self.get_next_response
        setattr(client, method_name, mock)
        return mock

    def patch_client_method(
        self, client_path: str, method_name: str = "send_endpoint_request"
    ):
        """Return context manager that patches client method.

        Args:
            client_path: Import path of client
            method_name: Method name to mock

        Returns:
            patch context manager

        Example:
            with mock_helper.patch_client_method(
                "crypto_api_client.bitflyer.exchange_api_client.ExchangeApiClient",
                "send_endpoint_request"
            ):
                # Test code
        """
        return patch(
            f"{client_path}.{method_name}",
            new_callable=AsyncMock,
            side_effect=self.get_next_response,
        )

    def assert_called_times(self, expected: int) -> None:
        """Verify number of calls.

        Args:
            expected: Expected number of calls

        Raises:
            AssertionError: When call count differs from expected
        """
        assert self.call_count == expected, (
            f"Expected {expected} calls, but got {self.call_count}"
        )

    def assert_no_unused_responses(self) -> None:
        """Verify no unused responses remain.

        Raises:
            AssertionError: When unused responses remain
        """
        remaining = len(self.response_queue)
        assert remaining == 0, (
            f"Found {remaining} unused mock responses. "
            f"This might indicate a test issue."
        )

    def get_last_request(self) -> dict[str, Any] | None:
        """Get last recorded request.

        Returns:
            Last request information, or None
        """
        return self.captured_requests[-1] if self.captured_requests else None

    def reset(self) -> None:
        """Reset mock helper state."""
        self.response_queue.clear()
        self.call_count = 0
        self.captured_requests.clear()
