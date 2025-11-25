from __future__ import annotations

import json
from typing import Any, Final

from yarl import URL

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.core.exchange_types import Exchange
from crypto_api_client.errors.exceptions import ExchangeApiError
from crypto_api_client.http import HttpResponseData, HttpStatusCode
from crypto_api_client.security.secret_headers import SecretHeaders


class UpbitResponseValidator(AbstractRequestCallback):
    """Response validator handler for Upbit.

    This class inherits from :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
    and detects Upbit API errors, raising exceptions.

    Response validation is executed in the :meth:`after_request` hook.

    Typically, obtain an instance using :func:`~crypto_api_client.factories.create_response_validator`.

    Example of error text when :term:`API endpoint` determines an error:

    .. code-block:: json

        {
            "error": {
                "name": "invalid_parameter",
                "message": "markets 파라미터가 필요합니다."
            }
        }

    .. seealso::
        - `Upbit Developer Center <https://global-docs.upbit.com/docs/rest-api>`__
        - :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
        - :func:`~crypto_api_client.factories.create_response_validator`
    """

    _EXCHANGE: Final[Exchange] = Exchange.UPBIT
    _ERROR_MESSAGE_TEMPLATE: Final[str] = (
        "{exchange_name} API error (HTTP status {http_status_code}, "
        "Error name: {error_name}): {api_error_message}"
    )

    async def before_request(
        self,
        url: URL,
        headers: SecretHeaders,
        data: str | None,
    ) -> None:
        pass

    async def after_request(self, response_data: HttpResponseData) -> None:
        self._validate_response(response_data)

    def _validate_response(self, http_response_data: HttpResponseData) -> None:
        """Check HTTP response data and raise exception if error exists.

        :raises ExchangeApiError: When an API error occurs.
        """
        http_status_code = http_response_data.http_status_code

        if HttpStatusCode.is_success(http_status_code):
            return

        response_body_text = http_response_data.response_body_text
        error_name, api_error_message = self._extract_error_info(response_body_text)

        error_description = self._ERROR_MESSAGE_TEMPLATE.format(
            exchange_name=self._EXCHANGE.display_name,
            http_status_code=http_status_code,
            error_name=error_name or "Unknown",
            api_error_message=api_error_message or "No error message",
        )

        raise ExchangeApiError(
            error_description=error_description,
            http_status_code=http_status_code,
            api_status_code_1=error_name,
            api_error_message_1=api_error_message,
            response_body=response_body_text,
        )

    def _extract_error_info(
        self, response_body_text: str
    ) -> tuple[str | None, str | None]:
        """Extract error information from Upbit :term:`http response data` text.

        Upbit error response format::

            {
                "error": {
                    "name": "invalid_parameter",
                    "message": "markets 파라미터가 필요합니다."
                }
            }

        .. code-block:: python

            validator = UpbitResponseValidator()
            error_json = '{"error": {"name": "invalid_parameter", "message": "Missing markets"}}'
            validator._extract_error_info(error_json)
            # ('invalid_parameter', 'Missing markets')
        """
        error_name: str | None = None
        api_error_message: str | None = None

        try:
            parsed_data: Any = json.loads(response_body_text)
            error_dict = parsed_data.get("error", {})
            error_name = error_dict.get("name")
            api_error_message = error_dict.get("message")
        except Exception:
            api_error_message = response_body_text

        return error_name, api_error_message
