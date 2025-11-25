"""GMO Coin :term:`response validator` implementation

With the migration from ResponseErrorRaiser to Composition pattern,
error handling logic is implemented as an independent class.
"""

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


class GmoCoinResponseValidator(AbstractRequestCallback):
    """GMO Coin error handler

    This class inherits from :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
    and detects GMO Coin API errors, raising exceptions.

    Response validation is executed in the :meth:`after_request` hook.

    Normally, obtain an instance using :func:`~crypto_api_client.factories.create_response_validator`.

    Example of HttpResponseData.text when :term:`API endpoint` determines an error:

    .. code-block:: json

        {
            "status": 1,
            "messages": [
                {
                    "message_code": "ERR-0001",
                    "message_string": "System error"
                }
            ]
        }

    .. seealso::
        - :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
        - :func:`~crypto_api_client.factories.create_response_validator`
    """

    _EXCHANGE: Final[Exchange] = Exchange.GMOCOIN
    _SUCCESS_STATUS_VALUE: Final[int] = 0
    _ERROR_MESSAGE_TEMPLATE: Final[str] = (
        "{exchange_name} API error (HTTP status {http_status_code}, API status {api_status_code}): {error_message}"
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
        :raises ExchangeApiError: If API error occurs
        :rtype: None
        """
        self._validate_response(response_data)

    def _validate_response(self, http_response_data: HttpResponseData) -> None:
        """Check response status code and raise error

        :param http_response_data: HTTP response data
        :type http_response_data: HttpResponseData
        :raises ExchangeApiError: If API error occurs
        :rtype: None
        """
        http_status_code = http_response_data.http_status_code
        response_body_text = http_response_data.response_body_text

        # Extract error information
        api_status_code, error_messages = self._extract_error_info(response_body_text)

        # Determine error
        is_success_http_status = HttpStatusCode.is_success(http_status_code)
        is_api_error = (
            api_status_code is not None
            and api_status_code != self._SUCCESS_STATUS_VALUE
        )

        if not is_success_http_status or is_api_error:
            # Build error message
            if error_messages:
                formatted_messages = [f"{code}: {msg}" for code, msg in error_messages]
                messages_str = "; ".join(formatted_messages)
                error_description = self._ERROR_MESSAGE_TEMPLATE.format(
                    exchange_name=self._EXCHANGE.display_name,
                    http_status_code=http_status_code,
                    api_status_code=api_status_code,
                    error_messages=messages_str,
                )
                api_error_message = messages_str
            else:
                error_description = self._ERROR_MESSAGE_TEMPLATE.format(
                    exchange_name=self._EXCHANGE.display_name,
                    http_status_code=http_status_code,
                    api_status_code=api_status_code,
                    error_messages=response_body_text,
                )
                api_error_message = response_body_text

            # Raise exception
            raise ExchangeApiError(
                error_description=error_description,
                http_status_code=http_status_code,
                api_status_code_1=str(api_status_code)
                if api_status_code is not None
                else None,
                api_error_message_1=api_error_message,
                response_body=response_body_text,
            )

    def _extract_error_info(
        self, response_body_text: str
    ) -> tuple[int | None, list[tuple[str, str]]]:
        """Extract error information from GMO Coin :term:`http response data` text

        :param response_body_text: Response body text
        :type response_body_text: str
        :return: Tuple of (api_status_code, error_messages)
                api_status_code: API status code (0 is success, returns None or int)
                error_messages: List of [(code, message), ...]
        :rtype: tuple[int | None, list[tuple[str, str]]]
        """
        api_status_code: int | None = None
        error_messages: list[tuple[str, str]] = []

        if not response_body_text:
            return api_status_code, error_messages

        try:
            json_data: dict[str, Any] = json.loads(response_body_text)

            api_status_code = json_data.get("status")

            messages: Any = json_data.get("messages")
            if isinstance(messages, list):
                for msg in messages:  # type: ignore[misc]
                    if isinstance(msg, dict):
                        code: Any = msg.get("message_code", "")  # type: ignore[attr-defined]
                        string: Any = msg.get("message_string", "")  # type: ignore[attr-defined]
                        # Convert to string and add
                        code_str: str = str(code) if code else ""  # type: ignore[arg-type]
                        string_str: str = str(string) if string else ""  # type: ignore[arg-type]
                        if code_str or string_str:
                            error_messages.append((code_str, string_str))

        except (json.JSONDecodeError, KeyError, TypeError):
            pass

        return api_status_code, error_messages
