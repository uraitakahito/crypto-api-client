from __future__ import annotations

import datetime
from typing import Any

import httpx
from pydantic import SecretStr
from yarl import URL

from crypto_api_client._base import ApiClient
from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.http._endpoint_request_builder import EndpointRequestBuilder
from crypto_api_client.http._http_method import HttpMethod
from crypto_api_client.security._hmac_signer import sign_message
from crypto_api_client.security.secret_headers import SecretHeaders

from ._native_messages import (
    Balance,
    BalancesMessage,
    Board,
    BoardMessage,
    BoardState,
    BoardStateMessage,
    CancelChildOrderMessage,
    ChildOrder,
    ChildOrdersMessage,
    HealthStatus,
    HealthStatusMessage,
    Market,
    MarketsMessage,
    PrivateExecution,
    PrivateExecutionsMessage,
    PublicExecution,
    PublicExecutionsMessage,
    SendChildOrderMessage,
    Ticker,
    TickerMessage,
    TradingCommission,
    TradingCommissionMessage,
)
from ._signature_builder import build_message
from .native_requests import (
    BoardRequest,
    BoardStateRequest,
    CancelChildOrderRequest,
    ChildOrdersRequest,
    HealthRequest,
    PrivateExecutionsRequest,
    PublicExecutionsRequest,
    SendChildOrderRequest,
    TickerRequest,
    TradingCommissionRequest,
)


