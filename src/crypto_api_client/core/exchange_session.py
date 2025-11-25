from __future__ import annotations

import ssl
from typing import Any, ClassVar, Self

import httpx
from pydantic import SecretStr
from yarl import URL

from crypto_api_client._base import ApiClient
from crypto_api_client.binance.binance_api_client_factory import BinanceApiClientFactory
from crypto_api_client.bitbank.bitbank_api_client_factory import BitbankApiClientFactory
from crypto_api_client.bitflyer.bitflyer_api_client_factory import (
    BitFlyerApiClientFactory,
)
from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.coincheck.coincheck_api_client_factory import (
    CoincheckApiClientFactory,
)
from crypto_api_client.core.api_client_factory import ApiClientFactoryBase
from crypto_api_client.core.session_config import SessionConfig
from crypto_api_client.gmocoin.gmocoin_api_client_factory import GmoCoinApiClientFactory
from crypto_api_client.upbit.upbit_api_client_factory import UpbitApiClientFactory

from .exchange_types import Exchange


class ExchangeSession[TApiClient: ApiClient]:
    """Generic exchange session

    .. code-block::python

        from crypto_api_client import Exchange, create_session

        # Using Public API
        async with create_session(Exchange.BITFLYER) as session:
            ticker = await session.api.ticker(TickerRequest(product_code=ProductCode.BTC_JPY))

        # Using Private API
        async with create_session(
            Exchange.BITFLYER,
            api_key=os.environ["BITFLYER_API_KEY"],
            api_secret=os.environ["BITFLYER_API_SECRET"]
        ) as session:
            balances = await session.api.getbalance()
    """

    _API_CLIENT_FACTORIES: ClassVar[dict[Exchange, ApiClientFactoryBase[Any]]] = {
        Exchange.BINANCE: BinanceApiClientFactory(),
        Exchange.BITBANK: BitbankApiClientFactory(),
        Exchange.BITFLYER: BitFlyerApiClientFactory(),
        Exchange.GMOCOIN: GmoCoinApiClientFactory(),
        Exchange.COINCHECK: CoincheckApiClientFactory(),
        Exchange.UPBIT: UpbitApiClientFactory(),
    }

    def __init__(
        self,
        *,
        exchange: Exchange,
        api_key: SecretStr,
        api_secret: SecretStr,
        session_config: SessionConfig | None = None,
        callbacks: tuple[AbstractRequestCallback, ...] | None = None,
        http_client: httpx.AsyncClient | None = None,
    ):
        if exchange not in self._API_CLIENT_FACTORIES:
            raise ValueError(f"Unsupported exchange: {exchange}")

        self._exchange = exchange
        api_client_factory = self._API_CLIENT_FACTORIES[exchange]

        self._session_config = session_config or SessionConfig()
        self._callbacks = callbacks if callbacks else ()
        self._closed = False

        if http_client is None:
            self._http_client = self._create_http_client()
            self._owns_http_client = True
        else:
            self._http_client = http_client
            self._owns_http_client = False

        self._api_client: TApiClient = self._create_api_client(
            api_client_factory, api_key, api_secret
        )

    def _create_http_client(self) -> httpx.AsyncClient:
        """Create HTTP client

        About trust_env:
            With httpx functionality, when trust_env=True,
            HTTP_PROXY/HTTPS_PROXY/ALL_PROXY/NO_PROXY environment variables are automatically loaded.
            Default is False (ignores environment variables). To use environment variables,
            explicitly specify SessionConfig(trust_env=True).

            Reference: https://www.python-httpx.org/environment_variables/
        """
        proxy = self._build_proxy_config()
        verify = self._build_ssl_verify_config()

        return httpx.AsyncClient(
            limits=self._session_config.to_httpx_limits(),
            timeout=self._session_config.to_httpx_timeout(),
            http2=self._session_config.http2_enabled,
            headers={"User-Agent": self._session_config.user_agent},
            follow_redirects=False,
            proxy=proxy,
            verify=verify,
            trust_env=self._session_config.trust_env,  # httpx automatically loads environment variables
        )

    def _build_proxy_config(self) -> str | None:
        """Build proxy configuration

        If proxy_auth is set, embeds authentication info in the URL.
        Uses SecretStr, so automatically masked in log output.

        :return: Proxy URL (may include authentication info), or None
        :rtype: str | None
        """
        if not self._session_config.proxy_url:
            return None

        proxy_url = self._session_config.proxy_url

        if self._session_config.proxy_auth:
            username, password = self._session_config.proxy_auth
            url = URL(proxy_url)
            url = url.with_user(username.get_secret_value())
            url = url.with_password(password.get_secret_value())
            proxy_url = str(url)

        return proxy_url

    def _build_ssl_verify_config(self) -> bool | str | ssl.SSLContext:
        """Build SSL verification configuration

        Priority:
        1. ssl_context (advanced configuration)
        2. verify_ssl=False (disable verification - creates SSLContext to work with proxies)
        3. ssl_cert_file (custom CA certificate)
        4. True (default verification)

        Note: When verify_ssl=False, returns ssl.SSLContext instead of bool False
        to work with HTTPS connections through proxies. This works around httpx/httpcore limitations.

        :return: SSL verification configuration
        :rtype: bool | str | ssl.SSLContext
        """
        if self._session_config.ssl_context:
            return self._session_config.ssl_context

        if not self._session_config.verify_ssl:
            # Create SSLContext to work with HTTPS connections through proxies
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            return ssl_context

        if self._session_config.ssl_cert_file:
            return self._session_config.ssl_cert_file

        return True

    def _create_api_client(
        self,
        api_client_factory: ApiClientFactoryBase[TApiClient],
        api_key: SecretStr,
        api_secret: SecretStr,
    ) -> TApiClient:
        """Create API client

        :param api_client_factory: API client factory
        :param api_key: API key
        :param api_secret: API secret
        :return: Created API client
        """
        return api_client_factory.create(
            api_key=api_key,
            api_secret=api_secret,
            http_client=self._http_client,
            callbacks=self._callbacks,
            request_config=self._session_config.to_request_config(),
        )

    @property
    def api(self) -> TApiClient:
        """Get API client

        :return: API client
        :raises RuntimeError: If session is already closed
        """
        if self._closed:
            raise RuntimeError("Session is already closed")

        return self._api_client

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    @property
    def config(self) -> SessionConfig:
        return self._session_config

    @property
    def is_closed(self) -> bool:
        return self._closed

    @property
    def callbacks(self):
        return self._callbacks

    async def close(self) -> None:
        if self._closed:
            return

        self._closed = True

        # Close HTTP client (only if owned)
        if self._owns_http_client and self._http_client:
            await self._http_client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
