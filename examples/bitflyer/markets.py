#!/usr/bin/env python3
"""Sample script to fetch list of tradable markets on bitFlyer

Fetches information about all currently tradable markets and
displays information such as currency pairs, market types, and aliases.

.. code-block:: console

    # Display basic information
    uv run python examples/bitflyer/markets.py
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

import typer

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer.native_domain_models import Market

sys.path.insert(0, str(Path(__file__).parent.parent))
import common.helpers as utils

# Unified settings for development environment
app = typer.Typer(
    pretty_exceptions_enable=True,      # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False        # Show full traceback
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
    utils.setup_logging(log_level)

    async with create_session(Exchange.BITFLYER) as session:
        markets = await session.api.markets()
        display_table(markets)


def display_table(markets: list[Market]) -> None:
    typer.echo("\n📊 bitFlyer Market List")
    typer.echo("=" * 80)

    for market in markets:
        pc = str(market.product_code)
        mt = market.market_type.value
        typer.echo(f"{pc:<15} {mt:<10}")

    typer.echo("=" * 80)


if __name__ == "__main__":
    app()  # Typer automatically catches exceptions and displays them nicely
