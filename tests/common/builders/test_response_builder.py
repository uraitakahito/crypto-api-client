"""Tests for ResponseBuilder."""

import json
from datetime import timedelta

import pytest

from crypto_api_client.http._http_status_code import HttpStatusCode
from tests.common.builders import ResponseBuilder


class TestResponseBuilder:
    """Test ResponseBuilder functionality."""

    @pytest.fixture
    def builder(self) -> ResponseBuilder:
        """Create ResponseBuilder instance."""
        return ResponseBuilder()

    def test_success_response_default(self, builder: ResponseBuilder) -> None:
        """Test creating default success response."""
        response = builder.success()

        assert response.http_status_code == HttpStatusCode.OK
        assert response.response_body_text == "{}"
        assert response.headers["content-type"] == "application/json"
        assert response.encoding == "utf-8"
        assert response.reason == "OK"

    def test_success_response_custom(self, builder: ResponseBuilder) -> None:
        """Test creating custom success response."""
        body = '{"result": "success"}'
        headers = {"x-custom": "value"}

        response = builder.success(http_status_code=201, body=body, headers=headers)

        assert response.http_status_code == HttpStatusCode.CREATED
        assert response.response_body_text == body
        assert response.headers["x-custom"] == "value"
        assert response.reason == "Created"

    def test_error_response_client_error(self, builder: ResponseBuilder) -> None:
        """Test creating client error response."""
        response = builder.error(
            http_status_code=400, message="Bad request", error_code="BAD_REQUEST"
        )

        assert response.http_status_code == HttpStatusCode.BAD_REQUEST

        error_data = json.loads(response.response_body_text)
        assert error_data["error"]["message"] == "Bad request"
        assert error_data["error"]["code"] == "BAD_REQUEST"
        assert "type" not in error_data["error"]

    def test_error_response_server_error(self, builder: ResponseBuilder) -> None:
        """Test creating server error response."""
        response = builder.error(
            http_status_code=500,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
        )

        assert response.http_status_code == HttpStatusCode.INTERNAL_SERVER_ERROR

        error_data = json.loads(response.response_body_text)
        assert error_data["error"]["message"] == "Internal server error"
        assert error_data["error"]["code"] == "INTERNAL_ERROR"
        assert error_data["error"]["type"] == "server_error"

    def test_rate_limit_error(self, builder: ResponseBuilder) -> None:
        """Test creating rate limit error response."""
        response = builder.rate_limit_error(retry_after=120)

        assert response.http_status_code == HttpStatusCode.TOO_MANY_REQUESTS
        assert response.headers["retry-after"] == "120"
        assert response.headers["x-ratelimit-remaining"] == "0"

        error_data = json.loads(response.response_body_text)
        assert error_data["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    def test_timeout_error(self, builder: ResponseBuilder) -> None:
        """Test creating timeout error response."""
        response = builder.timeout_error()

        assert response.http_status_code == HttpStatusCode.REQUEST_TIMEOUT

        error_data = json.loads(response.response_body_text)
        assert error_data["error"]["message"] == "Request timeout"
        assert error_data["error"]["code"] == "REQUEST_TIMEOUT"

    def test_not_found_error(self, builder: ResponseBuilder) -> None:
        """Test creating not found error response."""
        response = builder.not_found_error("Order")

        assert response.http_status_code == HttpStatusCode.NOT_FOUND

        error_data = json.loads(response.response_body_text)
        assert error_data["error"]["message"] == "Order not found"
        assert error_data["error"]["code"] == "NOT_FOUND"

    def test_unauthorized_error(self, builder: ResponseBuilder) -> None:
        """Test creating unauthorized error response."""
        response = builder.unauthorized_error("Invalid API key")

        assert response.http_status_code == HttpStatusCode.UNAUTHORIZED
        assert response.headers["www-authenticate"] == "Bearer"

        error_data = json.loads(response.response_body_text)
        assert error_data["error"]["message"] == "Invalid API key"
        assert error_data["error"]["code"] == "UNAUTHORIZED"

    def test_non_standard_status_code(self, builder: ResponseBuilder) -> None:
        """Test handling non-standard status codes."""
        response = builder._create_response(  # type: ignore[reportPrivateUsage]
            http_status_code=999,
            body="Custom error",
            headers={"content-type": "text/plain"},
        )

        # Should use integer status code for non-standard codes
        assert response.http_status_code == 999
        assert response.reason == "HTTP 999"

    def test_response_metadata(self, builder: ResponseBuilder) -> None:
        """Test response metadata fields."""
        response = builder.success()

        # Check metadata fields
        assert response.url == "https://api.example.com/test"
        assert response.request_method == "GET"
        assert response.request_url == "https://api.example.com/test"
        assert response.request_path == "/test"
        assert isinstance(response.elapsed, timedelta)
        assert response.cookies == {}
