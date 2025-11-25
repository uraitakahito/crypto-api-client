"""Tests for http_types module - includes HttpResponseData and HttpMethod."""

from datetime import timedelta

import pytest

from crypto_api_client.http._http_method import HttpMethod
from crypto_api_client.http.http_response_data import HttpResponseData


class TestHttpMethod:
    """Tests for HttpMethod class."""

    def test_http_method_enum_values(self) -> None:
        """Verify HttpMethod values are correct."""
        assert HttpMethod.GET.value == "GET"
        assert HttpMethod.POST.value == "POST"

    def test_http_method_string_representation(self) -> None:
        """Test HttpMethod string representation."""
        assert str(HttpMethod.GET) == "GET"
        assert str(HttpMethod.POST) == "POST"


class TestHttpResponseDataPydantic:
    """Tests for HttpResponseData Pydantic model."""

    def test_required_fields_pydantic(self) -> None:
        """Test Pydantic model with required fields."""
        response_data = HttpResponseData(
            http_status_code=200,
            headers={"Content-Type": "application/json"},
            response_body_text='{"result": "ok"}',
            url="https://api.example.com/v1/test",
        )

        assert response_data.http_status_code == 200
        assert isinstance(response_data.headers, dict)  # Breaking change: changed to dict type
        assert response_data.response_body_text == '{"result": "ok"}'
        assert response_data.url == "https://api.example.com/v1/test"

    def test_optional_fields_pydantic(self) -> None:
        """Test Pydantic model with optional fields."""
        response_data = HttpResponseData(
            http_status_code=200,
            headers={},
            response_body_text="OK",
            url="https://api.example.com/v1/test",
            response_body_bytes=b'{"result": "ok"}',
            reason="OK",
            elapsed=timedelta(seconds=0.5),
            cookies={"session": "abc123"},
            encoding="utf-8",
            request_method="GET",
            request_url="https://api.example.com/v1/test",
            request_path="/v1/test",
        )

        assert response_data.response_body_bytes == b'{"result": "ok"}'
        assert response_data.reason == "OK"
        assert isinstance(response_data.elapsed, timedelta)

    def test_complete_http_response_data_pydantic(self) -> None:
        """Test complete HttpResponseData Pydantic model."""
        response_data = HttpResponseData(
            # Required fields
            http_status_code=201,
            headers={"Location": "/resource/123"},
            response_body_text='{"id": 123, "created": true}',
            url="https://api.example.com/v1/resources",
            # Optional fields
            response_body_bytes=b'{"id": 123, "created": true}',
            reason="Created",
            elapsed=timedelta(seconds=0.123),
            encoding="utf-8",
        )

        # Verify required fields
        assert response_data.http_status_code == 201
        assert response_data.headers["Location"] == "/resource/123"
        assert response_data.response_body_text == '{"id": 123, "created": true}'
        assert response_data.url == "https://api.example.com/v1/resources"

        # Verify optional fields
        assert response_data.response_body_bytes == b'{"id": 123, "created": true}'
        assert response_data.reason == "Created"
        assert response_data.elapsed == timedelta(seconds=0.123)


class TestHttpResponseDataValidation:
    """Validation tests for HttpResponseData Pydantic model."""

    def test_valid_response_data_pydantic(self) -> None:
        """Test Pydantic validation with valid response data."""
        # Pydantic model ignores extra fields
        response_data = HttpResponseData(
            http_status_code=200,
            headers={"X-Test": "value"},
            response_body_text="Response body",
            url="https://api.example.com/test",
        )

        assert response_data.http_status_code == 200
        assert response_data.response_body_text == "Response body"

    def test_missing_required_field_pydantic(self) -> None:
        """Test Pydantic error when required field is missing."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            HttpResponseData(
                http_status_code=200,
                headers={},
                response_body_text=None,  # type: ignore
                url=None,  # type: ignore
                # "response_body_text" and "url" are missing
            )

        errors = exc_info.value.errors()
        error_fields = [error["loc"][0] for error in errors]
        assert "response_body_text" in error_fields
        assert "url" in error_fields

    def test_invalid_status_code_type_pydantic(self) -> None:
        """Test Pydantic error when http_status_code type is invalid."""
        from pydantic import ValidationError

        # Pydantic auto-converts "200" to 200, so use a non-convertible value
        with pytest.raises(ValidationError) as exc_info:
            HttpResponseData(
                http_status_code="invalid",  # type: ignore  # String that cannot be converted to number
                headers={},
                response_body_text="OK",
                url="https://example.com",
            )

        errors = exc_info.value.errors()
        # For Union types, error location may be nested
        assert any("http_status_code" in error["loc"] for error in errors)

    def test_invalid_headers_type_pydantic(self) -> None:
        """Test Pydantic error when headers type is invalid."""
        from pydantic import ValidationError

        # After httpx migration, headers accepts regular dict, so test with different invalid type
        with pytest.raises(ValidationError) as exc_info:
            HttpResponseData(
                http_status_code=200,
                headers="invalid_string",  # type: ignore  # String is invalid
                response_body_text="OK",
                url="https://example.com",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("headers",) for error in errors)

    def test_invalid_text_type_pydantic(self) -> None:
        """Test Pydantic error when text type is invalid."""
        from pydantic import ValidationError

        # Pydantic decodes bytes to string, so use a different invalid type
        with pytest.raises(ValidationError) as exc_info:
            HttpResponseData(
                http_status_code=200,
                headers={},
                response_body_text=123,  # type: ignore  # Number is invalid
                url="https://example.com",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("response_body_text",) for error in errors)

    def test_invalid_url_type_pydantic(self) -> None:
        """Test Pydantic error when url type is invalid."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            HttpResponseData(
                http_status_code=200,
                headers={},
                response_body_text="OK",
                url=None,  # type: ignore  # None is invalid
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("url",) for error in errors)

    def test_minimal_valid_data_pydantic(self) -> None:
        """Test minimal valid data Pydantic model."""
        response_data = HttpResponseData(
            http_status_code=404,
            headers={},
            response_body_text="",
            url="https://example.com/not-found",
        )

        assert response_data.http_status_code == 404
        assert response_data.response_body_text == ""
