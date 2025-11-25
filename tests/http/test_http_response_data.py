"""Tests for HttpResponseData model."""

from datetime import timedelta

import pytest
from pydantic import ValidationError

from crypto_api_client.http._http_status_code import HttpStatusCode
from crypto_api_client.http.http_response_data import HttpResponseData


class TestHttpResponseData:
    """Tests for HttpResponseData."""

    def test_create_with_required_fields_only(self) -> None:
        """Verify model can be created with required fields only."""
        data = HttpResponseData(
            http_status_code=HttpStatusCode.OK,
            headers={"Content-Type": "application/json"},
            response_body_text="response body",
            url="https://api.example.com/endpoint",
        )

        assert data.http_status_code == HttpStatusCode.OK
        assert (
            data.headers["Content-Type"] == "application/json"
        )  # Breaking change: case-sensitive
        assert data.response_body_text == "response body"
        assert data.url == "https://api.example.com/endpoint"

        # Verify default values for optional fields
        assert data.response_body_bytes is None
        assert data.reason is None
        assert data.elapsed is None
        assert data.cookies == {}
        assert data.encoding is None
        assert data.request_method == ""
        assert data.request_url == ""
        assert data.request_path == ""

    def test_create_with_all_fields(self) -> None:
        """Verify model can be created with all fields specified."""
        elapsed = timedelta(seconds=1.5)
        data = HttpResponseData(
            http_status_code=HttpStatusCode.CREATED,
            headers={"Content-Type": "text/plain"},
            response_body_text="created",
            url="https://api.example.com/resource/123",
            response_body_bytes=b"created",
            reason="Created",
            elapsed=elapsed,
            cookies={"session_id": "abc123"},
            encoding="utf-8",
            request_method="POST",
            request_url="https://api.example.com/resource",
            request_path="/resource",
        )

        assert data.http_status_code == HttpStatusCode.CREATED
        assert data.response_body_text == "created"
        assert data.response_body_bytes == b"created"
        assert data.reason == "Created"
        assert data.elapsed == elapsed
        assert data.cookies == {"session_id": "abc123"}
        assert data.encoding == "utf-8"
        assert data.request_method == "POST"

    def test_model_is_frozen(self) -> None:
        """Verify model is immutable."""
        data = HttpResponseData(
            http_status_code=HttpStatusCode.OK,
            headers={},
            response_body_text="test",
            url="https://example.com",
        )

        with pytest.raises(ValidationError) as exc_info:
            data.http_status_code = HttpStatusCode.NOT_FOUND

        assert "Instance is frozen" in str(exc_info.value)

    def test_missing_required_field_raises_error(self) -> None:
        """Verify error is raised when required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            HttpResponseData(
                # http_status_code is missing
                http_status_code=None,  # type: ignore
                headers={},
                response_body_text="test",
                url="https://example.com",
            )

        errors = exc_info.value.errors()
        # Since it's Union[HTTPStatus, int], None may cause multiple errors
        assert len(errors) >= 1
        # Verify error related to http_status_code is included
        assert any("http_status_code" in str(error["loc"]) for error in errors)

    def test_invalid_type_raises_error(self) -> None:
        """Verify error is raised for invalid type."""
        # Since it's Union[HTTPStatus, int], passing non-numeric type raises error
        with pytest.raises(ValidationError) as exc_info:
            HttpResponseData(
                http_status_code=[],  # type: ignore[arg-type]  # List is invalid type
                headers={},
                response_body_text="test",
                url="https://example.com",
            )

        errors = exc_info.value.errors()
        # For Union types, error location may be nested
        assert any("http_status_code" in error["loc"] for error in errors)

    def test_dict_export(self) -> None:
        """Verify export to dictionary format."""
        data = HttpResponseData(
            http_status_code=HttpStatusCode.OK,
            headers={"X-Custom": "value"},
            response_body_text="response",
            url="https://api.example.com",
        )

        data_dict = data.model_dump()
        assert data_dict["http_status_code"] == HttpStatusCode.OK
        assert data_dict["response_body_text"] == "response"
        assert data_dict["url"] == "https://api.example.com"
        assert isinstance(data_dict["headers"], dict)  # Breaking change: changed to dict type

    def test_json_export_with_exclude_none(self) -> None:
        """Verify JSON export with None excluded."""
        data = HttpResponseData(
            http_status_code=HttpStatusCode.OK,
            headers={},
            response_body_text="response",
            url="https://api.example.com",
            # response_body_bytes and reason are None
        )

        # headers is not serializable, so exclude it
        # Also add exclude_defaults=True to exclude default values
        json_str = data.model_dump_json(
            exclude={"headers"}, exclude_none=True, exclude_defaults=True
        )
        assert "response_body_bytes" not in json_str  # None is excluded
        assert "reason" not in json_str  # None is excluded
        assert "cookies" not in json_str  # Empty dict is also excluded
        assert "request_method" not in json_str  # Empty string is also excluded

    def test_model_copy(self) -> None:
        """Verify partial update with model_copy."""
        original = HttpResponseData(
            http_status_code=HttpStatusCode.OK,
            headers={},
            response_body_text="original",
            url="https://api.example.com",
        )

        # Update http_status_code and response_body_text
        updated = original.model_copy(
            update={
                "http_status_code": HttpStatusCode.CREATED,
                "response_body_text": "updated",
            }
        )

        assert updated.http_status_code == HttpStatusCode.CREATED
        assert updated.response_body_text == "updated"
        assert updated.url == original.url  # Unchanged
        assert updated.headers == original.headers  # Unchanged

        # Original object is unchanged
        assert original.http_status_code == HttpStatusCode.OK
        assert original.response_body_text == "original"

    def test_create_with_httpstatus_constants(self) -> None:
        """Verify model can be created using HttpStatusCode constants."""
        data = HttpResponseData(
            http_status_code=HttpStatusCode.NOT_FOUND,
            headers={},
            response_body_text="Not Found",
            url="https://api.example.com/missing",
        )

        assert data.http_status_code == HttpStatusCode.NOT_FOUND
        assert isinstance(data.http_status_code, int)

    def test_create_with_int_status_code(self) -> None:
        """Verify model can be created with int type http_status_code."""
        # Non-standard status code
        data = HttpResponseData(
            http_status_code=429,  # TOO_MANY_REQUESTS
            headers={},
            response_body_text="Rate Limited",
            url="https://api.example.com",
        )

        assert data.http_status_code == 429
        assert isinstance(data.http_status_code, int)

    def test_create_with_various_status_codes(self) -> None:
        """Verify model can be created with various HTTP status codes."""
        test_cases = [
            (HttpStatusCode.CONTINUE, 100),
            (HttpStatusCode.OK, 200),
            (HttpStatusCode.MOVED_PERMANENTLY, 301),
            (HttpStatusCode.BAD_REQUEST, 400),
            (HttpStatusCode.INTERNAL_SERVER_ERROR, 500),
            (HttpStatusCode.TOO_MANY_REQUESTS, 429),  # Python 3.11+
        ]

        for status_enum, expected_value in test_cases:
            data = HttpResponseData(
                http_status_code=status_enum,
                headers={},
                response_body_text="test",
                url="https://example.com",
            )
            assert data.http_status_code == status_enum
            assert isinstance(data.http_status_code, int)
            assert data.http_status_code == expected_value
