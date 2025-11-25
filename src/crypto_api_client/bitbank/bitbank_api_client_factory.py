from __future__ import annotations

from typing import Any

import httpx
from pydantic import SecretStr
from yarl import URL

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.core.api_client_factory import ApiClientFactoryBase

from .exchange_api_client import ExchangeApiClient


class BitbankApiClientFactory(ApiClientFactoryBase[ExchangeApiClient]):
    """API client factory. Holds default configuration for bitbank exchange-specific :term:`API endpoint`."""

    def get_default_config(self) -> dict[str, Any]:
        return {
            #
            # Base Configuration
            #
            "public_base_url": URL("https://public.bitbank.cc"),
            "private_base_url": URL("https://api.bitbank.cc"),
            "public_relative_stub_path": URL(""),
            "private_relative_stub_path": URL("v1"),
            "time_window_millisecond": 5000,
            #
            # Public API paths
            #
            # URL: https://public.bitbank.cc/{pair}/ticker
            "ticker_action_name": URL("ticker"),
            # URL: https://public.bitbank.cc/{pair}/depth
            "depth_action_name": URL("depth"),
            # URL: https://api.bitbank.cc/v1/spot/status
            # Note: Uses private_base_url unlike normal Public API
            "relative_spot_resource_identifier_path": URL("spot"),
            "status_action_name": URL("status"),
            #
            # Private API paths
            #
            # URL: https://api.bitbank.cc/v1/user/assets
            "relative_user_resource_identifier_path": URL("user"),
            "assets_action_name": URL("assets"),
            # URL: https://api.bitbank.cc/v1/user/spot/order
            "relative_user_spot_resource_identifier_path": URL("user/spot"),
            "order_action_name": URL("order"),
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
