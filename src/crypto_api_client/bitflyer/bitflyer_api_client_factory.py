from __future__ import annotations

from typing import Any

import httpx
from pydantic import SecretStr
from yarl import URL

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.core.api_client_factory import ApiClientFactoryBase

from .exchange_api_client import ExchangeApiClient


class BitFlyerApiClientFactory(ApiClientFactoryBase[ExchangeApiClient]):
    """API client factory. Holds default configuration for bitFlyer exchange-specific :term:`API endpoint`."""

    def get_default_config(self) -> dict[str, Any]:
        return {
            #
            # Base Configuration
            #
            "base_url": URL("https://api.bitflyer.jp"),
            "relative_stub_path": URL("v1"),
            #
            # Public API paths
            #
            "relative_board_identifier_path": URL("getboard"),
            "relative_executions_identifier_path": URL("executions"),
            "relative_getboardstate_identifier_path": URL("getboardstate"),
            "relative_gethealth_identifier_path": URL("gethealth"),
            "relative_markets_identifier_path": URL("markets"),
            "relative_ticker_identifier_path": URL("ticker"),
            #
            # Private API paths
            #
            "relative_resource_identifier_path": URL("me"),
            "getbalance_action_name": URL("getbalance"),
            "getchildorders_action_name": URL("getchildorders"),
            "getexecutions_action_name": URL("getexecutions"),
            "gettradingcommission_action_name": URL("gettradingcommission"),
            "sendchildorder_action_name": URL("sendchildorder"),
            "cancelchildorder_action_name": URL("cancelchildorder"),
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
