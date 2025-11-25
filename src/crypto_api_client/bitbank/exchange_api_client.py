from __future__ import annotations

import time
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

from ._native_messages.assets_message import AssetsMessage
from ._native_messages.create_order_message import CreateOrderMessage
from ._native_messages.depth_message import DepthMessage
from ._native_messages.spot_status_message import SpotStatusMessage
from ._native_messages.ticker_message import TickerMessage
from ._signature_builder import build_message
from .native_domain_models import Asset, Order, Ticker
from .native_domain_models.depth import Depth
from .native_domain_models.spot_status import SpotStatus
from .native_requests import CreateOrderRequest, SpotStatusRequest, TickerRequest
from .native_requests.depth_request import DepthRequest


class ExchangeApiClient(ApiClient):
    """bitbank exchange API client"""

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
        method: HttpMethod,
        endpoint_path: URL,
        query_params: dict[str, str] | None = None,
        request_body: dict[str, str | bool] | None = None,
        request_time: str,
        time_window_millisecond: str,
    ) -> SecretHeaders:
        """Generate authentication headers

        .. note::
            To make it clear what the authentication headers are generated from, we explicitly pass parameters instead of using instance variables.

        :param api_key: API key
        :param api_secret: API secret
        :param method: HTTP method (HttpMethod.GET or HttpMethod.POST)
        :param endpoint_path: :term:`endpoint path` . (e.g. /v1/user/assets)
        :param query_params: Query parameters (used for GET requests)
        :param request_body: Request body (used for POST requests)
        :param request_time: Request time (Unix timestamp in milliseconds)
        :param time_window_millisecond: Time window (milliseconds)
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
            request_time=request_time,
            time_window_millisecond=time_window_millisecond,
        )
        sign = sign_message(api_secret, msg)

        headers = {
            "ACCESS-KEY": api_key.get_secret_value(),
            "ACCESS-REQUEST-TIME": request_time,
            "ACCESS-TIME-WINDOW": time_window_millisecond,
            "ACCESS-SIGNATURE": sign,
            "Content-Type": "application/json",
        }
        return SecretHeaders(headers)

    def _request_time_and_window(self) -> tuple[str, str]:
        """Generate current request time and time window

        :return: Tuple of (request time, time window)
        """
        current_time_ms = int(time.time() * 1000)
        return str(current_time_ms), str(self._api_config["time_window_millisecond"])

    # ========== Public API Methods ==========

    async def depth(self, request_type: DepthRequest) -> Depth:
        """Get order book (Depth)

        URL structure: https://public.bitbank.cc/btc_jpy/depth

        .. seealso::

            `Depth <https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-api_JP.md#depth>`__
        """
        pair_str = request_type.pair
        relative_resource_identifier_path = URL(pair_str)
        relative_resource_path = relative_resource_identifier_path.joinpath(
            self._api_config["depth_action_name"].path
        )

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["public_base_url"],
            relative_stub_path=self._api_config["public_relative_stub_path"],
            relative_resource_path=relative_resource_path,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        depth_message = DepthMessage(response_data.response_body_text)
        return depth_message.to_domain_model()

    async def spot_status(self, request_type: SpotStatusRequest) -> SpotStatus:
        """Get exchange status

        URL structure: https://api.bitbank.cc/v1/spot/status

        .. seealso::

            `Get exchange status <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#get-exchange-status>`__

        :param request_type: Status request
        :return: Exchange status information

        .. note::

            - resource identifier path: ``spot``
            - action name: ``status``
            - spot/status uses private_base_url unlike normal Public API
        """
        relative_resource_path = self._api_config[
            "relative_spot_resource_identifier_path"
        ].joinpath(self._api_config["status_action_name"].path)

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["private_base_url"],
            relative_stub_path=self._api_config["private_relative_stub_path"],
            relative_resource_path=relative_resource_path,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        spot_status_message = SpotStatusMessage(response_data.response_body_text)
        return spot_status_message.to_domain_model()

    async def ticker(self, request_type: TickerRequest) -> Ticker:
        """Get ticker information

        URL structure: https://public.bitbank.cc/btc_jpy/ticker

        .. seealso::

            `Ticker <https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-api.md#ticker>`__
        """
        pair_str = request_type.pair
        relative_resource_identifier_path = URL(pair_str)
        relative_resource_path = relative_resource_identifier_path.joinpath(
            self._api_config["ticker_action_name"].path
        )

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["public_base_url"],
            relative_stub_path=self._api_config["public_relative_stub_path"],
            relative_resource_path=relative_resource_path,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        ticker_message = TickerMessage(response_data.response_body_text)
        return ticker_message.to_domain_model()

    # ========== Private API Methods ==========

    async def assets(self) -> list[Asset]:
        """Get asset information

        URL structure: https://api.bitbank.cc/v1/user/assets

        .. seealso::

            `Assets <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#return-users-asset-list>`__
        """
        request_time, time_window = self._request_time_and_window()

        action_name = self._api_config["assets_action_name"]
        relative_resource_identifier_path = self._api_config[
            "relative_user_resource_identifier_path"
        ]

        relative_resource_path = relative_resource_identifier_path.joinpath(
            action_name.path
        )
        endpoint_path = self.private_stub_path / relative_resource_path.path

        auth_headers = self._build_auth_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            method=HttpMethod.GET,
            endpoint_path=endpoint_path,
            request_time=request_time,
            time_window_millisecond=time_window,
        )

        endpoint_request = EndpointRequestBuilder.get(
            base_url=self._api_config["private_base_url"],
            relative_stub_path=self._api_config["private_relative_stub_path"],
            relative_resource_path=relative_resource_path,
            headers=auth_headers,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        assets_message = AssetsMessage(response_data.response_body_text)
        return assets_message.to_domain_model()

    async def create_order(self, request: CreateOrderRequest) -> Order:
        """Submit new order

        URL structure: https://api.bitbank.cc/v1/user/spot/order

        .. seealso::

            `Create new order <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#create-new-order>`__

        .. note::

            - resource identifier path: ``user/spot``
            - action name: ``order``
        """
        request_time, time_window = self._request_time_and_window()

        action_name = self._api_config["order_action_name"]
        relative_resource_identifier_path = self._api_config[
            "relative_user_spot_resource_identifier_path"
        ]

        relative_resource_path = relative_resource_identifier_path.joinpath(
            action_name.path
        )

        params = request.to_query_params()

        endpoint_path = self.private_stub_path / relative_resource_path.path

        auth_headers = self._build_auth_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            method=HttpMethod.POST,
            endpoint_path=endpoint_path,
            request_time=request_time,
            time_window_millisecond=time_window,
            request_body=params,
        )

        endpoint_request = EndpointRequestBuilder.post(
            base_url=self._api_config["private_base_url"],
            relative_stub_path=self._api_config["private_relative_stub_path"],
            relative_resource_path=relative_resource_path,
            body=params,
            headers=auth_headers,
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)

        create_order_message = CreateOrderMessage(response_data.response_body_text)
        return create_order_message.to_domain_model()
