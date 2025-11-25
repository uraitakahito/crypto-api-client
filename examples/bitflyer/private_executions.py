#!/usr/bin/env python3
"""Sample script to fetch your own execution history from bitFlyer

Fetches execution history for your trades on a specified currency pair.
Requires authentication as it uses the Private API.

.. code-block:: console

    # Fetch your execution history for BTC/JPY pair
    uv run python examples/bitflyer/private_executions.py --pair BTC_JPY --zone Asia/Tokyo

    # Fetch execution history for ETH/JPY pair (debug mode)
    uv run python examples/bitflyer/private_executions.py --pair ETH_JPY --zone Asia/Tokyo --log-level DEBUG

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
    PrivateExecution,
    PrivateExecutionsRequest,
    Side,
)

# Unified settings for development environment
app = typer.Typer(
    pretty_exceptions_enable=True,      # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False        # Show full traceback
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
    total_count: Annotated[
        int,
        typer.Option(
            "--total-count",
            min=1,
            max=10000,
            help="Total number of executions to fetch",
        ),
    ] = 1000,
    batch_size: Annotated[
        int,
        typer.Option(
            "--batch-size",
            min=1,
            max=500,
            help="Number of executions per request (API limit: 500)",
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
    zone: Annotated[
        ZoneInfo,
        typer.Option(
            "-Z",
            "--zone",
            help="Timezone: UTC, Asia/Tokyo, etc.",
            click_type=ZONE_INFO_TYPE,
        ),
    ] = ZoneInfo("UTC"),
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level",
            help="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
        ),
    ] = "WARNING",
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show all executions (default: show only 3)",
        ),
    ] = False,
) -> None:
    asyncio.run(
        async_main(pair, zone, total_count, batch_size, delay, log_level, verbose)
    )


async def async_main(
    pair: str,
    zone: ZoneInfo,
    total_count: int,
    batch_size: int,
    delay: float,
    log_level: str,
    verbose: bool,
) -> None:
    setup_logging(log_level)

    api_key, api_secret = get_key_and_secret("bitflyer")

    all_executions = await fetch_executions_with_paging(
        pair, total_count, batch_size, delay, zone, api_key, api_secret
    )

    if verbose:
        for execution in all_executions:
            converted = execution.with_timezone(zone)
            typer.echo(converted)
    else:
        # Display only first 3
        display_count = min(3, len(all_executions))
        for i in range(display_count):
            converted = all_executions[i].with_timezone(zone)
            typer.echo(converted)

        if len(all_executions) > 3:
            omitted_count = len(all_executions) - 3
            console.print(
                f"\n[dim]... {omitted_count} more executions omitted. "
                f"Use --verbose to show all.[/dim]"
            )

    console.print("📊 Summary:", style="bold green")
    buy_count = sum(1 for ex in all_executions if ex.side == Side.BUY)
    sell_count = sum(1 for ex in all_executions if ex.side == Side.SELL)
    no_side_count = sum(1 for ex in all_executions if ex.side is None)
    console.print(
        f"  [bold]Total:[/bold] {len(all_executions)} ([green]Buy: {buy_count}[/green] / [red]Sell: {sell_count}[/red]" +
        (f" / [dim]No side: {no_side_count}[/dim]" if no_side_count > 0 else "") + ")"
    )

    if all_executions:
        oldest_display = all_executions[-1].with_timezone(zone).exec_date
        newest_display = all_executions[0].with_timezone(zone).exec_date
        zone_name = zone.key if hasattr(zone, "key") else str(zone)
        console.print(
            f"  [bold]Period:[/bold] {oldest_display.strftime('%Y-%m-%d %H:%M:%S')} ~ {newest_display.strftime('%Y-%m-%d %H:%M:%S')} ({zone_name})"
        )

        total_buy_size = sum(ex.size for ex in all_executions if ex.side == Side.BUY)
        total_sell_size = sum(
            ex.size for ex in all_executions if ex.side == Side.SELL
        )
        total_commission = sum(ex.commission for ex in all_executions)
        console.print(
            f"  [bold]Volume:[/bold] [green]Buy: {total_buy_size:.8f}[/green] / [red]Sell: {total_sell_size:.8f}[/red]"
        )
        console.print(f"  [bold]Total Commission:[/bold] {total_commission:.8f}")


async def fetch_executions_with_paging(
    product_code: str,
    total_count: int,
    batch_size: int,
    delay: float,
    zone: ZoneInfo | None,
    api_key: SecretStr,
    api_secret: SecretStr,
) -> list[PrivateExecution]:
    all_executions: list[PrivateExecution] = []
    before_id: int | None = None
    request_count = 0

    async with create_session(
        Exchange.BITFLYER, api_key=api_key, api_secret=api_secret
    ) as session:
        while len(all_executions) < total_count:
            remaining = total_count - len(all_executions)
            count = min(batch_size, remaining)

            request = PrivateExecutionsRequest(
                product_code=product_code,
                count=count,
                before=before_id,
            )

            request_count += 1
            console.print(
                f"[bold blue][Request {request_count}][/bold blue] "
                f"Fetching {count} executions..."
            )

            executions = await session.api.private_executions(request)

            if not executions:
                console.print("No more executions available.", style="dim yellow")
                break

            all_executions.extend(executions)

            console.print(
                f"  [green]→[/green] Fetched [bold]{len(executions)}[/bold] executions. "
                f"Total: [bold cyan]{len(all_executions)}/{total_count}[/bold cyan]"
            )

            if executions:
                newest = executions[0].exec_date
                oldest = executions[-1].exec_date
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

            if executions:
                before_id = executions[-1].id

            if len(executions) < count:
                console.print(
                    "Reached the end of available executions.", style="dim green"
                )
                break

            if len(all_executions) >= total_count:
                console.print(
                    f"[bold green]✓[/bold green] Reached target count: {total_count}"
                )
                break

            if len(all_executions) < total_count:
                await asyncio.sleep(delay)

    return all_executions[:total_count]


if __name__ == "__main__":
    app()  # Typer automatically catches and displays exceptions beautifully
