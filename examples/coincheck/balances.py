#!/usr/bin/env python3
"""Sample script to fetch Coincheck account balances

.. code-block:: console

    uv run python examples/coincheck/balances.py

.. note::

    An API key is required to run this command.
    Set COINCHECK_API_KEY and COINCHECK_API_SECRET as environment variables.
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
from crypto_api_client.coincheck.exchange_api_client import (
    ExchangeApiClient as CoincheckApiClient,
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
        typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    ] = "WARNING",
) -> None:
    asyncio.run(async_main(log_level))


async def async_main(log_level: str) -> None:
    setup_logging(log_level)

    api_key, api_secret = get_key_and_secret("coincheck")

    async with create_session(
        Exchange.COINCHECK, api_key=api_key, api_secret=api_secret
    ) as session:
        await fetch_and_display_balances(session)


async def fetch_and_display_balances(
    session: ExchangeSession[CoincheckApiClient],
) -> None:
    balances = await session.api.balance()

    if not balances:
        console.print("[yellow]No holdings[/yellow]")
        return

    table = Table(
        title=f"{Exchange.COINCHECK.display_name} Balance Information", show_header=True, header_style="bold cyan"
    )
    table.add_column("Currency", style="cyan", width=8)
    table.add_column("Available", justify="right", style="green")
    table.add_column("In Order", justify="right", style="yellow")
    table.add_column("Lendable", justify="right", style="blue")
    table.add_column("Lending", justify="right", style="magenta")

    for balance in balances:
        if any(
            val > 0
            for val in [
                balance.available,
                balance.reserved,
                balance.lending,
                balance.lend_in_use,
            ]
        ):
            table.add_row(
                balance.currency.upper(),
                f"{balance.available:,.8f}".rstrip("0").rstrip("."),
                f"{balance.reserved:,.8f}".rstrip("0").rstrip("."),
                f"{balance.lending:,.8f}".rstrip("0").rstrip("."),
                f"{balance.lend_in_use:,.8f}".rstrip("0").rstrip("."),
            )

    console.print(table)


if __name__ == "__main__":
    app()
