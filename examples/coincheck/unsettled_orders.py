#!/usr/bin/env python3
"""Sample script to fetch Coincheck unsettled order list

Fetches the list of unsettled orders for a specified trading pair.

.. code-block:: console

    uv run python examples/coincheck/unsettled_orders.py --zone Asia/Tokyo

.. note::

    An API key is required to run this command.
    Set COINCHECK_API_KEY and COINCHECK_API_SECRET as environment variables.
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from common.helpers import get_key_and_secret, setup_logging
from common.typer_custom_types import ZONE_INFO_TYPE
from rich.console import Console
from rich.table import Table

from crypto_api_client import Exchange, create_session
from crypto_api_client.coincheck import Order, OrderType

app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=False,
)
console = Console()


@app.command()
def main(
    zone_info: Annotated[
        ZoneInfo,
        typer.Option(
            "--zone", help="Timezone name like Asia/Tokyo", click_type=ZONE_INFO_TYPE
        ),
    ] = ZoneInfo("UTC"),
    log_level: Annotated[
        str,
        typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    ] = "WARNING",
) -> None:
    asyncio.run(async_main(zone_info, log_level))


async def async_main(zone_info: ZoneInfo, log_level: str) -> None:
    setup_logging(log_level)

    api_key, api_secret = get_key_and_secret("COINCHECK")

    async with create_session(
        Exchange.COINCHECK, api_key=api_key, api_secret=api_secret
    ) as session:
        console.print("[bold blue]Fetching unsettled orders...[/bold blue]")

        orders = await session.api.unsettled_orders()

        display_orders(orders, zone_info)


def display_orders(orders: list[Order], tz: ZoneInfo) -> None:
    if not orders:
        console.print("[yellow]No unsettled orders[/yellow]")
        return

    console.print(
        f"\n[bold green]✓[/bold green] Found {len(orders)} unsettled orders\n"
    )

    table = Table(
        title="Coincheck Unsettled Order List", show_header=True, header_style="bold cyan"
    )
    table.add_column("ID", style="dim", width=10)
    table.add_column("Pair", style="cyan", width=10)
    table.add_column("Type", width=6)
    table.add_column("Rate", justify="right", width=12)
    table.add_column("Pending", justify="right", width=12)
    table.add_column("Created At", width=20)

    for order in orders:
        order_with_tz = order.with_timezone(tz)
        type_color = "green" if order.order_type == OrderType.BUY else "red"
        rate_str = f"{order.rate:,.0f}" if order.rate else "MARKET"

        table.add_row(
            str(order.id),
            order.pair.upper(),
            f"[{type_color}]{order.order_type.value.upper()}[/{type_color}]",
            rate_str,
            f"{order.pending_amount:,.8f}".rstrip("0").rstrip("."),
            order_with_tz.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    console.print(table)

    buy_count = sum(1 for o in orders if o.order_type == OrderType.BUY)
    sell_count = sum(1 for o in orders if o.order_type == OrderType.SELL)

    console.print("\n📊 Summary:")
    console.print(f"  [bold]Total:[/bold] {len(orders)} orders")
    console.print(
        f"  [bold]Breakdown:[/bold] [green]Buy: {buy_count}[/green] / "
        f"[red]Sell: {sell_count}[/red]"
    )


if __name__ == "__main__":
    app()
