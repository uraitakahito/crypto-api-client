
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


class BitbankResponseValidator(AbstractRequestCallback):
    """bitbank error handler

    This class inherits from :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
    and detects bitbank API errors and raises exceptions.

    Response validation is executed in the :meth:`after_request` hook.

    Normally, use :func:`~crypto_api_client.factories.create_response_validator` to obtain an instance.

    .. note::

        bitbank returns HTTP status code 200 even for authentication errors, so errors cannot be determined solely by HTTP response status code.

    Example of HttpResponseData.text when :term:`API endpoint` judges an error:

    .. code-block:: json

        {
            "success": 0,
            "data": {
                "code": "20003"
            }
        }

    .. seealso::
        - `Error codes for Bitbank <https://github.com/bitbankinc/bitbank-api-docs/blob/master/errors.md>`__
        - :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
        - :func:`~crypto_api_client.factories.create_response_validator`
    """

    _EXCHANGE: Final[Exchange] = Exchange.BITBANK
    _ERROR_VALUE: Final[int] = 0
    _SUCCESS_VALUE: Final[int] = 1

    _ERROR_MESSAGE_TEMPLATE: Final[str] = (
        "{exchange_name} API error (HTTP status {http_status_code}, API code {api_error_code}): {api_error_message}"
    )

    # Error code to message mapping dictionary
    # bitbank only returns error codes which is inconvenient, so we provide a mapping of codes to messages
    _ERROR_MESSAGES: Final[dict[str, str]] = {
        # SYSTEM_ERROR
        "10000": "Url not found.",
        "10001": "System error.",
        "10002": "Malformed request.",
        "10003": "System error.",
        "10005": "Timeout waiting for response.",
        "10007": "System maintenance.",
        "10008": "Server is busy. Retry later.",
        "10009": "You sent requests too frequently. Retry later with decreased requests.",
        # AUTHENTICATION_ERROR
        "20001": "Authentication failed api authorization.",
        "20002": "Invalid ACCESS-KEY.",
        "20003": "ACCESS-KEY not found.",
        "20004": "ACCESS-NONCE not found.",
        "20005": "Invalid ACCESS-SIGNATURE.",
        "20011": "MFA failed.",
        "20014": "SMS verification failed.",
        "20018": "Please login. (This happens when you request API without `/v1/`.)",
        "20019": "Please login. (This also happens when you request API without `/v1/`.)",
        "20023": "Missing OTP code.",
        "20024": "Missing SMS code.",
        "20025": "Missing OTP and SMS code.",
        "20026": "MFA is temporarily locked because too many failures. Please retry after 60 seconds.",
        "20033": "ACCESS-REQUEST-TIME not found.",
        "20034": "Invalid time of ACCESS-REQUEST-TIME.",
        "20035": "No request was sent within ACCESS-TIME-WINDOW.",
        "20036": "ACCESS-REQUEST-TIME and ACCESS-NONCE not found.",
        "20037": "Invalid ACCESS-REQUEST-TIME.",
        "20038": "Invalid ACCESS-TIME-WINDOW.",
        "20039": "Invalid ACCESS-NONCE.",
        # REQUIRED_PARAMETER_ERROR
        "30001": "Required order quantity.",
        "30006": "Required order id.",
        "30007": "Required order id array.",
        "30009": "Required asset.",
        "30012": "Required amount.",
        "30013": "Required order type.",
        "30015": "Required order side.",
        "30016": "Required asset.",
        "30019": "Required uuid.",
        "30039": "Required price.",
        "30101": "Required trigger price.",
        "30107": "Required 'pair'.",
        "30113": "Please specify 'since' or 'end' param.",
        "30117": "Required 'stop' or 'stop_limit'.",
        "30120": "Required 'stop_id' or 'stop_ids'.",
        "30121": "Too many stop order ids.",
        "30122": "Required 'stop_price' or 'stop_trigger_price'.",
        "30123": "Stop order id does not found.",
        # INVALID_PARAMETER_ERROR
        "40001": "Invalid order quantity.",
        "40006": "Invalid count.",
        "40007": "Invalid end param.",
        "40008": "Invalid end_id param.",
        "40009": "Invalid from_id param.",
        "40013": "Invalid order id.",
        "40014": "Invalid order id array.",
        "40015": "Invalid order type.",
        "40016": "Invalid asset.",
        "40017": "Invalid order side.",
        "40020": "Invalid uuid.",
        "40021": "Invalid price.",
        "40025": "Invalid amount.",
        "40028": "Invalid since param.",
        "40048": "Invalid user withdrawal limit.",
        "40112": "Invalid request body.",
        "40113": "Invalid pair.",
        "40114": "Invalid json format.",
        "40121": "Invalid stop order type.",
        "40122": "Invalid stop order side.",
        "40123": "Invalid stop price.",
        "40124": "Invalid stop order quantity.",
        "40126": "Invalid stop trigger price.",
        "40127": "pair does not match.",
        "40200": "Invalid order.",
        # DATA_ERROR
        "50003": "Account is restricted.",
        "50004": "Account is provisional.",
        "50005": "Account is blocked.",
        "50006": "Account is blocked.",
        "50008": "Identity verification is not confirmed.",
        "50009": "Order not found.",
        "50010": "Order can not be canceled.",
        "50011": "Api not found.",
        "50026": "Order has already been canceled.",
        "50027": "Order has already been executed.",
        "50028": "Buy order has already been placed.",
        "50029": "Sell order has already been placed.",
        "50030": "Buy and Sell orders have already been placed.",
        "50031": "Stop order has already been placed.",
        "50032": "Stop order has already been canceled.",
        "50033": "Stop order has already been triggered.",
        "50034": "Order does not exist.",
        "50035": "Stop order does not exist.",
        "50036": "Too many stop orders.",
        "50037": "Too many stop orders for same pair.",
        "50038": "Too many stop orders for all pairs.",
        "50040": "Pair suspension.",
        "50041": "Pair has already been suspended. Pair will become active shortly.",
        "50042": "Order or stop order has already been canceled.",
        "50043": "Cannot create buy order while short position exists.",
        "50044": "Cannot create sell order while long position exists.",
        "50050": "Withdrawal account registration has not been completed.",
        "50052": "Withdrawal destination is not registered.",
        "50064": "Withdrawal is restricted.",
        "50065": "Withdrawal is disabled.",
        "50066": "Withdrawal amount is over monthly limit.",
        "50067": "Deposit is disabled.",
        "50068": "Withdrawal is disabled temporary.",
        "50069": "Deposit is disabled temporary.",
        "50070": "User margin flag is off. Use 'Spot' account to create orders.",
        "50071": "User spot flag is off. Use 'Margin' account to create orders.",
        "50072": "Cannot specify both user spot and margin flags.",
        "50073": "Spot trading is disabled.",
        "50074": "Margin trading is disabled.",
        "50075": "Spot trading is temporarily disabled.",
        "50076": "Margin trading is temporarily disabled.",
        "50077": "Lending is temporarily disabled.",
        "50078": "Cannot lend or borrow asset while position exists.",
        "50079": "Too many lending offers.",
        "50080": "Loan cannot be canceled.",
        "50081": "Lending/borrowing is disabled.",
        "50082": "Too many open loan offers.",
        "50083": "Withdrawal is limited temporarily until collateral coverage is recovered.",
        # VALUE_ERROR
        "60001": "Insufficient amount.",
        "60002": "Market buy order quantity exceeded upper limit.",
        "60003": "Order quantity exceeded limit.",
        "60004": "Order quantity is below lower threshold.",
        "60005": "Order price exceeded upper limit.",
        "60006": "Order price is below lower limit.",
        "60011": "Too many simultaneous orders.",
        "60016": "Trigger price exceeded upper limit.",
        "60017": "Withdrawal amount exceeded upper limit.",
        "60018": "Trigger price can not be specified to trigger immediately.",
        "60019": "TakeProfit/StopLoss order side must be in close direction.",
        "60020": "Withdrawal amount is below lower limit.",
        # STOP_UPDATE_REQUEST_SYSTEM_STATUS
        "70001": "System error.",
        "70002": "System is currently unavailable.",
        "70003": "Please wait and try again.",
        "70004": "Too many orders are queued.",
        "70010": "Too many orders.",
        "70011": "Too many orders are queued. Please wait and try again.",
        "70012": "Too many conditional orders.",
        "70013": "Too many conditional orders are queued. Please wait and try again.",
        "70014": "Too many cancel or update orders.",
        "70015": "Too many cancel or update orders are queued. Please wait and try again.",
        "70016": "Received an incorrect order.",
        "70017": "From/To reversed.",
        "70018": "Too many requests via web.",
        "70019": "Too many requests via app.",
        "70020": "Too many requests via api.",
        "70021": "Too many requests.",
        "70022": "Too many requests at the same time.",
        "70023": "Too many requests are queued. Please wait and try again.",
        "70024": "Too many requests via api v3.",
        "70025": "Too many requests via api v1.",
        "70026": "Too many requests.",
    }

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
        :raises ExchangeApiError: When API error occurs
        :rtype: None
        """
        self._validate_response(response_data)

    def _validate_response(self, http_response_data: HttpResponseData) -> None:
        """Check HTTP response data and raise exception if error exists

        :param http_response_data: HTTP response data
        :type http_response_data: HttpResponseData
        :raises ExchangeApiError: When API error occurs
        :rtype: None
        """
        http_status_code = http_response_data.http_status_code
        response_body_text = http_response_data.response_body_text

        success, api_error_code, api_error_message = self._extract_error_info(
            response_body_text
        )

        # Inline error detection
        is_http_error = not HttpStatusCode.is_success(http_status_code)
        is_api_error = success != self._SUCCESS_VALUE

        if is_http_error or is_api_error:
            error_description = self._ERROR_MESSAGE_TEMPLATE.format(
                exchange_name=self._EXCHANGE.display_name,
                http_status_code=http_status_code,
                api_error_code=api_error_code or "unknown",
                api_error_message=api_error_message or "Unknown error",
            )

            raise ExchangeApiError(
                error_description=error_description,
                http_status_code=http_status_code,
                api_status_code_1=str(api_error_code)
                if api_error_code is not None
                else None,
                api_error_message_1=api_error_message,
                response_body=response_body_text,
            )

    def _extract_error_info(
        self, response_body_text: str
    ) -> tuple[int | None, Any, str | None]:
        """Extract error information from bitbank :term:`http response data` text

        :param response_body_text: Response body text
        :type response_body_text: str
        :return: Tuple of (success value, API error code, API error message)
        :rtype: tuple[int | None, Any, str | None]
        """
        success: int | None = None
        api_error_code: Any = None
        api_error_message: str | None = None

        try:
            json_data: Any = json.loads(response_body_text)

            success_value = json_data.get("success")
            success = (
                success_value if isinstance(success_value, int) else self._ERROR_VALUE
            )

            if success == self._ERROR_VALUE:
                try:
                    data_section = json_data["data"]
                    api_error_code = data_section["code"]
                except (KeyError, TypeError):
                    api_error_code = None

                if api_error_code is not None:
                    code_str = str(api_error_code)
                    api_error_message = self._ERROR_MESSAGES.get(
                        code_str, f"Unknown error (code: {code_str})"
                    )
                else:
                    api_error_message = "Unknown error"

        except Exception:
            pass

        return success, api_error_code, api_error_message
