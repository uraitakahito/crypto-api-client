"""Base class for asynchronous tests.

This module provides a base class to standardize asynchronous test patterns.
All async tests can inherit from this base class or its subclasses to utilize
common test patterns and helper methods.
"""

import json
from decimal import Decimal
from typing import Any, Generic, Type, TypeVar
from unittest.mock import AsyncMock, patch

import pytest

from crypto_api_client.http.http_response_data import HttpResponseData

T = TypeVar("T")


class BaseAsyncTestCase(Generic[T]):
    """Base class for asynchronous tests.

    This class provides the following features:
    - Automatic application of pytest.mark.asyncio
    - Helper for creating HTTP response mocks
    - Common assertions for API call success/error cases
    """

    # Automatically apply pytest.mark.asyncio
    pytestmark = pytest.mark.asyncio

    @pytest.fixture
    async def async_client(self) -> T:
        """Fixture that returns a client instance.

        Must be implemented in subclasses.

        :return: Client instance under test
        :rtype: T
        :raises NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError(
            "Subclass must implement async_client fixture"
        )

    def create_mock_response(
        self, data: Any, status_code: int = 200, headers: dict[str, str] | None = None
    ) -> HttpResponseData:
        """Create a standard HTTP response mock.

        :param data: Response body data
        :type data: Any
        :param status_code: HTTP status code
        :type status_code: int
        :param headers: Response headers
        :type headers: dict[str, str] | None
        :return: Mocked HTTP response
        :rtype: HttpResponseData
        """

        # Convert data containing Decimal to JSON-serializable format
        def decimal_default(obj: Any) -> float:
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError

        if isinstance(data, dict):
            text = json.dumps(data, default=decimal_default)
        else:
            text = str(data)

        return HttpResponseData(
            http_status_code=status_code,
            headers=headers or {},
            response_body_text=text,
            url="https://mocked.api.endpoint",
        )

    async def assert_api_call_success(
        self,
        client: Any,
        method_name: str,
        request: Any,
        mock_response_data: dict[str, Any],
        expected_result: Any | None = None,
    ) -> tuple[Any, AsyncMock]:
        """Common assertion for success cases.

        :param client: Client under test
        :type client: Any
        :param method_name: Method name to call
        :type method_name: str
        :param request: API request object
        :type request: Any
        :param mock_response_data: Mock response data
        :type mock_response_data: dict
        :param expected_result: Expected result (skip assertion if not specified)
        :type expected_result: Any | None
        :return: API method result and mock object
        :rtype: tuple[Any, AsyncMock]
        """
        with patch.object(
            client, "send_endpoint_request", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = self.create_mock_response(mock_response_data)

            result = await getattr(client, method_name)(request)

            if expected_result is not None:
                assert result == expected_result
            mock_send.assert_called_once()
            return result, mock_send

    async def assert_api_call_error(
        self,
        client: Any,
        method_name: str,
        request: Any,
        error_class: Type[Exception],
        error_message: str,
    ) -> AsyncMock:
        """Common assertion for error cases.

        :param client: Client under test
        :type client: Any
        :param method_name: Method name to call
        :type method_name: str
        :param request: API request object
        :type request: Any
        :param error_class: Expected error class
        :type error_class: Type[Exception]
        :param error_message: Expected error message
        :type error_message: str
        :return: Mock object
        :rtype: AsyncMock
        """
        with patch.object(
            client, "send_endpoint_request", new_callable=AsyncMock
        ) as mock_send:
            mock_send.side_effect = error_class(error_message)

            with pytest.raises(error_class) as exc_info:
                await getattr(client, method_name)(request)

            assert str(exc_info.value) == error_message
            mock_send.assert_called_once()
            return mock_send
