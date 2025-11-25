"""Base factory implementation with common utilities for test data generation."""

import random
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from crypto_api_client.http.http_response_data import HttpResponseData

from .abstract_factory import ExchangeTestDataFactory


class BaseTestDataFactory(ExchangeTestDataFactory):
    """Base factory with common utility methods for all exchange factories."""

    # Common test constants
    DEFAULT_API_KEY = "test_api_key_1234567890"
    DEFAULT_API_SECRET = "test_api_secret_0987654321"
    DEFAULT_MIN_PRICE = Decimal("1000")
    DEFAULT_MAX_PRICE = Decimal("10000000")
    DEFAULT_MIN_SIZE = Decimal("0.001")
    DEFAULT_MAX_SIZE = Decimal("100")

    def create_api_credentials(self) -> dict[str, str]:
        """Create API credentials for testing."""
        return {
            "api_key": self.DEFAULT_API_KEY,
            "api_secret": self.DEFAULT_API_SECRET,
        }

    @staticmethod
    def get_timestamp() -> datetime:
        """Get current UTC timestamp."""
        return datetime.now(timezone.utc)

    @staticmethod
    def get_timestamp_str() -> str:
        """Get current UTC timestamp as ISO format string."""
        return datetime.now(timezone.utc).isoformat()

    def create_price(
        self, min_price: Decimal | None = None, max_price: Decimal | None = None
    ) -> Decimal:
        """Create a random price within specified range."""
        min_val = float(min_price or self.DEFAULT_MIN_PRICE)
        max_val = float(max_price or self.DEFAULT_MAX_PRICE)
        return Decimal(str(round(random.uniform(min_val, max_val), 2)))

    def create_size(
        self, min_size: Decimal | None = None, max_size: Decimal | None = None
    ) -> Decimal:
        """Create a random size within specified range."""
        min_val = float(min_size or self.DEFAULT_MIN_SIZE)
        max_val = float(max_size or self.DEFAULT_MAX_SIZE)
        return Decimal(str(round(random.uniform(min_val, max_val), 8)))

    @staticmethod
    def create_http_response(
        status_code: int,
        body: str,
        headers: dict[str, str] | None = None,
        url: str | None = None,
    ) -> HttpResponseData:
        """Create a HttpResponseData object."""
        return HttpResponseData(
            http_status_code=status_code,
            headers=headers or {"content-type": "application/json"},
            response_body_text=body,
            response_body_bytes=body.encode("utf-8"),
            url=url or "https://api.test.com/endpoint",
        )

    def create_success_response(
        self, data: dict[str, Any] | list[Any]
    ) -> HttpResponseData:
        """Create a successful HTTP response."""
        import json

        return self.create_http_response(
            status_code=200,
            body=json.dumps(data),
        )

    def create_error_response(
        self, status_code: int, **kwargs: Any
    ) -> HttpResponseData:
        """Create an error response with specified status code."""
        error_messages = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            429: "Too Many Requests",
            500: "Internal Server Error",
            503: "Service Unavailable",
        }

        error_data = {
            "status": status_code,
            "error": error_messages.get(status_code, "Unknown Error"),
            "message": kwargs.get("message", f"Error {status_code}"),
        }

        if "error_code" in kwargs:
            error_data["error_code"] = kwargs["error_code"]

        import json

        return self.create_http_response(
            status_code=status_code,
            body=json.dumps(error_data),
        )

    @staticmethod
    def create_random_id(prefix: str = "") -> str:
        """Create a random ID with optional prefix."""
        random_part = "".join(
            random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=10)
        )
        return f"{prefix}{random_part}" if prefix else random_part

    @staticmethod
    def create_random_hash() -> str:
        """Create a random hash-like string."""
        return "".join(random.choices("abcdef0123456789", k=64))

    def create_headers(self, **kwargs: str) -> dict[str, str]:
        """Create HTTP headers for requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "crypto-api-client-test",
        }
        headers.update(kwargs)
        return headers
