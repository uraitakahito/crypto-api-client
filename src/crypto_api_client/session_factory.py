"""Session factory

Provides factory functions for creating sessions for each exchange.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, overload

import httpx
from pydantic import SecretStr

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.core.exchange_session import ExchangeSession
from crypto_api_client.core.exchange_types import Exchange
from crypto_api_client.core.session_config import SessionConfig

if TYPE_CHECKING:
    from crypto_api_client.binance.exchange_api_client import (
        ExchangeApiClient as BinanceApiClient,
    )
    from crypto_api_client.bitbank.exchange_api_client import (
        ExchangeApiClient as BitbankApiClient,
    )
    from crypto_api_client.bitflyer.exchange_api_client import (
        ExchangeApiClient as BitFlyerApiClient,
    )
    from crypto_api_client.coincheck.exchange_api_client import (
        ExchangeApiClient as CoincheckApiClient,
    )
    from crypto_api_client.gmocoin.exchange_api_client import (
        ExchangeApiClient as GmoCoinApiClient,
    )
    from crypto_api_client.upbit.exchange_api_client import (
        ExchangeApiClient as UpbitApiClient,
    )


@overload
def create_session(
    exchange: Literal[Exchange.BITFLYER],
    *,
    api_key: SecretStr | str = "dummy_api_key",
    api_secret: SecretStr | str = "dummy_api_secret",
    session_config: SessionConfig | None = None,
    callbacks: tuple[AbstractRequestCallback, ...] | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> ExchangeSession[BitFlyerApiClient]: ...


@overload
def create_session(
    exchange: Literal[Exchange.BINANCE],
    *,
    api_key: SecretStr | str = "dummy_api_key",
    api_secret: SecretStr | str = "dummy_api_secret",
    session_config: SessionConfig | None = None,
    callbacks: tuple[AbstractRequestCallback, ...] | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> ExchangeSession[BinanceApiClient]: ...


@overload
def create_session(
    exchange: Literal[Exchange.BITBANK],
    *,
    api_key: SecretStr | str = "dummy_api_key",
    api_secret: SecretStr | str = "dummy_api_secret",
    session_config: SessionConfig | None = None,
    callbacks: tuple[AbstractRequestCallback, ...] | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> ExchangeSession[BitbankApiClient]: ...


@overload
def create_session(
    exchange: Literal[Exchange.GMOCOIN],
    *,
    api_key: SecretStr | str = "dummy_api_key",
    api_secret: SecretStr | str = "dummy_api_secret",
    session_config: SessionConfig | None = None,
    callbacks: tuple[AbstractRequestCallback, ...] | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> ExchangeSession[GmoCoinApiClient]: ...


@overload
def create_session(
    exchange: Literal[Exchange.COINCHECK],
    *,
    api_key: SecretStr | str = "dummy_api_key",
    api_secret: SecretStr | str = "dummy_api_secret",
    session_config: SessionConfig | None = None,
    callbacks: tuple[AbstractRequestCallback, ...] | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> ExchangeSession[CoincheckApiClient]: ...


@overload
def create_session(
    exchange: Literal[Exchange.UPBIT],
    *,
    api_key: SecretStr | str = "dummy_api_key",
    api_secret: SecretStr | str = "dummy_api_secret",
    session_config: SessionConfig | None = None,
    callbacks: tuple[AbstractRequestCallback, ...] | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> ExchangeSession[UpbitApiClient]: ...


def create_session(
    exchange: Exchange,
    *,
    # By specifying default values for credentials, we unify error handling and omit None checks
    api_key: SecretStr | str = "dummy_api_key",
    api_secret: SecretStr | str = "dummy_api_secret",
    session_config: SessionConfig | None = None,
    callbacks: tuple[AbstractRequestCallback, ...] | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> ExchangeSession[Any]:
    """Factory function to create communication session with exchange

    .. code-block::python

        # Public API
        async with create_session(Exchange.BITFLYER) as session:
            ticker = await session.api.ticker(request)

        # Private API
        from pydantic import SecretStr
        async with create_session(
            Exchange.BITFLYER,
            api_key=SecretStr(os.environ["BITFLYER_API_KEY"]),
            api_secret=SecretStr(os.environ["BITFLYER_API_SECRET"])
        ) as session:
            balances = await session.api.getbalance()

        # Access via proxy
        config = SessionConfig(proxy_url="http://host.docker.internal:8080")
        async with create_session(Exchange.BITFLYER, session_config=config) as session:
            ticker = await session.api.ticker(request)

        # Proxy with authentication
        from pydantic import SecretStr
        config = SessionConfig(
            proxy_url="http://host.docker.internal:8080",
            proxy_auth=(SecretStr("username"), SecretStr("password"))
        )
        async with create_session(Exchange.BITFLYER, session_config=config) as session:
            ticker = await session.api.ticker(request)

    .. warning::

        ResponseValidationCallback is not automatically added. Include it explicitly in callbacks if needed.

    :param exchange: Exchange
    :type exchange: Exchange
    :param api_key: API key
    :type api_key: SecretStr | str
    :param api_secret: API secret
    :type api_secret: SecretStr | str
    :param session_config: Session configuration
    :type session_config: SessionConfig | None
    :param callbacks: Request callbacks
    :type callbacks: tuple[AbstractRequestCallback, ...] | None
    :param http_client: HTTP client provided externally for connection pooling
    :type http_client: httpx.AsyncClient | None
    :return: ExchangeSession according to exchange
    :rtype: ExchangeSession[BitFlyerApiClient] | ExchangeSession[BinanceApiClient] | ...
    :raises ValueError: If exchange is not supported
    """
    if session_config is None:
        session_config = SessionConfig()

    if isinstance(api_key, str):
        api_key = SecretStr(api_key)
    if isinstance(api_secret, str):
        api_secret = SecretStr(api_secret)

    return ExchangeSession(
        exchange=exchange,
        api_key=api_key,
        api_secret=api_secret,
        session_config=session_config,
        callbacks=callbacks,
        http_client=http_client,
    )
