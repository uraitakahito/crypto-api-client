#!/usr/bin/env python
"""Example of customizing request settings using SessionConfig

Demonstrates how to customize settings such as timeout, retry,
and HTTP/2 using SessionConfig.

.. code-block:: console

    uv run python examples/session_config_demo.py
    uv run python examples/session_config_demo.py --log-level DEBUG
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent))

import typer
from common.helpers import setup_logging

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer.native_requests import TickerRequest
from crypto_api_client.core.session_config import SessionConfig

app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=False,
)


@app.command()
def main(
    log_level: Annotated[
        str,
        typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    ] = "WARNING",
) -> None:
    asyncio.run(async_main(log_level))


async def async_main(log_level: str) -> None:
    setup_logging(log_level)

    product_code = "BTC_JPY"

    typer.echo("=== SessionConfig Custom Configuration Demo ===\n")

    typer.echo("Fast response-oriented configuration:")
    fast_config = SessionConfig(
        request_timeout_seconds=3,
        request_max_retries=1,
        request_initial_delay_seconds=0.5,
        request_backoff_factor=1.5,
        request_jitter=False,
    )

    async with create_session(Exchange.BITFLYER, session_config=fast_config) as session:
        typer.echo(f"  Timeout: {fast_config.request_timeout_seconds} seconds")
        typer.echo(f"  Max retries: {fast_config.request_max_retries}")

        request = TickerRequest(product_code=product_code)
        ticker = await session.api.ticker(request)
        typer.echo(f"  BTC price: {ticker.ltp:,.0f} JPY\n")


if __name__ == "__main__":
    app()
