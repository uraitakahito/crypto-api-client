from __future__ import annotations


class CryptoApiClientError(Exception):
    """Base class for all exceptions raised by the Crypto API Client."""

    def __init__(self, error_description: str) -> None:
        """
        Initialize the CryptoApiClientError with an error description.
        """
        super().__init__(error_description)
        self.error_description = error_description


class ExchangeApiError(CryptoApiClientError):
    """Exception raised when exchange API returns an error.

    This exception is raised when the :term:`API endpoint` determines there is an error,
    not when the library itself determines there is an error.
    """

    def __init__(
        self,
        error_description: str,
        *,
        http_status_code: int | None = None,
        api_status_code_1: str | None = None,
        api_status_code_2: str | None = None,
        api_error_message_1: str | None = None,
        api_error_message_2: str | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize ExchangeApiError with API endpoint error information

        :param error_description: Error message formatted by :term:`response validator` for human readability
        :type error_description: str
        :param http_status_code: HTTP status code (200, 400, 500, etc.)
        :type http_status_code: int | None
        :param api_status_code_1: Exchange-specific status code returned by API endpoint
        :type api_status_code_1: str | None
        :param api_status_code_2: Secondary exchange-specific status code returned by API endpoint
        :type api_status_code_2: str | None
        :param api_error_message_1: Error message returned by API endpoint
        :type api_error_message_1: str | None
        :param api_error_message_2: Secondary error message returned by API endpoint
        :type api_error_message_2: str | None
        :param response_body: Raw response body returned by API endpoint
        :type response_body: str | None

        .. note::
            ``http_status_code`` is of int type to support both standard HTTP status codes
            (200, 404, etc.) and non-standard codes (CloudFlare 520-527, nginx 499, etc.).
            See HttpStatusCode class for details.
        """
        super().__init__(error_description)
        self.http_status_code = http_status_code
        self.api_status_code_1 = api_status_code_1
        self.api_status_code_2 = api_status_code_2
        self.api_error_message_1 = api_error_message_1
        self.api_error_message_2 = api_error_message_2
        self.response_body = response_body


class RetryLimitExceededError(CryptoApiClientError):
    """Error raised when maximum retry count configured in retry_strategy is exceeded."""


class RateLimitApproachingError(CryptoApiClientError):
    """Warning indicating that rate limit violation is approaching.

    Used as a warning before the exchange determines a rate limit violation.
    """
