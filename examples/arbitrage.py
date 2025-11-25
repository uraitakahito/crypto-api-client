#!/usr/bin/env python3
"""Sample script to fetch BTC/JPY ticker information from all exchanges and analyze arbitrage opportunities

Arbitrage is a trading strategy that profits from price differences between different exchanges.

.. code-block:: console

    # Analyze arbitrage opportunities for BTC/JPY
    uv run python examples/arbitrage.py
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

    # Display price list table
    table = create_price_table(tickers, zone_info)
    console.print(table)

    # Display arbitrage analysis
    analyze_arbitrage(tickers)


def create_price_table(tickers: list[dict[str, Any]], zone_info: ZoneInfo) -> Table:
    """Create price table"""
    table = Table(
        title="BTC/JPY Price Information by Exchange",
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("Exchange", style="cyan", width=12)
    table.add_column("Ask Price", justify="right", style=SELL_COLOR)
    table.add_column("Bid Price", justify="right", style=BUY_COLOR)
    table.add_column("Spread", justify="right", style="white")
    table.add_column("Timestamp", style="dim")

    for ticker_data in tickers:
        if "error" in ticker_data:
            table.add_row(
                ticker_data["exchange"],
                "[red]Error[/red]",
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
                spread = f"¥{spread_value:,.0f} ({spread_pct:.3f}%)"
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
            format_price(ticker_data.get("ask_price")),
            format_price(ticker_data.get("bid_price")),
            spread,
            timestamp_str,
        )

    return table


def analyze_arbitrage(tickers: list[dict[str, Any]]) -> None:
    valid_tickers = [
        t
        for t in tickers
        if "error" not in t and t.get("bid_price") and t.get("ask_price")
    ]

    if len(valid_tickers) < 2:
        console.print("\n[red]Error: Valid data from less than 2 exchanges[/red]")
        return

    # Display spreads for all exchange pairs
    display_all_spreads(valid_tickers)


def display_all_spreads(tickers: list[dict[str, Any]]) -> None:
    console.print("\n[bold cyan]📈 Spreads for All Exchange Pairs[/bold cyan]")

    # Calculate spreads
    spreads: list[tuple[str, str, Decimal, Decimal]] = []

    for i, buy_exchange in enumerate(tickers):
        for sell_exchange in tickers[i + 1 :]:
            buy_ask = Decimal(str(buy_exchange["ask_price"]))
            sell_bid = Decimal(str(sell_exchange["bid_price"]))

            # Profit when buying on buy_exchange and selling on sell_exchange
            profit1 = sell_bid - buy_ask
            profit1_pct = (profit1 / buy_ask * 100) if buy_ask > 0 else Decimal(0)

            # Reverse direction
            sell_ask = Decimal(str(sell_exchange["ask_price"]))
            buy_bid = Decimal(str(buy_exchange["bid_price"]))
            profit2 = buy_bid - sell_ask
            profit2_pct = (profit2 / sell_ask * 100) if sell_ask > 0 else Decimal(0)

            if profit1 > profit2:
                spreads.append(
                    (
                        buy_exchange["exchange"],
                        sell_exchange["exchange"],
                        profit1,
                        profit1_pct,
                    )
                )
            else:
                spreads.append(
                    (
                        sell_exchange["exchange"],
                        buy_exchange["exchange"],
                        profit2,
                        profit2_pct,
                    )
                )

    # Sort by spread (descending)
    spreads.sort(key=lambda x: x[2], reverse=True)

    # Display top 3
    console.print("\nTop 3 spreads:")
    for i, (buy_ex, sell_ex, profit, profit_pct) in enumerate(spreads[:3], 1):
        color = "green" if profit > 0 else "red"
        console.print(
            f"  {i}. {buy_ex} → {sell_ex}: [{color}]¥{profit:,.0f} ({profit_pct:.3f}%)[/{color}]"
        )


if __name__ == "__main__":
    try:
        app()
    except Exception:
        raise typer.Exit(1)
