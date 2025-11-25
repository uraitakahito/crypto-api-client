from __future__ import annotations

from typing import Any

import httpx
from pydantic import SecretStr

from crypto_api_client._base import ApiClient
from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.http._endpoint_request_builder import EndpointRequestBuilder

from ._native_messages import (
    Depth,
    DepthMessage,
    ExchangeInfo,
    ExchangeInfoMessage,
    Ticker,
    TickerMessage,
)
from .native_requests import DepthRequest, ExchangeInfoRequest, TickerRequest


class ExchangeApiClient(ApiClient):
    """BINANCE exchange API client"""

    def __init__(
        self,
        *,
        # Disallow None for authentication info to simplify implementation
        api_key: SecretStr,
        api_secret: SecretStr,
        callbacks: tuple[AbstractRequestCallback, ...] | None = None,
        api_config: dict[str, Any],
        request_config: dict[str, Any],
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize integrated API client

        :param api_key: API key (required, use dummy value for Public API)
        :param api_secret: API secret (required, use dummy value for Public API)
        :param callbacks: Request callbacks
        :param api_config: API endpoint configuration
        :param request_config: Request configuration
        :param http_client: HTTP client
        """

        super().__init__(
            callbacks=callbacks,
            api_config=api_config,
            request_config=request_config,
            http_client=http_client,
        )

        self._api_key = api_key
        self._api_secret = api_secret

    # ========== Public API Methods ==========

    async def depth(self, request_type: DepthRequest) -> Depth:
        """Get order book (Depth)

        URL structure: https://api.binance.com/api/v3/depth?symbol=BTCUSDT

        .. seealso::

            `Order Book <https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#order-book>`__
        """
        params = request_type.to_query_params()
        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config["relative_depth_identifier_path"],
            params=params,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        depth_message = DepthMessage(response_data.response_body_text)
        return depth_message.to_domain_model()

    async def exchange_info(
        self, request_type: ExchangeInfoRequest | None = None
    ) -> ExchangeInfo:
        """Get exchange information

        URL structure: https://api.binance.com/api/v3/exchangeInfo

        .. seealso::
            `Exchange Information <https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information>`_
        """
        params = request_type.to_query_params() if request_type else {}
        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config[
                "relative_exchange_info_identifier_path"
            ],
            params=params,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        exchange_info_message = ExchangeInfoMessage(response_data.response_body_text)
        return exchange_info_message.to_domain_model()

    async def ticker_24hr(self, request_type: TickerRequest) -> Ticker:
        """Get 24-hour ticker information

        URL structure: https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT

        .. seealso::

            `24hr Ticker Price Change Statistics <https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#24hr-ticker-price-change-statistics>`__

        :param request_type: Request object containing symbol (required)
        """
        params = request_type.to_query_params()
        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config[
                "relative_ticker_24hr_identifier_path"
            ],
            params=params,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        ticker_message = TickerMessage(response_data.response_body_text)
        return ticker_message.to_domain_model()

    # ========== Private API Methods (planned for future implementation) ==========
