from __future__ import annotations

from typing import Any

import httpx
from yarl import URL

from crypto_api_client._base import ApiClient
from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.http import EndpointRequestBuilder

from ._native_messages import TickerMessage
from .native_domain_models import Ticker
from .native_requests import TickerRequest


class ExchangeApiClient(ApiClient):
    """Upbit exchange API client."""

    def __init__(
        self,
        *,
        callbacks: tuple[AbstractRequestCallback, ...] | None = None,
        api_config: dict[str, Any],
        request_config: dict[str, Any],
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize Upbit API client.

        Args:
            callbacks: Callbacks to be executed before and after requests.
            api_config: :term:`API endpoint` configuration (base_url, stub_path, etc.).
            request_config: Request configuration (timeout, etc.).
            http_client: HTTP client injected from external (for connection pooling).
        """
        super().__init__(
            callbacks=callbacks,
            api_config=api_config,
            request_config=request_config,
            http_client=http_client,
        )

    async def ticker(self, request: TickerRequest) -> list[Ticker]:
        """Retrieve ticker information.

        .. seealso::

            `API Specification <https://global-docs.upbit.com/reference/list-tickers>`__
        """
        endpoint_request = EndpointRequestBuilder.get(
            base_url=URL(self._api_config["base_url"]),
            relative_stub_path=URL(self._api_config["relative_stub_path"]),
            relative_resource_path=URL(self._api_config["relative_ticker_path"]),
            params=request.to_query_params(),
        )

        response_data = await self.send_endpoint_request(request=endpoint_request)
        ticker_message = TickerMessage(response_data.response_body_text)
        return ticker_message.to_domain_model()
