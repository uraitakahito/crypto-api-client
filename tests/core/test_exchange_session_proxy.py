"""Tests for ExchangeSession proxy-related functionality."""

import ssl

import pytest
from pydantic import SecretStr

from crypto_api_client.core.exchange_session import ExchangeSession
from crypto_api_client.core.exchange_types import Exchange
from crypto_api_client.core.session_config import SessionConfig


class TestExchangeSessionProxy:
    """Tests for ExchangeSession proxy-related functionality."""

    def test_build_proxy_config_no_auth(self) -> None:
        """Build proxy URL without authentication."""
        config = SessionConfig(proxy_url="http://host.docker.internal:8080")
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config,
        )

        proxy_url = session._build_proxy_config()
        assert proxy_url == "http://host.docker.internal:8080"

    def test_build_proxy_config_with_auth(self) -> None:
        """Build proxy URL with authentication."""
        config = SessionConfig(
            proxy_url="http://host.docker.internal:8080",
            proxy_auth=(SecretStr("testuser"), SecretStr("testpass")),
        )
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config,
        )

        proxy_url = session._build_proxy_config()
        assert proxy_url is not None
        assert "testuser" in proxy_url
        assert "testpass" in proxy_url
        assert "host.docker.internal:8080" in proxy_url

    def test_build_proxy_config_none(self) -> None:
        """Return None when proxy is not configured."""
        config = SessionConfig()
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config,
        )

        proxy_url = session._build_proxy_config()
        assert proxy_url is None

    def test_build_ssl_verify_config_default(self) -> None:
        """Default SSL configuration."""
        config = SessionConfig()
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config,
        )

        verify = session._build_ssl_verify_config()
        assert verify is True

    def test_build_ssl_verify_config_false(self) -> None:
        """Disable SSL verification.

        Note: When verify_ssl=False, returns ssl.SSLContext instead of bool False
        to work with HTTPS connections through proxy.
        """
        import ssl

        config = SessionConfig(verify_ssl=False)
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config,
        )

        verify = session._build_ssl_verify_config()
        assert isinstance(verify, ssl.SSLContext)
        # Verify that verification is disabled
        assert verify.check_hostname is False
        assert verify.verify_mode == ssl.CERT_NONE

    def test_build_ssl_verify_config_cert_file(self) -> None:
        """Custom CA certificate path."""
        import httpx

        config = SessionConfig(ssl_cert_file="/path/to/ca.pem")
        # Provide external HTTP client to skip session creation
        dummy_client = httpx.AsyncClient()
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config,
            http_client=dummy_client,
        )

        verify = session._build_ssl_verify_config()
        assert verify == "/path/to/ca.pem"

    def test_build_ssl_verify_config_context(self) -> None:
        """Custom SSLContext."""
        ctx = ssl.create_default_context()
        config = SessionConfig(ssl_context=ctx)
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config,
        )

        verify = session._build_ssl_verify_config()
        assert verify is ctx

    def test_create_http_client_with_proxy(self) -> None:
        """HTTP client creation with proxy."""
        config = SessionConfig(proxy_url="http://host.docker.internal:8080")
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config,
        )

        # Verify HTTP client is created
        assert session._http_client is not None
        # Proxy settings are internal to httpx, so direct verification is difficult
        # Need to test with actual HTTP requests

    @pytest.mark.asyncio
    async def test_session_lifecycle_with_proxy(self) -> None:
        """Session lifecycle with proxy configuration."""
        config = SessionConfig(proxy_url="http://host.docker.internal:8080")
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config,
        )

        assert not session.is_closed
        await session.close()
        assert session.is_closed

    def test_ssl_verify_priority(self) -> None:
        """Test SSL configuration priority.

        Priority:
        1. ssl_context
        2. verify_ssl=False
        3. ssl_cert_file
        4. True (default)
        """
        # Priority 1: ssl_context
        ctx = ssl.create_default_context()
        config1 = SessionConfig(
            ssl_context=ctx,
            verify_ssl=False,
            ssl_cert_file="/path/to/ca.pem",
        )
        session1 = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config1,
        )
        assert session1._build_ssl_verify_config() is ctx

        # Priority 2: verify_ssl=False (returns SSLContext)
        config2 = SessionConfig(verify_ssl=False, ssl_cert_file="/path/to/ca.pem")
        session2 = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config2,
        )
        result2 = session2._build_ssl_verify_config()
        assert isinstance(result2, ssl.SSLContext)
        assert result2.check_hostname is False
        assert result2.verify_mode == ssl.CERT_NONE

        # Priority 3: ssl_cert_file
        import httpx

        config3 = SessionConfig(ssl_cert_file="/path/to/ca.pem")
        dummy_client3 = httpx.AsyncClient()
        session3 = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config3,
            http_client=dummy_client3,
        )
        assert session3._build_ssl_verify_config() == "/path/to/ca.pem"

        # Priority 4: Default
        config4 = SessionConfig()
        session4 = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy"),
            api_secret=SecretStr("dummy"),
            session_config=config4,
        )
        assert session4._build_ssl_verify_config() is True
