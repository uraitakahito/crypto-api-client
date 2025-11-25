#!/usr/bin/env python3
"""Async version of bitbank asset information fetch sample

Fetches and displays account asset information (balance) from bitbank exchange.
Shows total amount and available amount.

.. code-block:: console

    uv run python examples/bitbank/assets.py

.. note::

    An API key is required to run this command.
    Set BITBANK_API_KEY and BITBANK_API_SECRET as environment variables.
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))


import typer
from common.helpers import get_key_and_secret, setup_logging
from rich.console import Console
from rich.table import Table

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitbank.exchange_api_client import (
    ExchangeApiClient as BitbankApiClient,
)
from crypto_api_client.core.exchange_session import ExchangeSession

app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=False,
)
console = Console()


@app.command()
def main(
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level", "-l", help="Log level (DEBUG, INFO, WARNING, ERROR)"
        ),
    ] = "WARNING",
) -> None:
    asyncio.run(async_main(log_level))


async def async_main(log_level: str) -> None:
    setup_logging(log_level)

    api_key, api_secret = get_key_and_secret("bitbank")

    async with create_session(
        Exchange.BITBANK,
        api_key=api_key,
        api_secret=api_secret,
    ) as session:
        await fetch_and_display_assets(session)


async def fetch_and_display_assets(
    session: ExchangeSession[BitbankApiClient],
) -> None:
    assets = await session.api.assets()

    if not assets or not any(a.onhand_amount > 0 or a.free_amount > 0 for a in assets):
        console.print("[yellow]No holdings[/yellow]")
        return

    table = Table(
        title=f"{Exchange.BITBANK.display_name} Balance Information", show_header=True, header_style="bold cyan"
    )
    table.add_column("Currency", style="cyan", width=8)
    table.add_column("Total Amount", justify="right", style="green")
    table.add_column("Available", justify="right", style="yellow")

    for asset in assets:
        if asset.onhand_amount > 0 or asset.free_amount > 0:
            table.add_row(
                asset.asset.upper(),
                f"{asset.onhand_amount:,.8f}".rstrip("0").rstrip("."),
                f"{asset.free_amount:,.8f}".rstrip("0").rstrip("."),
            )

    console.print(table)


if __name__ == "__main__":
    app()
