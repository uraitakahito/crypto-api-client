#!/usr/bin/env python3
"""Sample script to fetch your order list from bitFlyer

Fetches your order list for a specified currency pair.
Can filter orders by status: active orders, completed, canceled, etc.

.. code-block:: console

    # Fetch all orders for BTC_JPY pair
    uv run python examples/bitflyer/getchildorders.py --pair BTC_JPY

    # Fetch only active orders
    uv run python examples/bitflyer/getchildorders.py --pair BTC_JPY --state ACTIVE

    # Fetch completed orders
    uv run python examples/bitflyer/getchildorders.py --pair BTC_JPY --state COMPLETED

.. note::

    An API key is required to run this command.
    Set BITFLYER_API_KEY and BITFLYER_API_SECRET as environment variables.
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

from zoneinfo import ZoneInfo

import typer
from common.helpers import get_key_and_secret, setup_logging
from common.typer_custom_types import ZONE_INFO_TYPE
from pydantic import SecretStr
from rich.console import Console

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer import (
    ChildOrdersRequest,
    ChildOrderState,
    Side,
)
from crypto_api_client.bitflyer.native_domain_models import ChildOrder

app = typer.Typer(
    pretty_exceptions_enable=True,  # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False,  # Show full traceback
)
console = Console()


@app.command()
def main(
    pair: Annotated[
        str,
        typer.Option(
            "--pair",
            help="Currency pair (e.g., BTC_JPY, ETH_JPY)",
        ),
    ],
    order_state: Annotated[
        ChildOrderState | None,
        typer.Option(
            "--order-state",
            help="Order state (ACTIVE, COMPLETED, CANCELED, EXPIRED, REJECTED)",
            case_sensitive=False,
        ),
    ] = ChildOrderState.ACTIVE,
    total_count: Annotated[
        int,
        typer.Option(
            "--total-count",
            min=1,
            max=10000,
            help="Total number of orders to fetch",
        ),
    ] = 1000,
    batch_size: Annotated[
        int,
        typer.Option(
            "--batch-size",
            min=1,
            max=500,
            help="Number of orders per request (API limit: 500)",
        ),
    ] = 500,
    delay: Annotated[
        float,
        typer.Option(
            "--delay",
            min=0.0,
            help="Delay between requests in seconds",
        ),
    ] = 0.2,
    zone_info: Annotated[
        ZoneInfo,
        typer.Option(
            "--zone", help="Timezone name like Asia/Tokyo", click_type=ZONE_INFO_TYPE
        ),
    ] = ZoneInfo("UTC"),
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show all orders (default: only first 3)",
        ),
    ] = False,
    log_level: Annotated[
        str,
        typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    ] = "WARNING",
) -> None:
    asyncio.run(
        async_main(
            pair,
            order_state,
            total_count,
            batch_size,
            delay,
            zone_info,
            verbose,
            log_level,
        )
    )


async def async_main(
    pair: str,
    order_state: ChildOrderState | None,
    total_count: int,
    batch_size: int,
    delay: float,
    zone_info: ZoneInfo,
    verbose: bool,
    log_level: str,
) -> None:
    setup_logging(log_level)

    api_key, api_secret = get_key_and_secret("BITFLYER")

    orders = await fetch_orders_with_paging(
        pair,
        order_state,
        total_count,
        batch_size,
        delay,
        api_key,
        api_secret,
        zone_info,
    )

    if verbose:
        display_order_details(orders, zone_info)
    else:
        display_limited_orders(orders, zone_info)

    display_summary(pair, orders, order_state)


async def fetch_orders_with_paging(
    product_code: str,
    order_state: ChildOrderState | None,
    total_count: int,
    batch_size: int,
    delay: float,
    api_key: SecretStr,
    api_secret: SecretStr,
    zone: ZoneInfo | None = None,
) -> list[ChildOrder]:
    all_orders: list[ChildOrder] = []
    before_id: str | None = None
    request_count = 0

    async with create_session(
        Exchange.BITFLYER, api_key=api_key, api_secret=api_secret
    ) as session:
        while len(all_orders) < total_count:
            remaining = total_count - len(all_orders)
            count = min(batch_size, remaining)

            request = ChildOrdersRequest(
                product_code=product_code,
                child_order_state=order_state,
                count=count,
                before=before_id,
            )

            request_count += 1
            console.print(
                f"[bold blue][Request {request_count}][/bold blue] "
                f"Fetching {count} orders..."
            )

            orders = await session.api.getchildorders(request)

            if not orders:
                console.print("No more orders available.", style="dim yellow")
                break

            all_orders.extend(orders)

            console.print(
                f"  [green]→[/green] Fetched [bold]{len(orders)}[/bold] orders. "
                f"Total: [bold cyan]{len(all_orders)}/{total_count}[/bold cyan]"
            )

            # Display order date/time range
            if orders:
                newest = orders[0].child_order_date
                oldest = orders[-1].child_order_date
                if zone:
                    newest_display = newest.astimezone(zone)
                    oldest_display = oldest.astimezone(zone)
                    zone_name = zone.key if hasattr(zone, "key") else str(zone)
                    console.print(
                        f"     [dim]Range:[/dim] {newest_display.strftime('%Y-%m-%d %H:%M:%S')} ~ "
                        f"{oldest_display.strftime('%Y-%m-%d %H:%M:%S')} ({zone_name})",
                        style="dim",
                    )
                else:
                    console.print(
                        f"     [dim]Range:[/dim] {newest.strftime('%Y-%m-%d %H:%M:%S')} ~ "
                        f"{oldest.strftime('%Y-%m-%d %H:%M:%S')} (UTC)",
                        style="dim",
                    )

            if orders:
                before_id = orders[-1].child_order_acceptance_id

            if len(orders) < count:
                console.print("Reached the end of available orders.", style="dim green")
                break

            if len(all_orders) >= total_count:
                console.print(
                    f"[bold green]✓[/bold green] Reached target count: {total_count}"
                )
                break

            if len(all_orders) < total_count:
                await asyncio.sleep(delay)

    return all_orders[:total_count]


def display_summary(
    product_code: str,
    orders: list[ChildOrder],
    order_state: ChildOrderState | None,
) -> None:
    state_str = order_state.value if order_state else "ALL"

    if not orders:
        console.print(
            f"No matching orders found. ({product_code}, State: {state_str})",
            style="dim yellow",
        )
        return

    console.print("\n📊 Summary:", style="bold green")
    console.print(f"  [bold]Pair:[/bold] {product_code}")
    console.print(
        f"  [bold]Total:[/bold] {len(orders)} orders ([dim]State: {state_str}[/dim])"
    )

    buy_count = sum(1 for order in orders if order.side == Side.BUY)
    sell_count = sum(1 for order in orders if order.side == Side.SELL)
    console.print(
        f"  [bold]Breakdown:[/bold] [green]Buy: {buy_count}[/green] / [red]Sell: {sell_count}[/red]"
    )


def display_limited_orders(orders: list[ChildOrder], tz: ZoneInfo) -> None:
    """Display a limited number of orders (when not verbose).

    :param orders: List of orders
    :param tz: Timezone
    """
    if not orders:
        return

    console.print("\n[bold]Recent Orders:[/bold]")

    # Display only first 3
    display_count = min(3, len(orders))
    for i in range(display_count):
        order = orders[i]
        order_display = order.with_timezone(tz)
        side_color = "green" if order.side == Side.BUY else "red"
        console.print(
            f"  [{side_color}]{order.side.value}[/{side_color}] "
            f"{order.size} @ {order.price if order.price else 'MARKET'} "
            f"[dim]({order_display.child_order_date.strftime('%Y-%m-%d %H:%M:%S')})[/dim]"
        )

    # Display message if there are omitted orders
    if len(orders) > 3:
        omitted_count = len(orders) - 3
        console.print(
            f"\n[dim]... {omitted_count} more orders omitted. "
            f"Use --verbose to show all.[/dim]"
        )


def display_order_details(orders: list[ChildOrder], tz: ZoneInfo) -> None:
    """Display detailed information for all orders (when verbose).

    :param orders: List of orders
    :param tz: Timezone
    """
    if not orders:
        return

    console.print("\n[bold]Detailed Order List:[/bold]")
    console.print("=" * 60)

    for order in orders:
        converted = order.with_timezone(tz)
        side_color = "green" if converted.side == Side.BUY else "red"

        console.print(f"\n[bold]Order ID:[/bold] {converted.child_order_id}")
        console.print(
            f"  [dim]Acceptance ID:[/dim] {converted.child_order_acceptance_id}"
        )
        console.print(f"  [bold]Type:[/bold] {converted.child_order_type.value}")
        console.print(
            f"  [bold]Side:[/bold] [{side_color}]{converted.side.value}[/{side_color}]"
        )
        console.print(f"  [bold]Size:[/bold] {converted.size}")
        console.print(
            f"  [bold]Price:[/bold] {converted.price if converted.price else 'MARKET'}"
        )
        console.print(f"  [bold]Outstanding:[/bold] {converted.outstanding_size}")
        console.print(f"  [bold]Executed:[/bold] {converted.executed_size}")
        if converted.average_price:
            console.print(f"  [bold]Avg Price:[/bold] {converted.average_price}")
        console.print(f"  [bold]State:[/bold] {converted.child_order_state.value}")
        console.print(f"  [bold]Order Date:[/bold] {converted.child_order_date}")
        if converted.expire_date:
            console.print(f"  [bold]Expire Date:[/bold] {converted.expire_date}")


if __name__ == "__main__":
    app()
