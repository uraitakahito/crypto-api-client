#!/usr/bin/env python3
"""Sample script to fetch BINANCE exchange information

Fetches a list and detailed information of currency pairs supported by the exchange.

.. code-block:: console

    # Fetch information for all symbols
    uv run python examples/binance/exchange_info.py

    # Fetch only specific symbol
    uv run python examples/binance/exchange_info.py --symbol BTCUSDT

    # Fetch only symbols with SPOT permission
    uv run python examples/binance/exchange_info.py --permissions SPOT

    # Fetch only symbols with TRADING status
    uv run python examples/binance/exchange_info.py --status TRADING
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.helpers import setup_logging

from crypto_api_client import Exchange, create_session
from crypto_api_client.binance import (
    ExchangeInfo,
    ExchangeInfoRequest,
    ExchangeSymbol,
    SymbolStatus,
)

app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=False,
)
console = Console()


@app.command()
def main(
    symbol: Annotated[
        str | None,
        typer.Option(
            "--symbol",
            help="Single symbol to query (e.g., BTCUSDT)",
        ),
    ] = None,
    permissions: Annotated[
        str | None,
        typer.Option(
            "--permissions",
            help="Filter by permission (SPOT, MARGIN, LEVERAGED, etc.)",
        ),
    ] = None,
    status: Annotated[
        str | None,
        typer.Option(
            "--status",
            help="Filter by symbol status (TRADING, HALT, BREAK)",
        ),
    ] = None,
    show_details: Annotated[
        bool,
        typer.Option(
            "--show-details",
            help="Show detailed information for each symbol",
        ),
    ] = False,
    log_level: Annotated[
        str,
        typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    ] = "WARNING",
) -> None:
    asyncio.run(
        async_main(
            symbol=symbol,
            permissions=permissions,
            symbol_status=status,
            show_details=show_details,
            log_level=log_level,
        )
    )


async def async_main(
    symbol: str | None,
    permissions: str | None,
    symbol_status: str | None,
    show_details: bool,
    log_level: str,
) -> None:
    setup_logging(log_level)

    request_params: dict[str, Any] = {}
    if symbol:
        request_params["symbol"] = symbol
    elif permissions:
        request_params["permissions"] = permissions

    if symbol_status:
        request_params["symbol_status"] = symbol_status

    request = ExchangeInfoRequest(**request_params) if request_params else None

    async with create_session(Exchange.BINANCE) as session:
        exchange_info = await session.api.exchange_info(request)
        display_exchange_info(exchange_info, show_details)


def display_exchange_info(exchange_info: ExchangeInfo, show_details: bool) -> None:
    console.print("\n[bold cyan]🏦 BINANCE Exchange Information[/bold cyan]")
    console.print(f"Timezone: {exchange_info.timezone}")
    console.print(f"Server Time: {exchange_info.serverTime}")
    console.print(f"Total Symbols: {len(exchange_info.symbols)}\n")

    display_rate_limits(exchange_info)

    if show_details:
        display_detailed_symbols(exchange_info.symbols)
    else:
        display_summary_table(exchange_info.symbols)

    display_summary_statistics(exchange_info.symbols)


def display_rate_limits(exchange_info: ExchangeInfo) -> None:
    console.print("[bold]Rate Limits:[/bold]")
    for limit in exchange_info.rateLimits:
        interval_text = f"{limit.intervalNum} {limit.interval.value}"
        console.print(
            f"  • {limit.rateLimitType.value}: {limit.limit} per {interval_text}"
        )
    console.print()


def display_summary_table(symbols: list[ExchangeSymbol]) -> None:
    table = Table(title="Trading Symbols", show_header=True)
    table.add_column("Symbol", style="cyan", width=15)
    table.add_column("Status", style="magenta")
    table.add_column("Base/Quote", style="green")
    table.add_column("Permissions", style="yellow")

    for symbol in symbols:
        status_emoji = get_status_emoji(symbol.status)
        status_display = f"{status_emoji} {symbol.status.value}"
        base_quote = f"{symbol.baseAsset}/{symbol.quoteAsset}"
        permissions_str = ", ".join(symbol.permissions)

        table.add_row(
            symbol.symbol,
            status_display,
            base_quote,
            permissions_str,
        )

    console.print(table)


def display_detailed_symbols(symbols: list[ExchangeSymbol]) -> None:
    for i, symbol in enumerate(symbols, 1):
        console.print(f"\n[bold cyan]═══ {i}. {symbol.symbol} ═══[/bold cyan]")
        console.print(
            f"Status: {get_status_emoji(symbol.status)} {symbol.status.value}"
        )
        console.print(
            f"Base Asset: {symbol.baseAsset} (Precision: {symbol.baseAssetPrecision})"
        )
        console.print(
            f"Quote Asset: {symbol.quoteAsset} (Precision: {symbol.quoteAssetPrecision})"
        )
        console.print(f"Order Types: {', '.join(symbol.orderTypes)}")

        # Trading capabilities
        features: list[str] = []
        if symbol.isSpotTradingAllowed:
            features.append("✓ Spot Trading")
        if symbol.isMarginTradingAllowed:
            features.append("✓ Margin Trading")
        if symbol.icebergAllowed:
            features.append("✓ Iceberg Orders")
        if symbol.ocoAllowed:
            features.append("✓ OCO Orders")
        if symbol.otoAllowed:
            features.append("✓ OTO Orders")

        console.print(f"Features: {', '.join(features)}")
        console.print(f"Permissions: {', '.join(symbol.permissions)}")

        # Filter information (brief display)
        console.print(f"Filters: {len(symbol.filters)} filters applied")

        if i < len(symbols):
            console.print()  # Separator


def display_summary_statistics(symbols: list[ExchangeSymbol]) -> None:
    console.print("\n[bold]📊 Summary Statistics:[/bold]")

    # Count by status
    status_counts: dict[str, int] = {}
    for symbol in symbols:
        status_counts[symbol.status.value] = (
            status_counts.get(symbol.status.value, 0) + 1
        )

    console.print("\nStatus Distribution:")
    for status, count in sorted(status_counts.items()):
        emoji = get_status_emoji_from_string(status)
        console.print(f"  {emoji} {status}: {count}")

    # Count by permission
    permission_counts: dict[str, int] = {}
    for symbol in symbols:
        for perm in symbol.permissions:
            permission_counts[perm] = permission_counts.get(perm, 0) + 1

    console.print("\nPermissions Distribution:")
    for perm, count in sorted(permission_counts.items()):
        console.print(f"  • {perm}: {count}")

    # Feature support statistics
    spot_count = sum(1 for s in symbols if s.isSpotTradingAllowed)
    margin_count = sum(1 for s in symbols if s.isMarginTradingAllowed)
    iceberg_count = sum(1 for s in symbols if s.icebergAllowed)
    oco_count = sum(1 for s in symbols if s.ocoAllowed)

    console.print("\nFeature Support:")
    console.print(f"  • Spot Trading: {spot_count}/{len(symbols)}")
    console.print(f"  • Margin Trading: {margin_count}/{len(symbols)}")
    console.print(f"  • Iceberg Orders: {iceberg_count}/{len(symbols)}")
    console.print(f"  • OCO Orders: {oco_count}/{len(symbols)}")


def get_status_emoji(status: SymbolStatus) -> str:
    emoji_map = {
        SymbolStatus.TRADING: "🟢",
        SymbolStatus.HALT: "🔴",
        SymbolStatus.BREAK: "🟡",
        SymbolStatus.AUCTION_MATCH: "🔵",
        SymbolStatus.PRE_TRADING: "⚪",
        SymbolStatus.POST_TRADING: "⚪",
        SymbolStatus.END_OF_DAY: "⚫",
    }
    return emoji_map.get(status, "⚪")


def get_status_emoji_from_string(status: str) -> str:
    """Return emoji corresponding to status string"""
    try:
        status_enum = SymbolStatus(status)
        return get_status_emoji(status_enum)
    except ValueError:
        return "⚪"


if __name__ == "__main__":
    app()
