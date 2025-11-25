"""Mock helpers for HTTP responses and API methods.

This module provides convenient functions for creating mocks in tests,
reducing boilerplate code and making tests more readable.
"""

import json
from typing import Any
from unittest.mock import Mock

import httpx
from pytest_mock import MockerFixture

from crypto_api_client.http._http_status_code import HttpStatusCode
from crypto_api_client.http.http_response_data import HttpResponseData


def create_mock_response(
    status_code: int = 200, json_data: dict[str, Any] | None = None, text: str = ""
) -> Mock:
    """Create a mock HTTP response object.

    :param status_code: HTTP status code
    :param json_data: Optional JSON data for the response
    :param text: Response text
    :return: Mock response object
    """
    from datetime import timedelta

    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.text = text if text else json.dumps(json_data) if json_data else ""
    mock_response.headers = httpx.Headers({"Content-Type": "application/json"})
    mock_response.url = "https://api.example.com/endpoint"
    mock_response.content = mock_response.text.encode()
    mock_response.reason = "OK" if status_code < 400 else "Error"
    mock_response.elapsed = timedelta(seconds=0.1)
    mock_response.cookies = Mock()
    mock_response.cookies.get_dict.return_value = {}
    mock_response.encoding = "utf-8"

    # Mock request object
    mock_response.request = Mock()
    mock_response.request.method = "GET"
    mock_response.request.url = "https://api.example.com/endpoint"
    mock_response.request.path_url = "/endpoint"

    if json_data is not None:
        mock_response.json.return_value = json_data
    return mock_response


def mock_api_method_success(
    mocker: MockerFixture, target_class: type, method_name: str, return_data: Any
) -> Mock:
    """Mock an API method to return data directly (exception-based API).

    :param mocker: pytest-mock fixture
    :param target_class: The class containing the method
    :param method_name: The method name to mock
    :param return_data: The data to return directly
    :return: The mock object
    """
    return mocker.patch.object(
        target_class,
        method_name,
        return_value=return_data,
    )


def mock_api_method_error(
    mocker: MockerFixture, target_class: type, method_name: str, error: Exception
) -> Mock:
    """Mock an API method to raise an exception (exception-based API).

    :param mocker: pytest-mock fixture
    :param target_class: The class containing the method
    :param method_name: The method name to mock
    :param error: The error to raise
    :return: The mock object
    """
    return mocker.patch.object(
        target_class,
        method_name,
        side_effect=error,
    )


def create_mock_request(
    mocker: MockerFixture, module_path: str, response: Mock
) -> Mock:
    """Create a mock for requests.get/post/etc.

    :param mocker: pytest-mock fixture
    :param module_path: The module path to patch (e.g., 'requests.get')
    :param response: The mock response to return
    :return: The mock object
    """
    return mocker.patch(module_path, return_value=response)


def mock_multiple_api_calls(
    mocker: MockerFixture, target_class: type, mock_config: dict[str, tuple[bool, Any]]
) -> dict[str, Mock]:
    """Mock multiple API methods at once (exception-based API).

    :param mocker: pytest-mock fixture
    :param target_class: The class containing the methods
    :param mock_config: Dict mapping method names to (is_success, data_or_error) tuples
    :return: Dict mapping method names to mock objects
    """
    mocks = {}
    for method_name, (is_success, data) in mock_config.items():
        if is_success:
            mocks[method_name] = mock_api_method_success(
                mocker, target_class, method_name, data
            )
        else:
            mocks[method_name] = mock_api_method_error(
                mocker, target_class, method_name, data
            )
    return mocks  # type: ignore[return-value]


def create_mock_http_response_data(
    status_code: int = HttpStatusCode.OK,
    text: str = "{}",
    headers: dict[str, str] | None = None,
    url: str = "https://example.com/api",
    **kwargs: Any,
) -> HttpResponseData:
    """Create a mock HttpResponseData object.

    :param status_code: HTTP status code (default: 200)
    :param text: Response text (default: "{}")
    :param headers: Response headers (default: empty)
    :param url: Request URL (default: "https://example.com/api")
    :param kwargs: Additional optional fields (content, reason, elapsed, etc.)
    :return: HttpResponseData object
    """
    # Build kwargs for HttpResponseData
    model_kwargs: dict[str, Any] = {
        "http_status_code": status_code,
        "response_body_text": text,
        "headers": dict(headers or {}),
        "url": url,
    }

    # Add optional fields if provided
    if "content" in kwargs:
        model_kwargs["response_body_bytes"] = kwargs["content"]
    elif "response_body_bytes" in kwargs:
        model_kwargs["response_body_bytes"] = kwargs["response_body_bytes"]
    if "reason" in kwargs:
        model_kwargs["reason"] = kwargs["reason"]
    if "elapsed" in kwargs:
        model_kwargs["elapsed"] = kwargs["elapsed"]
    if "cookies" in kwargs:
        model_kwargs["cookies"] = kwargs["cookies"]
    if "encoding" in kwargs:
        model_kwargs["encoding"] = kwargs["encoding"]
    if "request_method" in kwargs:
        model_kwargs["request_method"] = kwargs["request_method"]
    if "request_url" in kwargs:
        model_kwargs["request_url"] = kwargs["request_url"]
    if "request_path" in kwargs:
        model_kwargs["request_path"] = kwargs["request_path"]

    return HttpResponseData(**model_kwargs)


def create_mock_api_response_data(
    json_data: dict[str, Any], status_code: int = HttpStatusCode.OK, **kwargs: Any
) -> HttpResponseData:
    """Create a mock HttpResponseData object with JSON data.

    :param json_data: JSON data to serialize as text
    :param status_code: HTTP status code (default: 200)
    :param kwargs: Additional optional fields
    :return: HttpResponseData object
    """
    text = json.dumps(json_data)
    return create_mock_http_response_data(status_code=status_code, text=text, **kwargs)


def create_mock_error_response_data(
    status_code: int = HttpStatusCode.BAD_REQUEST,
    error_message: str = "Bad Request",
    **kwargs: Any,
) -> HttpResponseData:
    """Create a mock HttpResponseData object for error cases.

    :param status_code: HTTP error status code (default: 400)
    :param error_message: Error message (default: "Bad Request")
    :param kwargs: Additional optional fields
    :return: HttpResponseData object
    """
    return create_mock_http_response_data(
        status_code=status_code, text=error_message, reason=error_message, **kwargs
    )
