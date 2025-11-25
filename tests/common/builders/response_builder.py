"""HTTP response builder for test mocks."""

import json
from datetime import datetime, timedelta
from typing import Any

from crypto_api_client.http.http_response_data import HttpResponseData


class ResponseBuilder:
    """Builder for creating mock HTTP responses."""

    def success(
        self,
        http_status_code: int = 200,
        body: str = "{}",
        headers: dict[str, str] | None = None,
        encoding: str = "utf-8",
    ) -> HttpResponseData:
        """Create successful HTTP response.

        Args:
            http_status_code: HTTP success status code (200-299)
            body: Response body as string
            headers: Response headers
            encoding: Response encoding

        Returns:
            Mock HttpResponseData
        """
        if headers is None:
            headers = {"content-type": "application/json"}

        return self._create_response(
            http_status_code=http_status_code,
            body=body,
            headers=headers,
            encoding=encoding,
        )

    def error(
        self,
        http_status_code: int,
        message: str,
        headers: dict[str, str] | None = None,
        error_code: str | None = None,
    ) -> HttpResponseData:
        """Create error HTTP response.

        Args:
            http_status_code: HTTP error status code
            message: Error message
            headers: Response headers
            error_code: Optional error code

        Returns:
            Mock HttpResponseData
        """
        if headers is None:
            headers = {"content-type": "application/json"}

        # Create error body based on common patterns
        if 400 <= http_status_code < 500:
            body = self._create_client_error_body(message, error_code)
        else:
            body = self._create_server_error_body(message, error_code)

        return self._create_response(
            http_status_code=http_status_code, body=body, headers=headers
        )

    def rate_limit_error(
        self, retry_after: int = 60, message: str = "Rate limit exceeded"
    ) -> HttpResponseData:
        """Create rate limit error response.

        Args:
            retry_after: Seconds to wait before retry
            message: Error message

        Returns:
            Mock HttpResponseData with 429 status
        """
        headers = {
            "content-type": "application/json",
            "retry-after": str(retry_after),
            "x-ratelimit-limit": "500",
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": str(
                int((datetime.now() + timedelta(seconds=retry_after)).timestamp())
            ),
        }

        return self.error(
            http_status_code=429,
            message=message,
            headers=headers,
            error_code="RATE_LIMIT_EXCEEDED",
        )

    def timeout_error(self) -> HttpResponseData:
        """Create timeout error response.

        Returns:
            Mock HttpResponseData with 408 status
        """
        return self.error(
            http_status_code=408,
            message="Request timeout",
            error_code="REQUEST_TIMEOUT",
        )

    def not_found_error(self, resource: str = "resource") -> HttpResponseData:
        """Create not found error response.

        Args:
            resource: Name of resource not found

        Returns:
            Mock HttpResponseData with 404 status
        """
        return self.error(
            http_status_code=404,
            message=f"{resource} not found",
            error_code="NOT_FOUND",
        )

    def unauthorized_error(self, message: str = "Unauthorized") -> HttpResponseData:
        """Create unauthorized error response.

        Args:
            message: Error message

        Returns:
            Mock HttpResponseData with 401 status
        """
        headers = {"content-type": "application/json", "www-authenticate": "Bearer"}

        return self.error(
            http_status_code=401,
            message=message,
            headers=headers,
            error_code="UNAUTHORIZED",
        )

    def _create_response(
        self,
        http_status_code: int,
        body: str,
        headers: dict[str, str],
        encoding: str = "utf-8",
    ) -> HttpResponseData:
        """Create HttpResponseData instance.

        Args:
            http_status_code: HTTP status code
            body: Response body
            headers: Response headers
            encoding: Response encoding

        Returns:
            HttpResponseData instance
        """
        # Status code is now always int

        # Create response data
        return HttpResponseData(
            http_status_code=http_status_code,
            headers=headers,
            response_body_text=body,
            response_body_bytes=body.encode(encoding),
            url="https://api.example.com/test",
            reason=self._get_reason_phrase(http_status_code),
            elapsed=timedelta(milliseconds=100),
            cookies={},
            encoding=encoding,
            request_method="GET",
            request_url="https://api.example.com/test",
            request_path="/test",
        )

    def _create_client_error_body(self, message: str, error_code: str | None) -> str:
        """Create client error response body.

        Args:
            message: Error message
            error_code: Optional error code

        Returns:
            JSON error body
        """
        error_data: dict[str, Any] = {"error": {"message": message}}

        if error_code:
            error_data["error"]["code"] = error_code

        return json.dumps(error_data)

    def _create_server_error_body(self, message: str, error_code: str | None) -> str:
        """Create server error response body.

        Args:
            message: Error message
            error_code: Optional error code

        Returns:
            JSON error body
        """
        error_data: dict[str, Any] = {
            "error": {"message": message, "type": "server_error"}
        }

        if error_code:
            error_data["error"]["code"] = error_code

        return json.dumps(error_data)

    def _get_reason_phrase(self, status_code: int) -> str:
        """Get reason phrase for status code.

        Args:
            status_code: HTTP status code

        Returns:
            Reason phrase
        """
        # Simple mapping for common status codes
        reason_phrases = {
            200: "OK",
            201: "Created",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
        }
        return reason_phrases.get(status_code, f"HTTP {status_code}")

    def server_error(self, message: str = "Internal Server Error") -> HttpResponseData:
        """Create a server error response.

        Args:
            message: Error message

        Returns:
            HttpResponseData for server error
        """
        return self.error(
            http_status_code=500, message=message, error_code="INTERNAL_SERVER_ERROR"
        )