class ExchangeApiClient(ApiClient):
    """bitFlyer exchange API client"""

    def __init__(
        self,
        *,
        # To simplify implementation, None is not allowed for credentials
        api_key: SecretStr,
        api_secret: SecretStr,
        callbacks: tuple[AbstractRequestCallback, ...] | None = None,
        api_config: dict[str, Any],
        request_config: dict[str, Any],
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize unified API client

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

    @property
    def _timestamp(self) -> str:
        """Generate Unix timestamp (milliseconds)

        bitFlyer API expects Unix timestamp (milliseconds).
        datetime.now().timestamp() has microsecond precision, but
        int(...*1000) truncates sub-millisecond values.

        :return: Unix timestamp string in milliseconds
        """
        return str(int(datetime.datetime.now(tz=datetime.UTC).timestamp() * 1000))

    def _build_auth_headers(
        self,
        *,
        api_key: SecretStr,
        api_secret: SecretStr,
        method: HttpMethod,
        endpoint_path: URL,
        query_params: dict[str, Any] | None = None,
        request_body: dict[str, Any] | None = None,
        timestamp: str,
    ) -> SecretHeaders:
        """Generate authentication headers

        .. note::
            To make it clear what the authentication headers are generated from,
            we explicitly pass arguments instead of using instance variables.

        :param api_key: API key
        :param api_secret: API secret
        :param method: HTTP method
        :param endpoint_path: :term:`endpoint path` (e.g., /v1/me/getbalance)
        :param query_params: Query parameters (used in GET requests)
        :param request_body: Request body (used in POST requests)
        :param timestamp: Timestamp (Unix timestamp in milliseconds)
        :return: Authentication headers
        """
        if method == HttpMethod.GET and request_body is not None:
            raise ValueError(
                f"GET request cannot have request_body. "
                f"endpoint_path={endpoint_path}, request_body={request_body}"
            )

        if method == HttpMethod.POST and query_params is not None:
            raise ValueError(
                f"POST request cannot have query_params. "
                f"endpoint_path={endpoint_path}, query_params={query_params}"
            )

        msg = build_message(
            method=method,
            endpoint_path=endpoint_path,
            query_params=query_params,
            request_body=request_body,
            timestamp=timestamp,
        )
        sign = sign_message(api_secret, msg)

        headers = {
            "ACCESS-KEY": api_key.get_secret_value(),
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-SIGN": sign,
            "Content-Type": "application/json",
        }
        return SecretHeaders(headers)

    # ========== Public API Methods ==========

    async def board(self, request_type: BoardRequest) -> Board:
        """Get order book (Board)

        URL structure: https://api.bitflyer.jp/v1/getboard?product_code=BTC_JPY

        .. seealso::

            `Order Book <https://lightning.bitflyer.com/docs?lang=en#order-book>`__
        """
        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config["relative_board_identifier_path"],
            params=request_type.to_query_params(),
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        board_message = BoardMessage(response_data.response_body_text)
        return board_message.to_domain_model()

    async def getboardstate(self, request_type: BoardStateRequest) -> BoardState:
        """Get board state

        URL structure: https://api.bitflyer.jp/v1/getboardstate?product_code=BTC_JPY

        .. seealso::

            `Orderbook status <https://lightning.bitflyer.com/docs?lang=en#orderbook-status>`__
        """
        params = request_type.to_query_params()

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config["relative_getboardstate_identifier_path"],
            params=params,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        board_state_message = BoardStateMessage(response_data.response_body_text)
        return board_state_message.to_domain_model()

    async def gethealth(self, request_type: HealthRequest) -> HealthStatus:
        """Get exchange operational status

        URL structure: https://api.bitflyer.jp/v1/gethealth?product_code=BTC_JPY

        .. seealso::

            `Exchange status <https://lightning.bitflyer.com/docs?lang=en#exchange-status>`__

        .. note::

            While you can specify a currency pair as an argument, note that the return value
            is the exchange's operational status, not the board state.

        :param request_type: Health check request
        :return: Exchange operational status
        """
        params = request_type.to_query_params()

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config["relative_gethealth_identifier_path"],
            params=params,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        health_status_message = HealthStatusMessage(response_data.response_body_text)
        return health_status_message.to_domain_model()

    async def markets(self) -> list[Market]:
        """Get list of available markets

        URL structure: https://api.bitflyer.jp/v1/markets

        .. seealso::

            `Market List <https://lightning.bitflyer.com/docs?lang=en#market-list>`__
        """
        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config["relative_markets_identifier_path"],
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        markets_message = MarketsMessage(response_data.response_body_text)
        return markets_message.to_domain_model()

    async def public_executions(
        self, request_type: PublicExecutionsRequest
    ) -> list[PublicExecution]:
        """Get execution history via Public API

        URL structure: https://api.bitflyer.jp/v1/executions?product_code=BTC_JPY

        .. seealso::

            `List Executions <https://lightning.bitflyer.com/docs?lang=en#list-executions>`__
        """
        params = request_type.to_query_params()
        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=self._api_config["relative_executions_identifier_path"],
            params=params,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        public_executions_message = PublicExecutionsMessage(
            response_data.response_body_text
        )
        return public_executions_message.to_domain_model()

    async def ticker(self, request_type: TickerRequest) -> Ticker:
        """Get ticker information

        URL structure: https://api.bitflyer.jp/v1/ticker?product_code=BTC_JPY

        .. seealso::

            `Ticker <https://lightning.bitflyer.com/docs?lang=en#ticker>`__
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

    async def cancelchildorder(self, request_type: CancelChildOrderRequest) -> None:
        """Cancel an order

        URL structure: https://api.bitflyer.jp/v1/me/cancelchildorder

        .. seealso::

            `Cancel Order <https://lightning.bitflyer.com/docs?lang=en#cancel-order>`__

        .. note::

            - This API requires authentication
            - On success, bitFlyer API returns an empty response body
        """
        relative_resource_path = self._api_config["relative_resource_identifier_path"].joinpath(
            self._api_config["cancelchildorder_action_name"].path
        )

        params = request_type.to_query_params()

        endpoint_path = self.stub_path / relative_resource_path.path

        auth_headers = self._build_auth_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            method=HttpMethod.POST,
            endpoint_path=endpoint_path,
            request_body=params,
            timestamp=self._timestamp,
        )

        endpoint_request = EndpointRequestBuilder.post(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=relative_resource_path,
            body=params,
            headers=auth_headers,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        cancel_message = CancelChildOrderMessage(response_data.response_body_text)
        # Return None since API endpoint returns empty string on success
        return cancel_message.to_domain_model()

    async def getbalance(self) -> list[Balance]:
        """URL structure: https://api.bitflyer.jp/v1/me/getbalance

        .. seealso::

            `Get Account Asset Balance <https://lightning.bitflyer.com/docs?lang=en#get-account-asset-balance>`__
        """

        relative_resource_path = self._api_config["relative_resource_identifier_path"].joinpath(
            self._api_config["getbalance_action_name"].path
        )

        endpoint_path = self.stub_path / relative_resource_path.path

        auth_headers = self._build_auth_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            method=HttpMethod.GET,
            endpoint_path=endpoint_path,
            timestamp=self._timestamp,
        )

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=relative_resource_path,
            headers=auth_headers,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        balances_message = BalancesMessage(response_data.response_body_text)
        return balances_message.to_domain_model()

    async def getchildorders(
        self, request_type: ChildOrdersRequest | None = None
    ) -> list[ChildOrder]:
        """Get list of own orders

        URL structure: https://api.bitflyer.jp/v1/me/getchildorders?product_code=BTC_JPY

        .. seealso::

            `List Orders <https://lightning.bitflyer.com/docs?lang=en#list-orders>`__

        .. note::

            This API requires authentication.
        """

        params = request_type.to_query_params() if request_type else None
        relative_resource_path = self._api_config["relative_resource_identifier_path"].joinpath(
            self._api_config["getchildorders_action_name"].path
        )

        endpoint_path = self.stub_path / relative_resource_path.path

        auth_headers = self._build_auth_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            method=HttpMethod.GET,
            endpoint_path=endpoint_path,
            query_params=params,
            timestamp=self._timestamp,
        )

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=relative_resource_path,
            params=params,
            headers=auth_headers,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        child_orders_message = ChildOrdersMessage(response_data.response_body_text)
        return child_orders_message.to_domain_model()

    async def sendchildorder(self, request_type: SendChildOrderRequest) -> str:
        """Send a new order

        URL structure: https://api.bitflyer.jp/v1/me/sendchildorder

        .. seealso::

            `Send a New Order <https://lightning.bitflyer.com/docs?lang=en#send-a-new-order>`__

        .. note::

            This API requires authentication.
        """

        relative_resource_path = self._api_config["relative_resource_identifier_path"].joinpath(
            self._api_config["sendchildorder_action_name"].path
        )

        params = request_type.to_query_params()

        endpoint_path = self.stub_path / relative_resource_path.path

        auth_headers = self._build_auth_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            method=HttpMethod.POST,
            endpoint_path=endpoint_path,
            request_body=params,
            timestamp=self._timestamp,
        )

        endpoint_request = EndpointRequestBuilder.post(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=relative_resource_path,
            body=params,
            headers=auth_headers,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        send_child_order_message = SendChildOrderMessage(
            response_data.response_body_text
        )
        return send_child_order_message.to_domain_model()

    async def gettradingcommission(
        self, request: TradingCommissionRequest
    ) -> TradingCommission:
        """Get trading commission rate

        URL structure: https://api.bitflyer.jp/v1/me/gettradingcommission?product_code=BTC_JPY

        .. seealso::

            `Get Trading Commission <https://lightning.bitflyer.com/docs?lang=en#get-trading-commission>`__

        .. note::

            This API requires authentication.
        """

        relative_resource_path = self._api_config["relative_resource_identifier_path"].joinpath(
            self._api_config["gettradingcommission_action_name"].path
        )

        params = request.to_query_params()

        endpoint_path = self.stub_path / relative_resource_path.path

        auth_headers = self._build_auth_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            method=HttpMethod.GET,
            endpoint_path=endpoint_path,
            query_params=params,
            timestamp=self._timestamp,
        )

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=relative_resource_path,
            params=params,
            headers=auth_headers,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        message = TradingCommissionMessage(response_data.response_body_text)
        return message.to_domain_model()

    async def private_executions(
        self, request: PrivateExecutionsRequest
    ) -> list[PrivateExecution]:
        """Get own execution history via Private API

        URL structure: https://api.bitflyer.jp/v1/me/getexecutions?product_code=BTC_JPY

        .. seealso::

            `List Executions <https://lightning.bitflyer.com/docs?lang=en#list-executions>`__

        .. note::

            This API requires authentication.
        """

        relative_resource_path = self._api_config["relative_resource_identifier_path"].joinpath(
            self._api_config["getexecutions_action_name"].path
        )

        params = request.to_query_params()

        endpoint_path = self.stub_path / relative_resource_path.path

        auth_headers = self._build_auth_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            method=HttpMethod.GET,
            endpoint_path=endpoint_path,
            query_params=params,
            timestamp=self._timestamp,
        )

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["base_url"],
            relative_stub_path=self._api_config["relative_stub_path"],
            relative_resource_path=relative_resource_path,
            params=params,
            headers=auth_headers,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        private_executions_message = PrivateExecutionsMessage(
            response_data.response_body_text
        )
        return private_executions_message.to_domain_model()
