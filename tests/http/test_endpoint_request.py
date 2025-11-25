"""Tests for EndpointRequest model."""

import pytest
from yarl import URL

from crypto_api_client import EndpointRequest, EndpointRequestBuilder
from crypto_api_client.http._http_method import HttpMethod
from crypto_api_client.security.secret_headers import SecretHeaders


class TestEndpointRequest:
    """Tests for EndpointRequest class."""

    def test_endpoint_path_with_stub_path(self) -> None:
        """Test endpoint_path property when stub_path is present."""
        request = EndpointRequest(
            method=HttpMethod.GET,
            base_url=URL("https://api.bitflyer.jp"),
            stub_path=URL("/v1"),
            relative_resource_path=URL("ticker"),
            body=None,
        )

        assert request.endpoint_path == URL("/v1/ticker")

    def test_endpoint_path_without_stub_path(self) -> None:
        """Test endpoint_path property when stub_path is absent."""
        request = EndpointRequest(
            method=HttpMethod.GET,
            base_url=URL("https://public.bitbank.cc"),
            stub_path=None,
            relative_resource_path=URL("btc_jpy/ticker"),
            body=None,
        )

        assert request.endpoint_path == URL("btc_jpy/ticker")

    def test_api_endpoint_without_params(self) -> None:
        """Test api_endpoint property without parameters."""
        request = EndpointRequest(
            method=HttpMethod.GET,
            base_url=URL("https://api.bitflyer.jp"),
            stub_path=URL("/v1"),
            relative_resource_path=URL("ticker"),
            body=None,
        )

        assert request.api_endpoint == URL("https://api.bitflyer.jp/v1/ticker")

    def test_api_endpoint_with_params(self) -> None:
        """Test api_endpoint property with parameters."""
        request = EndpointRequest(
            method=HttpMethod.GET,
            base_url=URL("https://api.bitflyer.jp"),
            stub_path=URL("/v1"),
            relative_resource_path=URL("ticker"),
            params={"product_code": "BTC_JPY"},
            body=None,
        )

        assert request.api_endpoint == URL(
            "https://api.bitflyer.jp/v1/ticker?product_code=BTC_JPY"
        )

    def test_api_endpoint_with_multiple_params(self) -> None:
        """Test api_endpoint property with multiple parameters."""
        request = EndpointRequest(
            method=HttpMethod.GET,
            base_url=URL("https://api.bitflyer.jp"),
            stub_path=URL("/v1"),
            relative_resource_path=URL("me/getchildorders"),
            params={
                "product_code": "BTC_JPY",
                "child_order_state": "COMPLETED",
                "count": "3",
            },
            body=None,
        )

        # URL query parameter order is not guaranteed, so check individually
        api_endpoint = request.api_endpoint
        assert str(api_endpoint).startswith(
            "https://api.bitflyer.jp/v1/me/getchildorders?"
        )
        assert "product_code=BTC_JPY" in str(api_endpoint)
        assert "child_order_state=COMPLETED" in str(api_endpoint)
        assert "count=3" in str(api_endpoint)

    def test_api_endpoint_without_stub_path(self) -> None:
        """Test api_endpoint property when stub_path is absent."""
        request = EndpointRequest(
            method=HttpMethod.GET,
            base_url=URL("https://public.bitbank.cc"),
            stub_path=None,
            relative_resource_path=URL("btc_jpy/ticker"),
            body=None,
        )

        assert request.api_endpoint == URL("https://public.bitbank.cc/btc_jpy/ticker")

    def test_endpoint_request_builder_get(self) -> None:
        """Test api_endpoint of request built with EndpointRequestBuilder.get method."""
        request = EndpointRequestBuilder.get(
            base_url=URL("https://api.bitflyer.jp"),
            relative_stub_path=URL("v1"),
            relative_resource_path=URL("ticker"),
            params={"product_code": "BTC_JPY"},
        )

        assert request.api_endpoint == URL(
            "https://api.bitflyer.jp/v1/ticker?product_code=BTC_JPY"
        )

    def test_endpoint_request_builder_post(self) -> None:
        """Test api_endpoint of request built with EndpointRequestBuilder.post method."""
        request = EndpointRequestBuilder.post(
            base_url=URL("https://api.bitflyer.jp"),
            relative_stub_path=URL("v1"),
            relative_resource_path=URL("me/sendchildorder"),
            body={"product_code": "BTC_JPY", "side": "BUY"},
        )

        # For POST requests, body is not included in the URL
        assert request.api_endpoint == URL(
            "https://api.bitflyer.jp/v1/me/sendchildorder"
        )
        # Content-Type is not auto-set (caller needs to set it)
        assert "Content-Type" not in request.headers

    def test_complex_relative_resource_path(self) -> None:
        """Test api_endpoint with complex relative_resource_path."""
        request = EndpointRequest(
            method=HttpMethod.GET,
            base_url=URL("https://api.example.com"),
            stub_path=URL("/api/v2"),
            relative_resource_path=URL("users/123/orders/456"),
            body=None,
        )

        assert request.api_endpoint == URL(
            "https://api.example.com/api/v2/users/123/orders/456"
        )

    def test_immutability(self) -> None:
        """Test that EndpointRequest is immutable."""
        request = EndpointRequest(
            method=HttpMethod.GET,
            base_url=URL("https://api.bitflyer.jp"),
            stub_path=URL("/v1"),
            relative_resource_path=URL("ticker"),
            body=None,
        )

        # Attempt to modify attribute
        with pytest.raises(
            Exception
        ):  # In Pydantic v2, this raises ValidationError or AttributeError
            request.method = HttpMethod.POST  # type: ignore

    def test_endpoint_request_equality(self) -> None:
        """Test that EndpointRequests with same content are equal."""
        request1 = EndpointRequest(
            method=HttpMethod.GET,
            base_url=URL("https://api.bitflyer.jp"),
            stub_path=URL("/v1"),
            relative_resource_path=URL("ticker"),
            params={"product_code": "BTC_JPY"},
            body=None,
        )

        request2 = EndpointRequest(
            method=HttpMethod.GET,
            base_url=URL("https://api.bitflyer.jp"),
            stub_path=URL("/v1"),
            relative_resource_path=URL("ticker"),
            params={"product_code": "BTC_JPY"},
            body=None,
        )

        assert request1 == request2
        assert request1.api_endpoint == request2.api_endpoint

    def test_post_without_body_no_content_type(self) -> None:
        """Test that Content-Type is not set for POST requests without body."""
        request = EndpointRequestBuilder.post(
            base_url=URL("https://api.bitflyer.jp"),
            relative_stub_path=URL("v1"),
            relative_resource_path=URL("me/cancelchildorder"),
            body=None,
        )

        # Content-Type is not set when there is no body
        assert "Content-Type" not in request.headers

    def test_post_with_custom_content_type(self) -> None:
        """Test that custom Content-Type is preserved when specified."""
        custom_headers = SecretHeaders(
            {"Content-Type": "application/x-www-form-urlencoded"}
        )
        request = EndpointRequestBuilder.post(
            base_url=URL("https://api.bitflyer.jp"),
            relative_stub_path=URL("v1"),
            relative_resource_path=URL("me/sendchildorder"),
            body={"product_code": "BTC_JPY"},
            headers=custom_headers,
        )

        # Custom Content-Type is preserved
        assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"

    def test_post_with_other_headers(self) -> None:
        """Test that headers are set correctly."""
        custom_headers = SecretHeaders(
            {
                "Authorization": "Bearer token123",
                "Content-Type": "application/json",
            }
        )
        request = EndpointRequestBuilder.post(
            base_url=URL("https://api.bitflyer.jp"),
            relative_stub_path=URL("v1"),
            relative_resource_path=URL("me/sendchildorder"),
            body={"product_code": "BTC_JPY"},
            headers=custom_headers,
        )

        # Explicitly set headers are preserved
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["Authorization"] == "Bearer token123"

    def test_get_with_headers(self) -> None:
        """Test that headers are set correctly for GET requests."""
        custom_headers = SecretHeaders({"User-Agent": "TestClient/1.0"})
        request = EndpointRequestBuilder.get(
            base_url=URL("https://api.bitflyer.jp"),
            relative_stub_path=URL("v1"),
            relative_resource_path=URL("ticker"),
            headers=custom_headers,
        )

        # Content-Type is not auto-set for GET requests
        assert "Content-Type" not in request.headers
        assert request.headers["User-Agent"] == "TestClient/1.0"

    def test_body_json_with_body(self) -> None:
        """Test body_json property when body is present."""
        body_data = {"product_code": "BTC_JPY", "side": "BUY", "size": 0.001}
        request = EndpointRequestBuilder.post(
            base_url=URL("https://api.bitflyer.jp"),
            relative_stub_path=URL("v1"),
            relative_resource_path=URL("me/sendchildorder"),
            body=body_data,
        )

        # body_json becomes a JSON string (compact format without spaces)
        assert request.body_json is not None
        assert (
            request.body_json == '{"product_code":"BTC_JPY","side":"BUY","size":0.001}'
        )

        # Original body is unchanged
        assert request.body == body_data

    def test_body_json_without_body(self) -> None:
        """Test body_json property when body is absent."""
        request = EndpointRequestBuilder.get(
            base_url=URL("https://api.bitflyer.jp"),
            relative_stub_path=URL("v1"),
            relative_resource_path=URL("ticker"),
        )

        # When body is absent, body_json is also None
        assert request.body is None
        assert request.body_json is None

    def test_body_json_with_complex_data(self) -> None:
        """Test body_json with complex data structure."""
        import json

        body_data = {
            "orders": [
                {"id": 1, "price": 1000000, "size": 0.001},
                {"id": 2, "price": 1010000, "size": 0.002},
            ],
            "metadata": {"timestamp": "2025-01-01T00:00:00Z", "version": 2},
        }
        request = EndpointRequest(
            method=HttpMethod.POST,
            base_url=URL("https://api.example.com"),
            stub_path=None,
            relative_resource_path=URL("batch/orders"),
            body=body_data,
        )

        # Verify body_json is correctly serialized
        assert request.body_json is not None
        parsed = json.loads(request.body_json)
        assert parsed == body_data

    def test_body_json_is_computed(self) -> None:
        """Test that body_json is a computed property."""
        request = EndpointRequestBuilder.post(
            base_url=URL("https://api.bitflyer.jp"),
            relative_stub_path=URL("v1"),
            relative_resource_path=URL("me/sendchildorder"),
            body={"product_code": "BTC_JPY"},
        )

        # body_json always returns the same value (compact format without spaces)
        json1 = request.body_json
        json2 = request.body_json
        assert json1 == json2
        assert json1 == '{"product_code":"BTC_JPY"}'
