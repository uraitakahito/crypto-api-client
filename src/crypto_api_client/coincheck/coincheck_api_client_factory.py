from __future__ import annotations

from typing import Any

import httpx
from pydantic import SecretStr
from yarl import URL

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.core.api_client_factory import ApiClientFactoryBase

from .exchange_api_client import ExchangeApiClient


class CoincheckApiClientFactory(ApiClientFactoryBase[ExchangeApiClient]):
    """API client factory. Holds default configuration for Coincheck exchange-specific :term:`API endpoint`."""

    def get_default_config(self) -> dict[str, Any]:
        return {
            #
            # Base Configuration
            #
            "base_url": URL("https://coincheck.com"),
            "relative_stub_path": URL("api"),
            #
            # Public API paths
            #
            "relative_ticker_identifier_path": URL("ticker"),
            "relative_order_book_identifier_path": URL("order_books"),
            #
            # Private API paths
            #
            "relative_balance_identifier_path": URL("accounts/balance"),
            "relative_unsettled_orders_identifier_path": URL("exchange/orders/opens"),
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
