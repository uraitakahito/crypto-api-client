#!/usr/bin/env python3
"""Sample program to fetch and display order books from multiple exchanges simultaneously

Fetches BTC/JPY order books from 5 exchanges (BINANCE, bitbank, bitFlyer, Coincheck, GMO Coin),
aggregates by price bands, and displays them. Allows comparison of bid/ask books, spreads,
and buying/selling pressure across exchanges.

.. code-block:: console

    uv run python examples/multi_exchange_orderbook.py --rows 10 --price-band 5000
"""

import asyncio
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent))

import typer
from common.display import BUY_COLOR, SELL_COLOR
from common.helpers import setup_logging
from rich.console import Console
from rich.table import Table

from crypto_api_client import Exchange, create_session
from crypto_api_client.binance import (
    Depth as BinanceDepth,
)
from crypto_api_client.binance import (
    DepthRequest as BinanceDepthRequest,
)
from crypto_api_client.bitbank import (
    Depth as BitbankDepth,
)
from crypto_api_client.bitbank import (
    DepthRequest as BitbankDepthRequest,
)
from crypto_api_client.bitflyer import (
    Board,
    BoardRequest,
)
from crypto_api_client.coincheck import (
    OrderBook as CoincheckOrderBook,
)
from crypto_api_client.coincheck import (
    OrderBookRequest as CoincheckOrderBookRequest,
)
from crypto_api_client.gmocoin import (
    OrderBook as GmoCoinOrderBook,
)
from crypto_api_client.gmocoin import (
    OrderBookRequest as GmoCoinOrderBookRequest,
)

app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=False,
)
console = Console()


@dataclass
class OrderBookEntry:
    """Unified order book entry"""

    price: Decimal
    size: Decimal


@dataclass
class UnifiedOrderBook:
    """Unified order book structure"""

    exchange: str
    symbol: str
    bids: list[OrderBookEntry]  # Bid side
    asks: list[OrderBookEntry]  # Ask side
    spread: Decimal | None = None


@dataclass
class AggregatedOrderBookEntry:
    """Aggregated order book entry"""

    price: Decimal
    total_size: Decimal
    exchange_sizes: dict[str, Decimal]  # Size per exchange


@dataclass
class AggregatedOrderBook:
    """Order book aggregated by price bands"""

    bids: list[AggregatedOrderBookEntry]  # Bid side (descending price order)
    asks: list[AggregatedOrderBookEntry]  # Ask side (ascending price order)
    total_bid_size: Decimal
    total_ask_size: Decimal
    exchanges: list[str]  # Included exchanges


@app.command()
def main(
    rows: Annotated[
        int,
        typer.Option(
            "--rows",
            help="Number of rows to display (applied after price band grouping)",
        ),
    ] = 5,
    log_level: Annotated[
        str,
        typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    ] = "WARNING",
    price_band: Annotated[
        int,
        typer.Option(
            "--price-band",
            help="Price band width for aggregation (e.g., 1000 for 1000 JPY bands)",
        ),
    ] = 1000,
) -> None:
    base = "BTC"
    quote = "JPY"

    asyncio.run(
        async_main(
            base,
            quote,
            rows,
            log_level,
            price_band,
        )
    )


