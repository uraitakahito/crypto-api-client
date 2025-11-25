from __future__ import annotations

import time
from typing import Any

import httpx
from pydantic import SecretStr
from yarl import URL

from crypto_api_client._base import ApiClient
from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.http._endpoint_request_builder import EndpointRequestBuilder
from crypto_api_client.security._hmac_signer import sign_message
from crypto_api_client.security.secret_headers import SecretHeaders

from ._native_messages import (
    BalanceMessage,
    CurrencyBalance,
    Order,
    OrderBook,
    OrderBookMessage,
    Ticker,
    TickerMessage,
    UnsettledOrdersMessage,
)
from ._signature_builder import build_message
from .native_requests import OrderBookRequest, TickerRequest


class ExchangeApiClient(ApiClient):
    """Coincheck exchange API client"""

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

    def _build_auth_headers(
        self,
        *,
        api_key: SecretStr,
        api_secret: SecretStr,
        api_endpoint: URL,
        body: str = "",
        nonce: str,
    ) -> SecretHeaders:
        """Generate authentication headers

        .. note::
            To make it clear what generates the authentication headers,
            we explicitly pass them as arguments instead of using instance variables.

        .. seealso::

            Authentication: https://coincheck.com/documents/exchange/api#auth

        :param api_key: API key
        :param api_secret: API secret
        :param api_endpoint: Complete API endpoint URL (e.g., https://coincheck.com/api/accounts/balance)
        :param body: Request body
        :param nonce: nonce value (UNIX timestamp in milliseconds)
        :return: Authentication headers
        """
        msg = build_message(
            nonce=nonce,
            api_endpoint=api_endpoint,
            body=body,
        )
        sign = sign_message(api_secret, msg)

        headers = {
            "ACCESS-KEY": api_key.get_secret_value(),
            "ACCESS-NONCE": nonce,
            "ACCESS-SIGNATURE": sign,
            "Content-Type": "application/json",
        }
        return SecretHeaders(headers)

    @property
    def _nonce(self) -> str:
        """Generate nonce value (UNIX timestamp in milliseconds)

        Coincheck API expects UNIX timestamp in milliseconds as nonce value.
        time.time() returns seconds with microsecond precision,
        but int(...*1000) truncates sub-millisecond values.

        :return: UNIX timestamp string in milliseconds
        """
        return str(int(time.time() * 1000))

    # ========== Public API Methods ==========

    async def order_book(self, request: OrderBookRequest) -> OrderBook:
        """URL structure: https://coincheck.com/api/order_books

        .. seealso::

            `Order Book <https://coincheck.com/documents/exchange/api#order-book>`__
        """
        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config["relative_order_book_identifier_path"],
            params=request.to_query_params(),
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        message = OrderBookMessage(response_data.response_body_text)
        return message.to_domain_model()

    async def ticker(self, request_type: TickerRequest) -> Ticker:
        """URL structure: https://coincheck.com/api/ticker

        .. seealso::

            `Ticker <https://coincheck.com/documents/exchange/api#ticker>`__
        """
        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config["relative_ticker_identifier_path"],
            params=request_type.to_query_params(),
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        ticker_message = TickerMessage(response_data.response_body_text)
        return ticker_message.to_domain_model()

    # ========== Private API Methods ==========

    async def balance(self) -> list[CurrencyBalance]:
        """URL structure: https://coincheck.com/api/accounts/balance

        .. seealso::

            `Balance <https://coincheck.com/documents/exchange/api#account-balance>`__
        """

        relative_resource_path = self._api_config["relative_balance_identifier_path"]
        endpoint_path = self.stub_path / relative_resource_path.path
        api_endpoint = self._api_config["base_url"].with_path(endpoint_path.path)

        auth_headers = self._build_auth_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            api_endpoint=api_endpoint,
            nonce=self._nonce,
        )

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=relative_resource_path,
            headers=auth_headers,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        balance_message = BalanceMessage(response_data.response_body_text)
        return balance_message.to_domain_model()

    async def unsettled_orders(self) -> list[Order]:
        """Get own unsettled order list

        URL structure: https://coincheck.com/api/exchange/orders/opens

        .. seealso::
            `Coincheck Unsettled order list <https://coincheck.com/ja/documents/exchange/api#order-opens>`__
        """
        relative_resource_path = self._api_config["relative_unsettled_orders_identifier_path"]
        endpoint_path = self.stub_path / relative_resource_path.path
        api_endpoint = self._api_config["base_url"].with_path(endpoint_path.path)

        auth_headers = self._build_auth_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            api_endpoint=api_endpoint,
            nonce=self._nonce,
        )

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=relative_resource_path,
            headers=auth_headers,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        message = UnsettledOrdersMessage(response_data.response_body_text)
        return message.to_domain_model()
