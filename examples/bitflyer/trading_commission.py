#!/usr/bin/env python3
"""Sample script to fetch trading commission rate from bitFlyer

Fetches the trading commission rate for a specified currency pair.
Displays the commission rate according to the account's trading level.

.. code-block:: console

    # Fetch commission rate for BTC_JPY pair
    uv run python examples/bitflyer/trading_commission.py --pair BTC_JPY

    # Fetch commission rate for ETH_JPY pair
    uv run python examples/bitflyer/trading_commission.py --pair ETH_JPY
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from common.helpers import setup_logging

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer import (
    TradingCommissionRequest,
)

# Unified settings for development environment
app = typer.Typer(
    pretty_exceptions_enable=True,  # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False,  # Show full traceback
)


@app.command()
def main(
    pair: Annotated[
        str,
        typer.Option(
            "--pair",
            help="Currency pair (e.g., BTC_JPY, ETH_JPY)",
        ),
    ],
    log_level: Annotated[
        str,
        typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    ] = "WARNING",
) -> None:
    asyncio.run(async_main(pair, log_level))


async def async_main(pair: str, log_level: str) -> None:
    setup_logging(log_level)

    api_key = os.getenv("BITFLYER_API_KEY")
    api_secret = os.getenv("BITFLYER_API_SECRET")

    if not api_key or not api_secret:
        typer.echo("Error: API credentials not found in environment variables")
        typer.echo("Please set BITFLYER_API_KEY and BITFLYER_API_SECRET")
        raise typer.Exit(1)

    request = TradingCommissionRequest(product_code=pair)

    # At this point, api_key and api_secret are guaranteed to be non-None
    async with create_session(
        Exchange.BITFLYER,
        api_key=api_key,  # type: ignore[arg-type]
        api_secret=api_secret,  # type: ignore[arg-type]
    ) as session:
        commission = await session.api.gettradingcommission(request)

        typer.echo(f"Product Code: {pair}")
        typer.echo(f"Commission Rate: {commission.commission_rate}")
        typer.echo(f"Commission %: {commission.commission_rate * 100:.3f}%")


if __name__ == "__main__":
    app()  # Typer automatically catches exceptions and displays them nicely
