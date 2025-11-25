from __future__ import annotations

import ssl
from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import SecretStr


@dataclass
class SessionConfig:
    """Manages HTTP client settings: connection pool, timeout, retry, proxy, etc.

    .. code-block::python

        # Basic proxy
        config = SessionConfig(proxy_url="http://host.docker.internal:8080")

        # Proxy with authentication
        config = SessionConfig(
            proxy_url="http://host.docker.internal:8080",
            proxy_auth=(SecretStr("user"), SecretStr("pass"))
        )

        # Custom CA certificate
        config = SessionConfig(
            proxy_url="http://host.docker.internal:8080",
            ssl_cert_file="/path/to/ca.pem"
        )

        # Enable loading proxy from environment variables explicitly
        config = SessionConfig(trust_env=True)
        # Default is disabled (explicit settings only)
        config = SessionConfig()  # trust_env=False
    """

    max_keepalive_connections: int = 30
    max_connections: int = 100
    keepalive_expiry: float = 30.0

    connect_timeout: float = 5.0
    read_timeout: float = 10.0
    write_timeout: float = 10.0
    pool_timeout: float = 10.0

    http2_enabled: bool = True

    user_agent: str = "crypto-api-client/1.0"

    #
    # Proxy settings
    #
    proxy_url: str | None = None
    proxy_auth: tuple[SecretStr, SecretStr] | None = None
    # httpx functionality: When True, automatically loads HTTP_PROXY/HTTPS_PROXY environment variables
    # Default is False (ignores environment variables). Enable explicitly to use environment variables
    # Reference: https://www.python-httpx.org/environment_variables/
    trust_env: bool = False

    # SSL verification settings
    verify_ssl: bool = True
    ssl_cert_file: str | None = None
    ssl_context: ssl.SSLContext | None = None

    #
    # Request settings (for RequestMixin)
    #
    request_timeout_seconds: int = 10
    request_max_retries: int = 5
    request_initial_delay_seconds: float = 1.0
    request_max_delay: float = 60.0
    request_backoff_factor: float = 2.0
    request_jitter: bool = True

    def to_httpx_limits(self) -> httpx.Limits:
        return httpx.Limits(
            max_keepalive_connections=self.max_keepalive_connections,
            max_connections=self.max_connections,
            keepalive_expiry=self.keepalive_expiry,
        )

    def to_httpx_timeout(self) -> httpx.Timeout:
        return httpx.Timeout(
            connect=self.connect_timeout,
            read=self.read_timeout,
            write=self.write_timeout,
            pool=self.pool_timeout,
        )

    def to_request_config(self) -> dict[str, Any]:
        """Get request configuration in dictionary format

        Returns a dictionary in the format expected by RequestMixin's request_config parameter.

        :return: Dictionary of request configuration (RequestMixin-compatible format)
        """
        return {
            "timeout_seconds": self.request_timeout_seconds,
            "max_retries": self.request_max_retries,
            "initial_delay_seconds": self.request_initial_delay_seconds,
            "max_delay": self.request_max_delay,
            "backoff_factor": self.request_backoff_factor,
            "jitter": self.request_jitter,
        }
