from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import SecretStr

from crypto_api_client._base import ApiClient
from crypto_api_client.callbacks import AbstractRequestCallback


class ApiClientFactoryBase[TApiClient: ApiClient](ABC):
    """Base class for API client factories

    Each exchange inherits this class to implement its own factory.
    Completely encapsulates configuration and instance creation responsibilities,
    ensuring type safety.

    Type Parameters:
        TApiClient: Type of API client to create
    """

    @abstractmethod
    def get_default_config(self) -> dict[str, Any]:
        """Get default API configuration

        Returns exchange-specific endpoint configuration.
        This configuration does not change unless the exchange modifies its API specifications.

        :return: Dictionary of API configuration
        :rtype: dict[str, Any]
        """
        ...

    @abstractmethod
    def create(
        self,
        *,
        api_key: SecretStr,
        api_secret: SecretStr,
        http_client: httpx.AsyncClient,
        callbacks: tuple[AbstractRequestCallback, ...] | None,
        request_config: dict[str, Any],
    ) -> TApiClient:
        """Create API client

        :param api_key: API key
        :type api_key: SecretStr
        :param api_secret: API secret
        :type api_secret: SecretStr
        :param http_client: HTTP client
        :type http_client: httpx.AsyncClient
        :param callbacks: Request callbacks
        :type callbacks: tuple[AbstractRequestCallback, ...] | None
        :param request_config: Request configuration (timeout, retry, etc.)
        :type request_config: dict[str, Any]
        :return: Created API client
        :rtype: TApiClient
        """
        ...
