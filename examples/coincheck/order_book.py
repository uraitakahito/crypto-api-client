#!/usr/bin/env python3
"""Sample script to fetch order book from Coincheck

.. code-block:: console

    # Fetch order book for BTC/JPY
    uv run python examples/coincheck/order_book.py --pair btc_jpy --price-band 100000 --rows 5

    # Fetch order book for XRP/JPY
    uv run python examples/coincheck/order_book.py --pair xrp_jpy --price-band 0.1 --rows 5
"""

import asyncio
import sys
from decimal import Decimal
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from common.helpers import format_price, setup_logging
from common.order_book_display import display_order_book_table_with_bands
from common.typer_custom_types import POSITIVE_DECIMAL_TYPE

from crypto_api_client import Exchange, create_session
from crypto_api_client.coincheck import OrderBook, OrderBookRequest

app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=False,
)


@app.command()
def main(
    pair: Annotated[
        str,
        typer.Option(
            "--pair",
            help="Currency pair (e.g., btc_jpy, eth_jpy, etc_jpy)",
        ),
    ],
    price_band: Annotated[
        Decimal,
        typer.Option(
            "--price-band",
            help="Price band width for grouping orders (e.g., 1000 groups orders within 1000 JPY ranges, or 0.1 for smaller price ranges)",
            click_type=POSITIVE_DECIMAL_TYPE,
        ),
    ],
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
) -> None:
    asyncio.run(
        async_main(
            price_band,
            pair,
            rows,
            log_level,
        )
    )


async def async_main(
    price_band: Decimal,
    pair: str,
    rows: int,
    log_level: str,
) -> None:
    setup_logging(log_level)

    request = OrderBookRequest(pair=pair)

    async with create_session(Exchange.COINCHECK) as session:
        order_book = await session.api.order_book(request)

    display_order_book(order_book, request, rows, price_band)


def display_order_book(
    order_book: OrderBook,
    request: OrderBookRequest,
    rows: int,
    price_band: Decimal,
) -> None:
    # Format price_band value according to precision (e.g., 1000 → "1,000", 0.1 → "0.1")
    price_band_str = format_price(price_band, align_to=price_band)

    title = f"Order Book: {request.pair} (Price Band: {price_band_str} | Spread: {order_book.spread:,.0f})"
    display_order_book_table_with_bands(
        title, order_book, rows, price_band, size_precision=6
    )


if __name__ == "__main__":
    app()
