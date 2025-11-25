from __future__ import annotations

from typing import Any

import httpx
from pydantic import SecretStr
from yarl import URL

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.core.api_client_factory import ApiClientFactoryBase

from .exchange_api_client import ExchangeApiClient


class UpbitApiClientFactory(ApiClientFactoryBase[ExchangeApiClient]):
    """API client factory. Holds default configuration for Upbit exchange-specific :term:`API endpoint`."""

    def get_default_config(self) -> dict[str, Any]:
        return {
            #
            # Base Configuration
            #
            "base_url": URL("https://api.upbit.com"),
            "relative_stub_path": URL("v1"),
            #
            # Public API paths
            #
            "relative_ticker_path": URL("ticker"),
            # Future additions:
            # "relative_orderbook_path": URL("orderbook"),
            # "relative_trades_path": URL("trades"),
            # "relative_candles_path": URL("candles"),
            #
            # Private API paths (future implementation)
            #
            # "relative_accounts_path": URL("accounts"),
            # "relative_orders_path": URL("orders"),
        }

    def __init__(self) -> None:
        self._api_config = self.get_default_config()

    def create(
        self,
        *,
        api_key: SecretStr,
        api_secret: SecretStr,
        http_client: httpx.AsyncClient,
        callbacks: tuple[AbstractRequestCallback, ...] | None,
        request_config: dict[str, Any],
    ) -> ExchangeApiClient:
        return ExchangeApiClient(
            callbacks=callbacks,
            api_config=self._api_config,
            request_config=request_config,
            http_client=http_client,
        )
