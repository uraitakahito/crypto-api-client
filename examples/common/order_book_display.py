"""Common order book display logic

Provides common order book display functionality for multiple exchanges (BINANCE, bitbank, bitFlyer).
Eliminates duplicate code following the DRY principle.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from decimal import Decimal
from typing import Protocol

from rich.console import Console
from rich.table import Table

from .display import BUY_COLOR, SELL_COLOR
from .helpers import format_price

console = Console()


def get_item_size(item: OrderBookItem) -> Decimal:
    """Get size from order book item

    Supports both `quantity` attribute (used by BINANCE) and
    `size` attribute (used by other exchanges).

    :param item: Order book item
    :return: Order size
    """
    # Check attribute existence using hasattr
    if hasattr(item, "quantity"):
        return item.quantity  # type: ignore[attr-defined]
    elif hasattr(item, "size"):
        return item.size  # type: ignore[attr-defined]
    else:
        raise AttributeError(
            f"OrderBookItem must have either 'quantity' or 'size' attribute, got {type(item)}"
        )


class OrderBookItem(Protocol):
    """Common interface for order book items

    Protocol that order (ask/bid) objects from each exchange should implement.
    BINANCE uses quantity attribute, other exchanges use size attribute.
    """

    price: Decimal


class OrderBook(Protocol):
    """Common interface for order books

    Protocol that order book (depth/board) objects from each exchange should implement.
    Since Sequence is covariant, it can accept list[DepthEntry] or list[BoardEntry].
    """

    @property
    def asks(self) -> Sequence[OrderBookItem]:
        """List of ask/sell orders"""
        ...

    @property
    def bids(self) -> Sequence[OrderBookItem]:
        """List of bid/buy orders"""
        ...


def aggregate_orders_by_price_band(
    order_book: OrderBook, price_band: Decimal
) -> tuple[dict[Decimal, Decimal], dict[Decimal, Decimal]]:
    """Aggregate orders by price band

    :param order_book: Order book object
    :param price_band: Width of price band
    :return: (ask_bands, bid_bands) - Aggregation dictionaries by price band
    """
    ask_bands: dict[Decimal, Decimal] = defaultdict(Decimal)
    bid_bands: dict[Decimal, Decimal] = defaultdict(Decimal)

    for ask in order_book.asks:
        band = (ask.price // price_band) * price_band
        ask_bands[band] += get_item_size(ask)

    for bid in order_book.bids:
        band = (bid.price // price_band) * price_band
        bid_bands[band] += get_item_size(bid)

    return ask_bands, bid_bands


def select_bands_to_display(
    ask_bands: dict[Decimal, Decimal], bid_bands: dict[Decimal, Decimal], rows: int
) -> list[Decimal]:
    """Select price bands to display

    Prioritizes price bands closer to the center price.

    :param ask_bands: Aggregated ask orders by price band
    :param bid_bands: Aggregated bid orders by price band
    :param rows: Number of rows to display
    :return: List of selected price bands (descending order)
    """
    all_bands = sorted(set(ask_bands.keys()) | set(bid_bands.keys()), reverse=True)

    if len(all_bands) <= rows:
        return all_bands

    best_ask_band = min(ask_bands.keys()) if ask_bands else Decimal("inf")
    best_bid_band = max(bid_bands.keys()) if bid_bands else Decimal("-inf")

    if ask_bands and bid_bands:
        center = (best_ask_band + best_bid_band) / 2
    elif ask_bands:
        center = best_ask_band
    else:
        center = best_bid_band

    # Sort by distance from center
    # Example: all_bands=[10000, 10100, 10200, 10300, 10400, 10500, 10600], center=10250
    #     → [(250, 10000), (150, 10100), (50, 10200), (50, 10300), (150, 10400), (250, 10500), (350, 10600)]
    #     → After sort: [(50, 10200), (50, 10300), (150, 10100), (150, 10400), (250, 10000), (250, 10500), (350, 10600)]
    all_bands_with_distance = [(abs(band - center), band) for band in all_bands]
    all_bands_with_distance.sort()

    # Select top rows and re-sort by price
    selected_bands = [band for _, band in all_bands_with_distance[:rows]]
    return sorted(selected_bands, reverse=True)


def calculate_cumulative_sizes(
    ask_bands: dict[Decimal, Decimal], bid_bands: dict[Decimal, Decimal]
) -> tuple[dict[Decimal, Decimal], dict[Decimal, Decimal]]:
    """Calculate cumulative sizes from center price outward

    :param ask_bands: Aggregated ask orders by price band
    :param bid_bands: Aggregated bid orders by price band
    :return: (ask_cumulatives, bid_cumulatives) - Dictionaries of cumulative sizes
    """
    ask_cumulatives: dict[Decimal, Decimal] = {}
    bid_cumulatives: dict[Decimal, Decimal] = {}

    # Calculate cumulative for asks (from center price outward)
    if ask_bands:
        ask_cumulative = Decimal(0)
        for band in sorted(ask_bands.keys()):  # From lower prices (closer to center)
            ask_cumulative += ask_bands[band]
            ask_cumulatives[band] = ask_cumulative

    # Calculate cumulative for bids (from center price outward)
    if bid_bands:
        bid_cumulative = Decimal(0)
        for band in sorted(
            bid_bands.keys(), reverse=True
        ):  # From higher prices (closer to center)
            bid_cumulative += bid_bands[band]
            bid_cumulatives[band] = bid_cumulative

    return ask_cumulatives, bid_cumulatives


def format_price_range_style(price_range: str, has_ask: bool, has_bid: bool) -> str:
    """Format price range display style

    :param price_range: Price range string
    :param has_ask: Whether ask orders exist
    :param has_bid: Whether bid orders exist
    :return: Styled price range string
    """
    if has_ask and has_bid:
        return price_range
    elif has_ask:
        return f"[{SELL_COLOR}]{price_range}[/{SELL_COLOR}]"
    elif has_bid:
        return f"[{BUY_COLOR}]{price_range}[/{BUY_COLOR}]"
    else:
        return price_range


def display_order_book_table_with_bands(
    title: str,
    order_book: OrderBook,
    rows: int,
    price_band: Decimal,
    size_precision: int = 3,
) -> None:
    """Display order book aggregated by price bands

    :param title: Table title
    :param order_book: Order book object
    :param rows: Number of rows to display
    :param price_band: Width of price band
    :param size_precision: Decimal precision for sizes
    """
    ask_bands, bid_bands = aggregate_orders_by_price_band(order_book, price_band)

    bands_to_display = select_bands_to_display(ask_bands, bid_bands, rows)

    ask_cumulatives, bid_cumulatives = calculate_cumulative_sizes(ask_bands, bid_bands)

    order_book_table = Table(title=title, show_header=True)
    order_book_table.add_column("Ask Total", justify="right", style=SELL_COLOR)
    order_book_table.add_column("Ask Size", justify="right", style=SELL_COLOR)
    order_book_table.add_column("Price Range", justify="center")
    order_book_table.add_column("Bid Size", justify="right", style=BUY_COLOR)
    order_book_table.add_column("Bid Total", justify="right", style=BUY_COLOR)

    for band in bands_to_display:
        band_start = format_price(band, align_to=price_band)
        band_end = format_price(band + price_band, align_to=price_band)
        price_range = f"{band_start} - {band_end}"

        has_ask = band in ask_bands
        has_bid = band in bid_bands

        ask_size = f"{ask_bands[band]:.{size_precision}f}" if has_ask else ""
        ask_cum = f"{ask_cumulatives[band]:.{size_precision}f}" if has_ask else ""
        bid_size = f"{bid_bands[band]:.{size_precision}f}" if has_bid else ""
        bid_cum = f"{bid_cumulatives[band]:.{size_precision}f}" if has_bid else ""

        styled_price_range = format_price_range_style(price_range, has_ask, has_bid)

        order_book_table.add_row(
            ask_cum, ask_size, styled_price_range, bid_size, bid_cum
        )

    console.print(order_book_table)
