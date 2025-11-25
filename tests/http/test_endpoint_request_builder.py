"""Tests for EndpointRequestBuilder."""

import pytest
from yarl import URL

from crypto_api_client import EndpointRequestBuilder
from crypto_api_client.http._http_method import HttpMethod
from crypto_api_client.security.secret_headers import SecretHeaders


class TestEndpointRequestBuilder:
    """Tests for EndpointRequestBuilder class."""

    @pytest.fixture
    def base_url(self) -> URL:
        """Base URL for testing."""
        return URL("https://api.example.com")

    @pytest.fixture
    def relative_stub_path(self) -> URL:
        """Relative stub path for testing."""
        return URL("v1")

    @pytest.fixture
    def relative_resource_path(self) -> URL:
        """Relative resource path for testing."""
        return URL("users/123")

    def test_get_request_basic(
        self, base_url: URL, relative_stub_path: URL, relative_resource_path: URL
    ) -> None:
        """Test basic GET request construction."""
        request = EndpointRequestBuilder.get(
            base_url=base_url, relative_stub_path=relative_stub_path, relative_resource_path=relative_resource_path
        )

        assert request.method == HttpMethod.GET
        assert request.base_url == base_url
        # relative_stub_path (e.g., "v1") is converted to stub_path (e.g., "/v1")
        assert request.stub_path == URL("/") / relative_stub_path.path
        assert request.relative_resource_path == relative_resource_path
        assert request.params == {}
        assert request.headers == SecretHeaders()
        assert request.body is None

    def test_get_request_with_params_and_headers(
        self, base_url: URL, relative_stub_path: URL, relative_resource_path: URL
    ) -> None:
        """Test GET request construction with parameters and headers."""
        params = {"sort": "asc", "limit": 10}
        headers = SecretHeaders({"Authorization": "Bearer token123"})

        request = EndpointRequestBuilder.get(
            base_url=base_url,
            relative_stub_path=relative_stub_path,
            relative_resource_path=relative_resource_path,
            params=params,
            headers=headers,
        )

        assert request.params == params
        assert request.headers == headers

    def test_get_request_without_stub_path(
        self, base_url: URL, relative_resource_path: URL
    ) -> None:
        """Test GET request construction without stub path."""
        request = EndpointRequestBuilder.get(
            base_url=base_url, relative_stub_path=None, relative_resource_path=relative_resource_path
        )

        assert request.stub_path is None

    def test_post_request_basic(
        self, base_url: URL, relative_stub_path: URL, relative_resource_path: URL
    ) -> None:
        """Test basic POST request construction."""
        body = {"name": "John", "email": "john@example.com"}

        request = EndpointRequestBuilder.post(
            base_url=base_url,
            relative_stub_path=relative_stub_path,
            relative_resource_path=relative_resource_path,
            body=body,
        )

        assert request.method == HttpMethod.POST
        assert request.body == body
        # Content-Type is not auto-set
        assert "Content-Type" not in request.headers

    def test_post_request_without_body(
        self, base_url: URL, relative_stub_path: URL, relative_resource_path: URL
    ) -> None:
        """Test POST request construction without body."""
        request = EndpointRequestBuilder.post(
            base_url=base_url, relative_stub_path=relative_stub_path, relative_resource_path=relative_resource_path
        )

        assert request.body is None
        # When body is None, Content-Type is not set
        assert "Content-Type" not in request.headers

    def test_post_request_with_custom_content_type(
        self, base_url: URL, relative_stub_path: URL, relative_resource_path: URL
    ) -> None:
        """Test POST request construction with custom Content-Type."""
        body = {"data": "test"}
        headers = SecretHeaders({"Content-Type": "application/xml"})

        request = EndpointRequestBuilder.post(
            base_url=base_url,
            relative_stub_path=relative_stub_path,
            relative_resource_path=relative_resource_path,
            body=body,
            headers=headers,
        )

        # Verify explicitly set Content-Type is preserved
        assert request.headers["Content-Type"] == "application/xml"

    def test_post_request_headers_not_modified(
        self, base_url: URL, relative_stub_path: URL, relative_resource_path: URL
    ) -> None:
        """Test that original headers are not modified."""
        original_headers = SecretHeaders({"Authorization": "Bearer token"})
        body = {"data": "test"}

        request = EndpointRequestBuilder.post(
            base_url=base_url,
            relative_stub_path=relative_stub_path,
            relative_resource_path=relative_resource_path,
            body=body,
            headers=original_headers,
        )

        # Verify passed headers are used as-is
        assert request.headers == original_headers
        assert "Authorization" in request.headers
        # Content-Type is not auto-set
        assert "Content-Type" not in request.headers

    def test_post_request_with_auth_headers(
        self, base_url: URL, relative_stub_path: URL, relative_resource_path: URL
    ) -> None:
        """Test POST request construction with auth headers (including Content-Type).

        Tests actual usage pattern (Private API).
        """
        body = {"order_type": "LIMIT", "side": "BUY", "size": 0.001}
        # Mimics actual _build_auth_headers() return value
        auth_headers = SecretHeaders(
            {
                "ACCESS-KEY": "test-key",
                "ACCESS-TIMESTAMP": "1234567890",
                "ACCESS-SIGN": "test-signature",
                "Content-Type": "application/json",
            }
        )

        request = EndpointRequestBuilder.post(
            base_url=base_url,
            relative_stub_path=relative_stub_path,
            relative_resource_path=relative_resource_path,
            body=body,
            headers=auth_headers,
        )

        assert request.method == HttpMethod.POST
        assert request.body == body
        # Auth headers Content-Type is preserved
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["ACCESS-KEY"] == "test-key"
