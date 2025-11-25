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


class CoincheckResponseValidator(AbstractRequestCallback):
    """Coincheck error handler

    This class inherits from :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
    and detects Coincheck API errors and raises exceptions.

    Response validation is executed in the :meth:`after_request` hook.

    Normally, use :func:`~crypto_api_client.factories.create_response_validator` to obtain an instance.

    Example of text when :term:`API endpoint` judges an error:

    .. code-block:: json

        {
            "success": false,
            "error": "invalid authentication"
        }

    .. seealso::
        - `Coincheck API Documentation <https://coincheck.com/ja/documents/exchange/api>`__
        - :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
        - :func:`~crypto_api_client.factories.create_response_validator`
    """

    _EXCHANGE: Final[Exchange] = Exchange.COINCHECK
    _ERROR_MESSAGE_TEMPLATE: Final[str] = (
        "{exchange_name} API error (HTTP status {http_status_code}): {api_error_message}"
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

        :raises ExchangeApiError: When API error occurs
        """
        self._validate_response(response_data)

    def _validate_response(self, http_response_data: HttpResponseData) -> None:
        """Check HTTP response data and raise exception if error

        :raises ExchangeApiError: When API error occurs
        """
        http_status_code = http_response_data.http_status_code

        if HttpStatusCode.is_success(http_status_code):
            return

        response_body_text = http_response_data.response_body_text
        success, api_error_message = self._extract_error_info(response_body_text)
        error_description = self._ERROR_MESSAGE_TEMPLATE.format(
            exchange_name=self._EXCHANGE.display_name,
            http_status_code=http_status_code,
            api_error_message=api_error_message,
        )

        raise ExchangeApiError(
            error_description=error_description,
            http_status_code=http_status_code,
            api_status_code_1=str(success) if success is not None else None,
            api_error_message_1=api_error_message,
            response_body=response_body_text,
        )

    def _extract_error_info(
        self, response_body_text: str
    ) -> tuple[bool | None, str | None]:
        """Extract error information from Coincheck :term:`http response data` text

        :param response_body_text: Response body text
        :type response_body_text: str
        :return: Tuple of (success value, API error message)
        :rtype: tuple[bool | None, str | None]
        """
        success: bool | None = None
        api_error_message: str | None = None

        try:
            parsed_data: dict[str, Any] = json.loads(response_body_text)

            success_value = parsed_data.get("success")
            if isinstance(success_value, bool):
                success = success_value

            error_value = parsed_data.get("error")
            if isinstance(error_value, str):
                api_error_message = error_value
        except Exception:
            pass

        return success, api_error_message
