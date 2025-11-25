from __future__ import annotations

from typing import Any

import httpx
from pydantic import SecretStr

from crypto_api_client._base import ApiClient
from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.http._endpoint_request_builder import EndpointRequestBuilder

from ._native_messages import OrderBookMessage, Ticker, TickerMessage
from .native_domain_models import OrderBook
from .native_requests import OrderBookRequest, TickerRequest


class ExchangeApiClient(ApiClient):
    """GMO Coin exchange API client"""

    def __init__(
        self,
        *,
        # To simplify implementation, disallow None for authentication credentials
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
        :raises ValueError: If api_config is not provided
        """
        if not api_config:
            raise ValueError("api_config is required and cannot be empty")

        super().__init__(
            callbacks=callbacks,
            api_config=api_config,
            request_config=request_config,
            http_client=http_client,
        )

        self._api_key = api_key
        self._api_secret = api_secret

    # ========== Public API Methods ==========

    async def orderbook(self, request_type: OrderBookRequest) -> OrderBook:
        """Get order book

        URL structure: https://api.coin.z.com/public/v1/orderbooks?symbol=BTC_JPY

        .. seealso::
            `OrderBooks <https://api.coin.z.com/docs/#orderbooks>`__
        """
        params = request_type.to_query_params()
        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config["relative_orderbook_identifier_path"],
            params=params,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        orderbook_message = OrderBookMessage(response_data.response_body_text)
        result = orderbook_message.to_domain_model()

        return result

    async def ticker(self, request_type: TickerRequest) -> list[Ticker]:
        """Get ticker information

        URL structure: https://api.coin.z.com/public/v1/ticker?symbol=BTC_JPY

        .. seealso::

            `Ticker <https://api.coin.z.com/docs/#ticker>`__

        .. note::

            - GMO Coin API always returns responses in array format
            - Even when specifying a single symbol, it returns a list with one element
            - Omitting the symbol parameter retrieves tickers for all symbols
        """
        params = request_type.to_query_params()
        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config["relative_ticker_identifier_path"],
            params=params,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        ticker_message = TickerMessage(response_data.response_body_text)
        result = ticker_message.to_domain_model()

        if request_type.symbol is not None and len(result) == 0:
            from crypto_api_client.errors import CryptoApiClientError

            raise CryptoApiClientError(
                error_description=f"Ticker for symbol {request_type.symbol} not found"
            )

        return result

    # ========== Private API Methods (planned for future implementation) ==========
