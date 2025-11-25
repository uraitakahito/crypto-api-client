from __future__ import annotations

from typing import Any

import httpx
from yarl import URL

from ..callbacks import AbstractRequestCallback
from ..http._request_mixin import RequestMixin


class ApiClient(RequestMixin):
    """Base API client class common to all exchanges.

    Provides common implementation, with error handling realized through the callback system.

    :ivar _api_config: API endpoint configuration (base_url, relative_stub_path, etc.)
    """

    def __init__(
        self,
        *,
        callbacks: tuple[AbstractRequestCallback, ...] | None = None,
        api_config: dict[str, Any],
        request_config: dict[str, Any],
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize API client.

        :param callbacks: Callbacks executed before and after HTTP requests
        :type callbacks: tuple[AbstractRequestCallback, ...] | None
        :param api_config: API endpoint configuration. Includes the following keys:

            - base_url: Base URL of the API (required)
            - relative_stub_path: API's :term:`relative stub path` (optional, default: "")
        :type api_config: dict[str, Any]
        :param request_config: Request configuration (timeout, retry, etc.) - required
        :type request_config: dict[str, Any]
        :param http_client: Custom HTTP client (for connection pooling)
        :type http_client: httpx.AsyncClient | None
        """
        # Initialize RequestMixin
        super().__init__(
            callbacks=callbacks,
            request_config=request_config,
            http_client=http_client,
        )

        self._api_config = api_config

    @property
    def stub_path(self) -> URL:
        relative_stub_path = self._api_config.get("relative_stub_path", "")
        if not relative_stub_path:
            return URL("")
        return URL("/") / URL(relative_stub_path).path

    @property
    def private_stub_path(self) -> URL:
        relative_stub_path = self._api_config.get("private_relative_stub_path", "")
        if not relative_stub_path:
            # fallback to regular stub_path
            return self.stub_path
        return URL("/") / URL(relative_stub_path).path
