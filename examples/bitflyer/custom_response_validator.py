#!/usr/bin/env python3
"""Custom response validator implementation example

This sample demonstrates how to implement custom response validation processing
by inheriting from :class:`~crypto_api_client.callbacks.AbstractRequestCallback`.

Provides two custom implementation examples:

1. **Logging Response Validator**: Records statistical information when errors occur
2. **Business Logic Response Validator**: Converts API errors to application-specific exceptions

.. code-block:: console

    uv run python examples/bitflyer/custom_response_validator.py --test logging
    uv run python examples/bitflyer/custom_response_validator.py --test business

.. warning::

    ``--test business`` may actually place orders, so be careful.

.. note::

    If you want to use the default response validator,
    see ``examples/bitflyer/default_response_validator.py``.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from common.helpers import get_key_and_secret, setup_logging
from pydantic import SecretStr
from rich.console import Console
from yarl import URL

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer import (
    SendChildOrderRequest,
)
from crypto_api_client.bitflyer.native_domain_models import (
    ChildOrderType,
    Side,
)
from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.errors.exceptions import ExchangeApiError
from crypto_api_client.http._http_status_code import HttpStatusCode
from crypto_api_client.http.http_response_data import HttpResponseData
from crypto_api_client.security.secret_headers import SecretHeaders

app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=False,
)
console = Console()
logger = logging.getLogger(__name__)


class BusinessLogicError(Exception):
    """Business logic error (insufficient balance, etc.)"""

    pass


class LoggingResponseValidator(AbstractRequestCallback):
    """Response Validator that logs responses before validation

    Example of a custom response validation handler.
    Logs errors when they occur and maintains statistical information.

    .. seealso::
        :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
    """

    def __init__(self):
        self.error_count = 0
        self.last_error_time: datetime | None = None

    async def before_request(
        self,
        url: URL,
        headers: SecretHeaders,
        data: str | None,
    ) -> None:
        """Pre-request processing (does nothing)"""
        pass

    async def after_request(self, response_data: HttpResponseData) -> None:
        """Post-response validation processing"""
        self._validate_response(response_data)

    def _validate_response(self, http_response_data: HttpResponseData) -> None:
        """Log response and then validate"""
        http_status_code = http_response_data.http_status_code

        if HttpStatusCode.is_success(http_status_code):
            return

        self.error_count += 1
        self.last_error_time = datetime.now()

        logger.error(
            "API Error detected",
            extra={
                "http_status": http_status_code,
                "response_body": http_response_data.response_body_text[
                    :500
                ],  # First 500 characters
                "error_count": self.error_count,
                "timestamp": self.last_error_time.isoformat(),
            },
        )

        api_status, api_message = self._extract_error_info(
            http_response_data.response_body_text
        )
        raise ExchangeApiError(
            error_description=f"bitFlyer API error (HTTP {http_status_code}, status {api_status}): {api_message}",
            http_status_code=http_status_code,
            api_status_code_1=str(api_status) if api_status else None,
            api_error_message_1=api_message,
            response_body=http_response_data.response_body_text,
        )

    def _extract_error_info(self, response_body: str) -> tuple[int | None, str | None]:
        """Extract error information from response body"""
        try:
            data = json.loads(response_body)
            return data.get("status"), data.get("error_message")
        except Exception:
            return None, None


# Error conversion type Response Validator
class BusinessLogicResponseValidator(AbstractRequestCallback):
    """Response Validator that converts business logic errors to custom exceptions

    Inherits from AbstractRequestCallback, parses exchange error codes and
    converts them to application-specific exception classes.

    .. seealso::
        :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
    """

    # Business logic error mapping
    BUSINESS_ERROR_CODES = {
        -106: BusinessLogicError("( ゜д゜)What!? That order is impossible!"),
    }

    async def before_request(
        self,
        url: URL,
        headers: SecretHeaders,
        data: str | None,
    ) -> None:
        """Pre-request processing (does nothing)"""
        pass

    async def after_request(self, response_data: HttpResponseData) -> None:
        """Post-response validation processing"""
        self._validate_response(response_data)

    def _validate_response(self, http_response_data: HttpResponseData) -> None:
        """Convert business logic errors to custom exceptions"""
        http_status_code = http_response_data.http_status_code

        if HttpStatusCode.is_success(http_status_code):
            return

        # Extract API status code
        api_status = self._extract_api_status(http_response_data.response_body_text)

        # Check for business errors
        if api_status in self.BUSINESS_ERROR_CODES:
            raise self.BUSINESS_ERROR_CODES[api_status]

        # Other errors
        raise ExchangeApiError(
            error_description=f"Unknown error: HTTP {http_status_code}, API {api_status}",
            http_status_code=http_status_code,
            api_status_code_1=str(api_status) if api_status else None,
            response_body=http_response_data.response_body_text,
        )

    def _extract_api_status(self, response_body: str) -> int | None:
        """Extract API status code from response body"""
        try:
            data = json.loads(response_body)
            return data.get("status")
        except Exception:
            return None


@app.command()
def main(
    test_type: Annotated[
        str,
        typer.Option(
            "--test",
            help="Test type to run (logging, business)",
            case_sensitive=False,
        ),
    ] = "logging",
    log_level: Annotated[
        str,
        typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    ] = "INFO",
    use_private_api: Annotated[
        bool,
        typer.Option("--private", help="Test using Private API (API key required)"),
    ] = False,
) -> None:
    asyncio.run(async_main(test_type.lower(), log_level, use_private_api))


async def async_main(test_type: str, log_level: str, use_private_api: bool) -> None:
    setup_logging(log_level)

    console.print("[bold magenta]Custom Response Validator Implementation Example[/bold magenta]")
    console.print("=" * 60)

    test_mapping = {
        "logging": [test_logging],
        "business": [test_business_logic],
    }

    tests = test_mapping.get(test_type, [])

    for test_func in tests:
        await test_func()  # type: ignore


async def test_logging() -> None:
    console.print(
        "\n[bold cyan]Using Logging Response Validator with create_session[/bold cyan]"
    )

    # Configure custom Response Validator (pass directly as callback)
    response_validator = LoggingResponseValidator()

    console.print(
        "\n   [yellow]Test 1: Generate (expected) API error with invalid authentication[/yellow]"
    )
    try:
        async with create_session(
            Exchange.BITFLYER,
            api_key=SecretStr("invalid_key"),
            api_secret=SecretStr("invalid_secret"),
            callbacks=(response_validator,),
        ) as session:
            # Call Private API to trigger authentication error
            await session.api.getbalance()
    except ExchangeApiError:
        pass


async def test_business_logic() -> None:
    """Use Business Logic Response Validator with create_session"""
    console.print(
        "\n[bold cyan]Using Business Logic Response Validator with create_session[/bold cyan]"
    )
    console.print("   Convert exchange responses to application-specific exceptions")

    response_validator = BusinessLogicResponseValidator()

    api_key, api_secret = get_key_and_secret("bitflyer")

    try:
        async with create_session(
            Exchange.BITFLYER,
            api_key=api_key,
            api_secret=api_secret,
            callbacks=(response_validator,),
        ) as session:
            # Intentionally send a large order at a low price to trigger an error
            console.print("   📝 Simulating error with large order...")
            # Specify product code
            product_code = "BTC_JPY"

            await session.api.sendchildorder(
                SendChildOrderRequest(
                    product_code=product_code,
                    child_order_type=ChildOrderType.LIMIT,
                    side=Side.BUY,
                    price=Decimal("1000"),  # Low price
                    size=Decimal("100.0"),  # Large quantity
                    minute_to_expire=60,  # Add expiration time
                )
            )
    except BusinessLogicError as e:
        console.print(f"   💰 Business error: {e}")
        console.print("   → Execute appropriate handling at application layer")
    except Exception as e:
        console.print(f"   ❌ Other error: {type(e).__name__}")


if __name__ == "__main__":
    app()  # Typer automatically catches and displays exceptions beautifully
