#!/usr/bin/env python3
"""Sample script to fetch and display bitbank exchange status

.. code-block:: console

    # Check status for all currency pairs
    uv run python examples/bitbank/spot_status.py
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from common.helpers import setup_logging
from rich import print
from rich.table import Table

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitbank import SpotStatus, SpotStatusRequest

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

    async with create_session(Exchange.BITBANK) as session:
        spot_status = await session.api.spot_status(SpotStatusRequest())
        display_spot_status(spot_status)


def display_spot_status(spot_status: SpotStatus) -> None:
    statuses = spot_status.statuses

    table = Table(title="bitbank Exchange Status")
    table.add_column("Currency Pair", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Min Order Amount", style="green", justify="right")

    for pair_status in statuses:
        status_emoji = get_status_emoji(pair_status.status.value)
        status_display = f"{status_emoji} {pair_status.status.value}"

        table.add_row(
            pair_status.pair,
            status_display,
            str(pair_status.min_amount),
        )

    print(table)

    normal_count = sum(1 for s in statuses if s.status.value == "NORMAL")
    busy_count = sum(1 for s in statuses if s.status.value == "BUSY")
    very_busy_count = sum(1 for s in statuses if s.status.value == "VERY_BUSY")
    halt_count = sum(1 for s in statuses if s.status.value == "HALT")

    print("\n[bold]Summary:[/bold]")
    print(f"  🟢 NORMAL: {normal_count}")
    print(f"  🟡 BUSY: {busy_count}")
    print(f"  🟠 VERY_BUSY: {very_busy_count}")
    print(f"  🔴 HALT: {halt_count}")


def get_status_emoji(status: str) -> str:
    emoji_map = {
        "NORMAL": "🟢",
        "BUSY": "🟡",
        "VERY_BUSY": "🟠",
        "HALT": "🔴",
    }
    return emoji_map.get(status, "⚪")


if __name__ == "__main__":
    app()
