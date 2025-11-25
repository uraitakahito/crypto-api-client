"""Tests for SessionConfig proxy settings."""

import ssl

from pydantic import SecretStr

from crypto_api_client.core.session_config import SessionConfig


class TestSessionConfigProxy:
    """Tests for SessionConfig proxy-related settings."""

    def test_proxy_url_basic(self) -> None:
        """Basic proxy URL configuration."""
        config = SessionConfig(proxy_url="http://host.docker.internal:8080")
        assert config.proxy_url == "http://host.docker.internal:8080"
        assert config.proxy_auth is None
        assert config.trust_env is False

    def test_proxy_auth_secret_str(self) -> None:
        """SecretStr conversion of authentication credentials."""
        config = SessionConfig(
            proxy_url="http://host.docker.internal:8080",
            proxy_auth=(SecretStr("testuser"), SecretStr("testpass")),
        )
        assert config.proxy_url == "http://host.docker.internal:8080"
        assert config.proxy_auth is not None
        assert config.proxy_auth[0].get_secret_value() == "testuser"
        assert config.proxy_auth[1].get_secret_value() == "testpass"

        # Verify SecretStr masking
        assert "testuser" not in str(config.proxy_auth[0])
        assert "testpass" not in str(config.proxy_auth[1])

    def test_ssl_verify_false(self) -> None:
        """Disable SSL verification."""
        config = SessionConfig(verify_ssl=False)
        assert config.verify_ssl is False

    def test_ssl_cert_file(self) -> None:
        """Custom CA certificate path."""
        config = SessionConfig(ssl_cert_file="/path/to/ca.pem")
        assert config.ssl_cert_file == "/path/to/ca.pem"
        assert config.verify_ssl is True

    def test_ssl_context(self) -> None:
        """Custom SSLContext."""
        ctx = ssl.create_default_context()
        config = SessionConfig(ssl_context=ctx)
        assert config.ssl_context is ctx

    def test_trust_env_default(self) -> None:
        """Default value of trust_env (False)."""
        config = SessionConfig()
        assert config.trust_env is False

    def test_trust_env_true(self) -> None:
        """Enable trust_env."""
        config = SessionConfig(trust_env=True)
        assert config.trust_env is True

    def test_default_values(self) -> None:
        """Verify default values."""
        config = SessionConfig()
        assert config.proxy_url is None
        assert config.proxy_auth is None
        assert config.trust_env is False
        assert config.verify_ssl is True
        assert config.ssl_cert_file is None
        assert config.ssl_context is None

    def test_combined_proxy_ssl_settings(self) -> None:
        """Combined proxy and SSL settings."""
        config = SessionConfig(
            proxy_url="http://host.docker.internal:8080",
            proxy_auth=(SecretStr("user"), SecretStr("pass")),
            verify_ssl=False,
        )
        assert config.proxy_url == "http://host.docker.internal:8080"
        assert config.proxy_auth is not None
        assert config.verify_ssl is False
