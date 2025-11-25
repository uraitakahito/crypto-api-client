from __future__ import annotations

from abc import ABC, abstractmethod

from yarl import URL

from crypto_api_client.http.http_response_data import HttpResponseData
from crypto_api_client.security.secret_headers import SecretHeaders


class AbstractRequestCallback(ABC):
    """Abstract base class for callbacks invoked before and after HTTP requests."""

    @abstractmethod
    async def before_request(
        self,
        url: URL,
        headers: SecretHeaders,
        data: str | None,
    ) -> None:
        """Called asynchronously before sending request.

        :param url: Request URL
        :type url: yarl.URL
        :param headers: Request headers
        :type headers: SecretHeaders
        :param data: Request body
        :type data: str | None
        :rtype: None
        """

    @abstractmethod
    async def after_request(self, response_data: HttpResponseData) -> None:
        """Called asynchronously after receiving response

        :param response_data: HTTP response data
        :type response_data: HttpResponseData
        :rtype: None
        """
