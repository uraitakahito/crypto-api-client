"""Tests for HttpStatusCode class."""

from crypto_api_client.http._http_status_code import HttpStatusCode


class TestHttpStatusCode:
    """Tests for HttpStatusCode class."""

    def test_standard_status_codes(self) -> None:
        """Verify standard HTTP status codes are defined correctly."""
        assert HttpStatusCode.OK == 200
        assert HttpStatusCode.CREATED == 201
        assert HttpStatusCode.BAD_REQUEST == 400
        assert HttpStatusCode.UNAUTHORIZED == 401
        assert HttpStatusCode.NOT_FOUND == 404
        assert HttpStatusCode.INTERNAL_SERVER_ERROR == 500
        assert HttpStatusCode.SERVICE_UNAVAILABLE == 503

    def test_non_standard_cloudflare_codes(self) -> None:
        """Verify CloudFlare non-standard codes are defined correctly."""
        assert HttpStatusCode.CLOUDFLARE_UNKNOWN_ERROR == 520
        assert HttpStatusCode.CLOUDFLARE_WEB_SERVER_IS_DOWN == 521
        assert HttpStatusCode.CLOUDFLARE_CONNECTION_TIMED_OUT == 522
        assert HttpStatusCode.CLOUDFLARE_ORIGIN_IS_UNREACHABLE == 523
        assert HttpStatusCode.CLOUDFLARE_TIMEOUT_OCCURRED == 524
        assert HttpStatusCode.CLOUDFLARE_SSL_HANDSHAKE_FAILED == 525
        assert HttpStatusCode.CLOUDFLARE_INVALID_SSL_CERTIFICATE == 526
        assert HttpStatusCode.CLOUDFLARE_RAILGUN_ERROR == 527

    def test_non_standard_nginx_codes(self) -> None:
        """Verify nginx non-standard codes are defined correctly."""
        assert HttpStatusCode.NGINX_CLIENT_CLOSED_REQUEST == 499

    def test_is_success(self) -> None:
        """Test success status determination."""
        assert HttpStatusCode.is_success(200) is True
        assert HttpStatusCode.is_success(201) is True
        assert HttpStatusCode.is_success(299) is True
        assert HttpStatusCode.is_success(300) is False
        assert HttpStatusCode.is_success(400) is False
        assert HttpStatusCode.is_success(500) is False
