#!/usr/bin/env python3
"""Callback system implementation sample

Sample implementation of hook processing before and after requests.
Cross-cutting concerns such as logging, monitoring, and rate limiting
can be easily added.

.. code-block:: console

    uv run python examples/bitflyer/callbacks.py --pair BTC_JPY
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

import typer
from yarl import URL

sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer import TickerRequest
from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.factories import create_response_validator
from crypto_api_client.http.http_response_data import HttpResponseData
from crypto_api_client.security.secret_headers import SecretHeaders

# Unified settings for development environment
app = typer.Typer(
    pretty_exceptions_enable=True,  # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False,  # Show full traceback
)


@app.command()
def main(
    product_code: Annotated[
        str,
        typer.Option(
            "--product-code",
            help="Currency pair (e.g., BTC_JPY, ETH_JPY)",
        ),
    ],
) -> None:
    asyncio.run(async_main(product_code))


async def async_main(product_code: str) -> None:
    # Create custom callbacks
    response_validator = create_response_validator(Exchange.BITFLYER)
    timing_callback = MyAsyncCallback("Timer")
    rate_monitor = RateLimitMonitor()

    async with create_session(
        Exchange.BITFLYER, callbacks=(response_validator, timing_callback, rate_monitor)
    ) as session:
        typer.echo(f"📊 Fetching currency pair {product_code}\n")

        request = TickerRequest(product_code=product_code)
        ticker = await session.api.ticker(request)

        typer.echo("\n📈 Result:")
        typer.echo(
            f"  {str(ticker.product_code)}: "
            f"Last price={ticker.ltp:,.0f} JPY, "
            f"Volume={ticker.volume:,.2f}"
        )


class MyAsyncCallback(AbstractRequestCallback):
    """Custom async callback implementation example."""

    def __init__(self, name: str):
        self.name = name
        self.request_count = 0
        self.total_response_time = 0.0

    async def before_request(
        self,
        url: URL,
        headers: SecretHeaders,
        data: str | None,
    ) -> None:
        """Async processing before request is sent."""
        self.request_count += 1
        typer.echo(
            f"🔵 [{self.name}] Request #{self.request_count} starting: {url.host}{url.path}",
            color=True,
        )
        await asyncio.sleep(0.001)  # Simulate async processing

    async def after_request(self, response_data: HttpResponseData) -> None:
        """Async processing after response is received."""
        if response_data.elapsed:
            elapsed_ms = response_data.elapsed.total_seconds() * 1000
            self.total_response_time += elapsed_ms
            avg_time = self.total_response_time / self.request_count

            typer.echo(
                f"🟢 [{self.name}] Response received: "
                f"Status={response_data.http_status_code}, "
                f"Time={elapsed_ms:.1f}ms, "
                f"Avg={avg_time:.1f}ms",
                color=True,
            )

        # Example async processing: send analysis data (actual implementation would use async HTTP client)
        await asyncio.sleep(0.001)  # Simulate async processing


class RateLimitMonitor(AbstractRequestCallback):
    """Async callback that monitors rate limit information."""

    async def before_request(
        self,
        url: URL,
        headers: SecretHeaders,
        data: str | None,
    ) -> None:
        pass

    async def after_request(self, response_data: HttpResponseData) -> None:
        """Extract and display rate limit information from response."""
        headers = response_data.headers

        # Check bitFlyer rate limit headers
        # Important: httpx normalizes HTTP header names to lowercase,
        # so even if the original header name is "X-RateLimit-*", we need to access it as "x-ratelimit-*"
        rate_limit_period = headers.get("x-ratelimit-period")
        rate_limit_remaining = headers.get("x-ratelimit-remaining")
        rate_limit_reset = headers.get("x-ratelimit-reset")

        if rate_limit_remaining:
            typer.echo(
                f"⚡ Rate Limit: {rate_limit_remaining} requests remaining "
                f"(Period: {rate_limit_period}s, Reset: {rate_limit_reset})",
                color=True,
            )


if __name__ == "__main__":
    app()  # Typer automatically catches and displays exceptions beautifully
