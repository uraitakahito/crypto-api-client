#!/usr/bin/env python3
"""Sample script to fetch and display BTC/JPY ticker information from all exchanges

Fetches price information for BTC/JPY currency pair from each exchange in parallel
and displays as a comparison table.
Supported exchanges: BINANCE, bitbank, bitFlyer, Coincheck, GMO Coin

.. code-block:: console

    # Fetch BTC/JPY ticker information
    uv run python examples/tickers.py
"""

import asyncio
import sys
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Any
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from common.display import BUY_COLOR, SELL_COLOR
from common.helpers import setup_logging
from common.ticker_fetcher import fetch_all_btc_jpy_tickers
from common.typer_custom_types import ZONE_INFO_TYPE
from rich.console import Console
from rich.table import Table

# Unified settings for development environment
app = typer.Typer(
    pretty_exceptions_enable=True,  # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False,  # Show full traceback
)
console = Console()


@app.command()
def main(
    zone_info: Annotated[
        ZoneInfo,
        typer.Option(
            "--zone", help="Timezone (e.g., Asia/Tokyo)", click_type=ZONE_INFO_TYPE
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

    tickers = await fetch_all_btc_jpy_tickers()

    table = create_comparison_table(tickers, zone_info)
    console.print(table)

    display_price_statistics(tickers)


def create_comparison_table(
    tickers: list[dict[str, Any]], zone_info: ZoneInfo
) -> Table:
    table = Table(
        title="BTC/JPY Ticker Information by Exchange",
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("Exchange", style="cyan", width=12)
    table.add_column("Last Price", justify="right", style="yellow")
    table.add_column("Ask Price", justify="right", style=SELL_COLOR)
    table.add_column("Bid Price", justify="right", style=BUY_COLOR)
    table.add_column("Spread", justify="right", style="white")
    table.add_column("24h Volume", justify="right", style="green")
    table.add_column("24h High", justify="right", style="bright_green")
    table.add_column("24h Low", justify="right", style="bright_red")
    table.add_column("Timestamp", style="dim")

    for ticker_data in tickers:
        if "error" in ticker_data:
            table.add_row(
                ticker_data["exchange"],
                "[red]Error[/red]",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                ticker_data.get("error", "Unknown error"),
            )
            continue

        # Calculate spread
        spread = "-"
        if ticker_data.get("ask_price") and ticker_data.get("bid_price"):
            try:
                ask = Decimal(str(ticker_data["ask_price"]))
                bid = Decimal(str(ticker_data["bid_price"]))

                spread_value = ask - bid
                spread_pct = (spread_value / bid * 100) if bid > 0 else 0
                spread = f"{spread_value:,.0f} ({spread_pct:.3f}%)"
            except (ValueError, TypeError, AttributeError):
                pass

        # Format price
        def format_price(price: Any) -> str:
            if price is None:
                return "-"
            try:
                return f"¥{Decimal(str(price)):,.0f}"
            except (ValueError, TypeError, AttributeError):
                return str(price)

        # Format volume
        def format_volume(volume: Any) -> str:
            if volume is None:
                return "-"
            try:
                vol = Decimal(str(volume))
                return f"{vol:,.0f}"
            except (ValueError, TypeError, AttributeError):
                return str(volume)

        # Format timestamp
        timestamp_str = "-"
        if ticker_data.get("timestamp"):
            try:
                dt = ticker_data["timestamp"]
                if hasattr(dt, "astimezone"):
                    dt = dt.astimezone(zone_info)
                    timestamp_str = dt.strftime("%H:%M:%S")
            except (AttributeError, TypeError):
                pass

        table.add_row(
            ticker_data["exchange"],
            format_price(ticker_data.get("last_price")),
            format_price(ticker_data.get("ask_price")),
            format_price(ticker_data.get("bid_price")),
            spread,
            format_volume(ticker_data.get("volume")),
            format_price(ticker_data.get("high")),
            format_price(ticker_data.get("low")),
            timestamp_str,
        )

    return table


def display_price_statistics(tickers: list[dict[str, Any]]) -> None:
    valid_tickers = [
        t for t in tickers if "error" not in t and t.get("last_price") is not None
    ]

    if len(valid_tickers) < 2:
        return

    console.print("\n[bold cyan]📊 Price Statistics[/bold cyan]")

    # Statistics for last traded price
    prices = [Decimal(str(t["last_price"])) for t in valid_tickers]
    avg_price = sum(prices) / len(prices)
    max_price = max(prices)
    min_price = min(prices)
    price_range = max_price - min_price

    console.print(f"  Average price: ¥{avg_price:,.0f}")
    console.print(f"  Highest price: ¥{max_price:,.0f}")
    console.print(f"  Lowest price : ¥{min_price:,.0f}")
    console.print(
        f"  Price range  : ¥{price_range:,.0f} ({price_range / min_price * 100:.3f}%)"
    )


if __name__ == "__main__":
    try:
        app()
    except Exception:
        raise typer.Exit(1)