async def async_main(
    base: str,
    quote: str,
    rows: int,
    log_level: str,
    price_band: int,
) -> None:
    setup_logging(log_level)

    try:
        orderbooks = await asyncio.gather(
            fetch_bitflyer_orderbook(base.upper(), quote.upper()),
            fetch_binance_orderbook(base.upper(), quote.upper(), limit=5000),
            fetch_bitbank_orderbook(base.lower(), quote.lower()),
            fetch_coincheck_orderbook(base.lower(), quote.lower()),
            fetch_gmocoin_orderbook(base.upper(), quote.upper()),
            return_exceptions=False,
        )

        valid_orderbooks = [ob for ob in orderbooks if ob is not None]

        if valid_orderbooks:
            display_orderbooks(
                valid_orderbooks,
                rows,
                price_band=Decimal(str(price_band)),
            )
        else:
            console.print("[red]Failed to fetch any order books[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


async def fetch_bitflyer_orderbook(base: str, quote: str) -> UnifiedOrderBook | None:
    try:
        async with create_session(Exchange.BITFLYER) as session:
            # bitFlyer uses uppercase with underscore separator
            product_code = f"{base}_{quote}"
            request = BoardRequest(product_code=product_code)
            board = await session.api.board(request)
            return convert_bitflyer_board(board, product_code)
    except Exception as e:
        console.print(f"[red]bitFlyer error: {e}[/red]")
        return None


async def fetch_binance_orderbook(
    base: str, quote: str, limit: int = 1000
) -> UnifiedOrderBook | None:
    try:
        async with create_session(Exchange.BINANCE) as session:
            # BINANCE uses no separator
            symbol = f"{base}{quote}"
            request = BinanceDepthRequest(symbol=symbol, limit=limit)
            depth = await session.api.depth(request)
            return convert_binance_depth(depth, symbol)
    except Exception as e:
        console.print(f"[red]BINANCE error: {e}[/red]")
        return None


async def fetch_bitbank_orderbook(base: str, quote: str) -> UnifiedOrderBook | None:
    try:
        async with create_session(Exchange.BITBANK) as session:
            # bitbank uses lowercase with underscore separator
            pair_str = f"{base.lower()}_{quote.lower()}"
            request = BitbankDepthRequest(pair=pair_str)
            depth = await session.api.depth(request)
            return convert_bitbank_depth(depth, pair_str)
    except Exception as e:
        console.print(f"[red]bitbank error: {e}[/red]")
        return None


async def fetch_coincheck_orderbook(base: str, quote: str) -> UnifiedOrderBook | None:
    try:
        async with create_session(Exchange.COINCHECK) as session:
            # Coincheck uses lowercase with underscore separator
            pair_str = f"{base.lower()}_{quote.lower()}"
            request = CoincheckOrderBookRequest(pair=pair_str)
            order_book = await session.api.order_book(request)
            return convert_coincheck_orderbook(order_book, pair_str)
    except Exception as e:
        console.print(f"[red]Coincheck error: {e}[/red]")
        return None


async def fetch_gmocoin_orderbook(base: str, quote: str) -> UnifiedOrderBook | None:
    try:
        async with create_session(Exchange.GMOCOIN) as session:
            # GMO Coin uses uppercase with underscore separator
            pair_str = f"{base.upper()}_{quote.upper()}"
            request = GmoCoinOrderBookRequest(symbol=pair_str)
            order_book = await session.api.orderbook(request)
            return convert_gmocoin_orderbook(order_book, pair_str)
    except Exception as e:
        console.print(f"[red]GMO Coin error: {e}[/red]")
        return None


def convert_bitflyer_board(board: Board, symbol: str) -> UnifiedOrderBook:
    """Convert bitFlyer Board to unified format"""
    bids = [
        OrderBookEntry(price=Decimal(str(b.price)), size=Decimal(str(b.size)))
        for b in board.bids
    ]
    asks = [
        OrderBookEntry(price=Decimal(str(a.price)), size=Decimal(str(a.size)))
        for a in board.asks
    ]

    spread = None
    if asks and bids:
        spread = asks[0].price - bids[0].price

    return UnifiedOrderBook(
        exchange="bitFlyer", symbol=symbol, bids=bids, asks=asks, spread=spread
    )


def convert_binance_depth(depth: BinanceDepth, symbol: str) -> UnifiedOrderBook:
    """Convert BINANCE Depth to unified format"""
    bids = [OrderBookEntry(price=b.price, size=b.quantity) for b in depth.bids]
    asks = [OrderBookEntry(price=a.price, size=a.quantity) for a in depth.asks]

    spread = depth.spread

    return UnifiedOrderBook(
        exchange="BINANCE", symbol=symbol, bids=bids, asks=asks, spread=spread
    )


def convert_bitbank_depth(depth: BitbankDepth, symbol: str) -> UnifiedOrderBook:
    """Convert bitbank Depth to unified format"""
    bids = [OrderBookEntry(price=b.price, size=b.size) for b in depth.bids]
    asks = [OrderBookEntry(price=a.price, size=a.size) for a in depth.asks]

    spread = depth.spread

    return UnifiedOrderBook(
        exchange="bitbank", symbol=symbol, bids=bids, asks=asks, spread=spread
    )


def convert_coincheck_orderbook(
    order_book: CoincheckOrderBook, symbol: str
) -> UnifiedOrderBook:
    """Convert Coincheck OrderBook to unified format"""
    bids = [OrderBookEntry(price=b.price, size=b.size) for b in order_book.bids]
    asks = [OrderBookEntry(price=a.price, size=a.size) for a in order_book.asks]

    spread = order_book.spread

    return UnifiedOrderBook(
        exchange="Coincheck", symbol=symbol, bids=bids, asks=asks, spread=spread
    )


def convert_gmocoin_orderbook(
    order_book: GmoCoinOrderBook, symbol: str
) -> UnifiedOrderBook:
    """Convert GMO Coin OrderBook to unified format"""
    bids = [OrderBookEntry(price=b.price, size=b.size) for b in order_book.bids]
    asks = [OrderBookEntry(price=a.price, size=a.size) for a in order_book.asks]

    spread = order_book.spread

    return UnifiedOrderBook(
        exchange="GMO Coin", symbol=symbol, bids=bids, asks=asks, spread=spread
    )


def aggregate_orderbooks(
    orderbooks: list[UnifiedOrderBook], price_band: Decimal = Decimal("1000")
) -> AggregatedOrderBook:
    """Aggregate order books from multiple exchanges by price bands"""

    # Aggregate bid side (by price band)
    bid_aggregation: dict[Decimal, dict[str, Decimal]] = {}
    for ob in orderbooks:
        for bid in ob.bids:
            # Round to price band (e.g., 1000 JPY units)
            price_band_key = (bid.price // price_band) * price_band
            if price_band_key not in bid_aggregation:
                bid_aggregation[price_band_key] = {}
            if ob.exchange not in bid_aggregation[price_band_key]:
                bid_aggregation[price_band_key][ob.exchange] = Decimal(0)
            bid_aggregation[price_band_key][ob.exchange] += bid.size

    # Aggregate ask side (by price band)
    ask_aggregation: dict[Decimal, dict[str, Decimal]] = {}
    for ob in orderbooks:
        for ask in ob.asks:
            # Round to price band (e.g., 1000 JPY units)
            price_band_key = (ask.price // price_band) * price_band
            if price_band_key not in ask_aggregation:
                ask_aggregation[price_band_key] = {}
            if ob.exchange not in ask_aggregation[price_band_key]:
                ask_aggregation[price_band_key][ob.exchange] = Decimal(0)
            ask_aggregation[price_band_key][ob.exchange] += ask.size

    # Convert to list of AggregatedOrderBookEntry
    aggregated_bids: list[AggregatedOrderBookEntry] = []
    for price, exchange_sizes in sorted(bid_aggregation.items(), reverse=True):
        total_size = Decimal(sum(exchange_sizes.values()))
        aggregated_bids.append(
            AggregatedOrderBookEntry(
                price=price,
                total_size=total_size,
                exchange_sizes=exchange_sizes,
            )
        )

    aggregated_asks: list[AggregatedOrderBookEntry] = []
    for price, exchange_sizes in sorted(ask_aggregation.items()):
        total_size = Decimal(sum(exchange_sizes.values()))
        aggregated_asks.append(
            AggregatedOrderBookEntry(
                price=price,
                total_size=total_size,
                exchange_sizes=exchange_sizes,
            )
        )

    total_bid_size = sum(entry.total_size for entry in aggregated_bids)
    total_ask_size = sum(entry.total_size for entry in aggregated_asks)

    return AggregatedOrderBook(
        bids=aggregated_bids,
        asks=aggregated_asks,
        total_bid_size=total_bid_size if total_bid_size else Decimal(0),
        total_ask_size=total_ask_size if total_ask_size else Decimal(0),
        exchanges=[ob.exchange for ob in orderbooks],
    )


def create_aggregated_orderbook_table(
    agg_book: AggregatedOrderBook,
    rows: int,
    orderbooks: list[UnifiedOrderBook],
    price_band: Decimal,
) -> Table:
    """Create table for aggregated order book"""
    table = Table(
        title="Aggregated Market Depth (All Exchanges)",
        show_header=True,
    )

    # Add columns - Ask side
    table.add_column("Total Ask", justify="right", style=SELL_COLOR)
    for exchange in agg_book.exchanges:
        table.add_column(f"{exchange}", justify="right", style="dim")

    # Central price range column
    table.add_column("Price Range", justify="center")

    # Bid side
    for exchange in agg_book.exchanges:
        table.add_column(f"{exchange}", justify="right", style="dim")
    table.add_column("Total Bid", justify="right", style=BUY_COLOR)

    # Select and display price bands near best bid/ask
    ask_bands = {entry.price: entry for entry in agg_book.asks}
    bid_bands = {entry.price: entry for entry in agg_book.bids}

    bands_to_display = select_bands_to_display(ask_bands, bid_bands, rows)

    # Calculate cumulative sizes (from center price outward)
    ask_cumulatives = calculate_cumulative_sizes(ask_bands, is_ask_side=True)
    bid_cumulatives = calculate_cumulative_sizes(bid_bands, is_ask_side=False)

    for band in bands_to_display:
        row_data: list[str] = []

        price_range = f"{band:,.0f} - {band + price_band:,.0f}"

        has_ask = band in ask_bands
        has_bid = band in bid_bands

        # Ask side
        if has_ask:
            ask = ask_bands[band]
            row_data.append(f"{ask_cumulatives[band]:.6f}")
            for exchange in agg_book.exchanges:
                size = ask.exchange_sizes.get(exchange, Decimal(0))
                row_data.append(f"{size:.6f}" if size > 0 else "")
        else:
            row_data.extend([""] * (1 + len(agg_book.exchanges)))

        # Determine price range color
        if has_ask and has_bid:
            styled_price_range = price_range
        elif has_ask:
            styled_price_range = f"[{SELL_COLOR}]{price_range}[/{SELL_COLOR}]"
        elif has_bid:
            styled_price_range = f"[{BUY_COLOR}]{price_range}[/{BUY_COLOR}]"
        else:
            styled_price_range = price_range

        row_data.append(styled_price_range)

        # Bid side
        if has_bid:
            bid = bid_bands[band]
            for exchange in agg_book.exchanges:
                size = bid.exchange_sizes.get(exchange, Decimal(0))
                row_data.append(f"{size:.6f}" if size > 0 else "")
            row_data.append(f"{bid_cumulatives[band]:.6f}")
        else:
            row_data.extend([""] * (1 + len(agg_book.exchanges)))

        table.add_row(*row_data)

    return table


def select_bands_to_display(
    ask_bands: dict[Decimal, AggregatedOrderBookEntry],
    bid_bands: dict[Decimal, AggregatedOrderBookEntry],
    rows: int,
) -> list[Decimal]:
    """Select price bands to display (closest to best bid/ask first)"""
    all_bands = sorted(set(ask_bands.keys()) | set(bid_bands.keys()), reverse=True)

    if len(all_bands) <= rows:
        return all_bands

    # Identify best ask and best bid
    best_ask_band = min(ask_bands.keys()) if ask_bands else Decimal("inf")
    best_bid_band = max(bid_bands.keys()) if bid_bands else Decimal("-inf")

    # Calculate center price
    if ask_bands and bid_bands:
        center = (best_ask_band + best_bid_band) // 2
    elif ask_bands:
        center = best_ask_band
    else:
        center = best_bid_band

    # Sort by distance from center
    all_bands_with_distance = [(abs(band - center), band) for band in all_bands]
    all_bands_with_distance.sort()

    # Select top rows and re-sort by price
    selected_bands = [band for _, band in all_bands_with_distance[:rows]]
    return sorted(selected_bands, reverse=True)


def calculate_cumulative_sizes(
    bands: dict[Decimal, AggregatedOrderBookEntry], is_ask_side: bool
) -> dict[Decimal, Decimal]:
    """Calculate cumulative sizes from center price outward

    :param bands: Order aggregation data by price band
    :param is_ask_side: True=ask side, False=bid side
    :returns: Dictionary of cumulative sizes
    """
    cumulatives: dict[Decimal, Decimal] = {}

    if not bands:
        return cumulatives

    cumulative = Decimal(0)
    if is_ask_side:
        # Ask side cumulative (from low price = outward from best ask)
        for band in sorted(bands.keys()):
            cumulative += bands[band].total_size
            cumulatives[band] = cumulative
    else:
        # Bid side cumulative (from high price = outward from best bid)
        for band in sorted(bands.keys(), reverse=True):
            cumulative += bands[band].total_size
            cumulatives[band] = cumulative

    return cumulatives


def display_orderbooks(
    orderbooks: list[UnifiedOrderBook],
    rows: int,
    price_band: Decimal = Decimal("1000"),
) -> None:
    """Aggregate and display multiple order books"""
    # Aggregated view
    agg_book = aggregate_orderbooks(orderbooks, price_band)

    # Display aggregated table
    agg_table = create_aggregated_orderbook_table(
        agg_book, rows, orderbooks, price_band
    )
    console.print(agg_table)


if __name__ == "__main__":
    app()
