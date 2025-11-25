from __future__ import annotations

import json
from typing import Any, Final

from yarl import URL

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.core.exchange_types import Exchange
from crypto_api_client.errors.exceptions import ExchangeApiError
from crypto_api_client.http._http_status_code import HttpStatusCode
from crypto_api_client.http.http_response_data import HttpResponseData
from crypto_api_client.security.secret_headers import SecretHeaders


class BitFlyerResponseValidator(AbstractRequestCallback):
    """bitFlyer response validation handler

    This class inherits from :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
    and detects bitFlyer API errors, raising exceptions when errors occur.

    Response validation is executed in the :meth:`after_request` hook.

    Typically, use :func:`~crypto_api_client.factories.create_response_validator` to obtain an instance.

    Example text when :term:`API endpoint` returns an error:

    .. code-block:: json

        {
            "status":-500,
            "error_message":"Invalid signature",
            "data":null
        }

    .. seealso::
        - `bitFlyer(bF) Error Code List <https://note.com/17num/n/n6955c3a711a8>`__
        - :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
        - :func:`~crypto_api_client.factories.create_response_validator`
    """

    _EXCHANGE: Final[Exchange] = Exchange.BITFLYER
    _ERROR_MESSAGE_TEMPLATE: Final[str] = (
        "{exchange_name} API error (HTTP status {http_status_code}, API status {api_status_code}): {api_error_message}"
    )

    async def before_request(
        self,
        url: URL,
        headers: SecretHeaders,
        data: str | None,
    ) -> None:
        """Pre-request processing (does nothing for response validation)

        :param url: Request URL
        :type url: yarl.URL
        :param headers: Request headers
        :type headers: SecretHeaders
        :param data: Request body
        :type data: str | None
        :rtype: None
        """
        pass

    async def after_request(self, response_data: HttpResponseData) -> None:
        """Post-response validation processing

        :param response_data: HTTP response data
        :type response_data: HttpResponseData
        :raises ExchangeApiError: When an API error occurs
        :rtype: None
        """
        self._validate_response(response_data)

    def _validate_response(self, http_response_data: HttpResponseData) -> None:
        """Check HTTP response data and raise exception if error exists

        :param http_response_data: HTTP response data
        :type http_response_data: HttpResponseData
        :raises ExchangeApiError: When an API error occurs
        :rtype: None
        """
        http_status_code = http_response_data.http_status_code

        if HttpStatusCode.is_success(http_status_code):
            return

        response_body_text = http_response_data.response_body_text
        bitflyer_status_code, api_error_message = self._extract_error_info(
            response_body_text
        )
        error_description = self._ERROR_MESSAGE_TEMPLATE.format(
            exchange_name=self._EXCHANGE.display_name,
            http_status_code=http_status_code,
            api_status_code=bitflyer_status_code,
            api_error_message=api_error_message,
        )

        raise ExchangeApiError(
            error_description=error_description,
            http_status_code=http_status_code,
            api_status_code_1=str(bitflyer_status_code)
            if bitflyer_status_code is not None
            else None,
            api_error_message_1=api_error_message,
            response_body=response_body_text,
        )

    def _extract_error_info(
        self, response_body_text: str
    ) -> tuple[int | None, str | None]:
        """Extract error information from bitFlyer :term:`http response data` text

        :param response_body_text: Response body text
        :type response_body_text: str
        :return: Tuple of (bitflyer_status_code, api_error_message)
        :rtype: tuple[int | None, str | None]

        """
        bitflyer_status_code: int | None = None
        api_error_message: str | None = None

        try:
            parsed_data: Any = json.loads(response_body_text)
            api_error_message = parsed_data["error_message"]
            bitflyer_status_code = parsed_data["status"]
        except Exception:
            pass

        return bitflyer_status_code, api_error_message
