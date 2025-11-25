"""Factory for creating test HTTP responses."""

import json
from datetime import timedelta
from typing import Any, Dict

from crypto_api_client.http.http_response_data import HttpResponseData


class ResponseFactory:
    """Factory class for creating test HTTP responses.

    Provides simple response generation using static methods without inheritance.
    """

    @staticmethod
    def create_response(
        http_status_code: int,
        response_body_text: str,
        headers: Dict[str, str] | None = None,
        url: str = "https://api.example.com/test",
        elapsed: timedelta | None = None,
        encoding: str = "utf-8",
    ) -> HttpResponseData:
        """Create a basic HTTP response.

        Args:
            http_status_code: HTTP status code
            response_body_text: Response body text
            headers: Response headers
            url: Response URL
            elapsed: Request processing time
            encoding: Character encoding

        Returns:
            HttpResponseData instance
        """
        return HttpResponseData(
            http_status_code=http_status_code,
            headers=headers or {},
            response_body_text=response_body_text,
            url=url,
            response_body_bytes=response_body_text.encode(encoding)
            if response_body_text
            else b"",
            elapsed=elapsed,
            encoding=encoding,
        )

    @staticmethod
    def success(
        body: Any = None, status_code: int = 200, headers: Dict[str, str] | None = None
    ) -> HttpResponseData:
        """Create a success response.

        Args:
            body: Response body (converted to JSON if dict)
            status_code: HTTP status code (default: 200)
            headers: Response headers

        Returns:
            Success response
        """
        if body is None:
            body = {"status": "success"}

        text = json.dumps(body) if isinstance(body, (dict, list)) else str(body)

        return ResponseFactory.create_response(
            http_status_code=status_code,
            response_body_text=text,
            headers=headers or {"Content-Type": "application/json"},
        )

    @staticmethod
    def error(
        status_code: int = 400,
        message: str = "Error occurred",
        error_code: str | None = None,
        headers: Dict[str, str] | None = None,
    ) -> HttpResponseData:
        """Create an error response.

        Args:
            status_code: HTTP error status code
            message: Error message
            error_code: Error code (optional)
            headers: Response headers

        Returns:
            Error response
        """
        error_body = {"error": message}
        if error_code:
            error_body["code"] = error_code

        return ResponseFactory.create_response(
            http_status_code=status_code,
            response_body_text=json.dumps(error_body),
            headers=headers or {"Content-Type": "application/json"},
        )

    @staticmethod
    def rate_limit_error(
        retry_after: int = 60, message: str = "Rate limit exceeded"
    ) -> HttpResponseData:
        """Create a rate limit error response.

        Args:
            retry_after: Seconds until retry allowed
            message: Error message

        Returns:
            429 Rate Limit error response
        """
        return ResponseFactory.error(
            status_code=429,
            message=message,
            headers={
                "Content-Type": "application/json",
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
            },
        )

    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> HttpResponseData:
        """Create a 401 Unauthorized response.

        Args:
            message: Error message

        Returns:
            401 Unauthorized response
        """
        return ResponseFactory.error(
            status_code=401, message=message, headers={"WWW-Authenticate": "Bearer"}
        )

    @staticmethod
    def not_found(message: str = "Not found") -> HttpResponseData:
        """Create a 404 Not Found response.

        Args:
            message: Error message

        Returns:
            404 Not Found response
        """
        return ResponseFactory.error(status_code=404, message=message)

    @staticmethod
    def server_error(message: str = "Internal server error") -> HttpResponseData:
        """Create a 500 Internal Server Error response.

        Args:
            message: Error message

        Returns:
            500 Internal Server Error response
        """
        return ResponseFactory.error(status_code=500, message=message)

    @staticmethod
    def timeout_error(message: str = "Gateway timeout") -> HttpResponseData:
        """Create a 504 Gateway Timeout response.

        Args:
            message: Error message

        Returns:
            504 Gateway Timeout response
        """
        return ResponseFactory.error(status_code=504, message=message)

    # Exchange-specific response creators

    @staticmethod
    def bitflyer_ticker_response(
        product_code: str = "BTC_JPY",
        ltp: float = 12000000.0,
        best_bid: float = 11999000.0,
        best_ask: float = 12001000.0,
        volume: float = 1234.5678,
        timestamp: str = "2024-01-01T12:00:00.000Z",
    ) -> HttpResponseData:
        """Create a bitFlyer-format ticker response.

        Args:
            product_code: Product code
            ltp: Last traded price
            best_bid: Best bid price
            best_ask: Best ask price
            volume: Trading volume
            timestamp: Timestamp

        Returns:
            bitFlyer ticker response
        """
        ticker_data = {
            "product_code": product_code,
            "state": "RUNNING",
            "timestamp": timestamp,
            "tick_id": 12345,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "best_bid_size": 0.1,
            "best_ask_size": 0.1,
            "total_bid_depth": 100.0,
            "total_ask_depth": 100.0,
            "market_bid_size": 0.0,
            "market_ask_size": 0.0,
            "ltp": ltp,
            "volume": volume,
            "volume_by_product": volume / 2,
        }

        return ResponseFactory.success(ticker_data)

    @staticmethod
    def bitflyer_error_response(
        http_status: int = 400,
        api_status: int = -100,
        message: str = "Invalid parameter",
    ) -> HttpResponseData:
        """Create a bitFlyer-format error response.

        Args:
            http_status: HTTP status code
            api_status: bitFlyer API status code
            message: Error message

        Returns:
            bitFlyer error response
        """
        error_body = {"status": api_status, "error_message": message, "data": None}

        return ResponseFactory.create_response(
            http_status_code=http_status,
            response_body_text=json.dumps(error_body),
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def bitbank_ticker_response(
        pair: str = "btc_jpy",
        last: str = "12000000",
        bid: str = "11999000",
        ask: str = "12001000",
        volume: str = "1234.5678",
    ) -> HttpResponseData:
        """Create a bitbank-format ticker response.

        Args:
            pair: Currency pair
            last: Last traded price
            bid: Bid price
            ask: Ask price
            volume: Trading volume

        Returns:
            bitbank ticker response
        """
        response_data = {
            "success": 1,
            "data": {
                "sell": ask,
                "buy": bid,
                "high": "12100000",
                "low": "11900000",
                "open": "12000000",
                "last": last,
                "vol": volume,
                "timestamp": 1704110400000,
            },
        }

        return ResponseFactory.success(response_data)
