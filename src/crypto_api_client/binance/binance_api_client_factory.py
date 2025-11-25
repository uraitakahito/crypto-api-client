from __future__ import annotations

from typing import Any

import httpx
from pydantic import SecretStr
from yarl import URL

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.core.api_client_factory import ApiClientFactoryBase

from .exchange_api_client import ExchangeApiClient


class BinanceApiClientFactory(ApiClientFactoryBase[ExchangeApiClient]):
    """API client factory. Holds default configuration for BINANCE exchange-specific :term:`API endpoint`."""

    def get_default_config(self) -> dict[str, Any]:
        return {
            #
            # Base Configuration
            #
            "base_url": URL("https://api.binance.com"),
            "relative_stub_path": URL("api/v3"),
            #
            # Public API paths
            #
            "relative_depth_identifier_path": URL("depth"),
            "relative_exchange_info_identifier_path": URL("exchangeInfo"),
            "relative_ticker_24hr_identifier_path": URL("ticker/24hr"),
            #
            # Private API paths (planned for future implementation)
            #
        }

    def __init__(self):
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
            api_key=api_key,
            api_secret=api_secret,
            http_client=http_client,
            callbacks=callbacks,
            api_config=self._api_config,
            request_config=request_config,
        )
