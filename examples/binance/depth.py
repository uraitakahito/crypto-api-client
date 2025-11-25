#!/usr/bin/env python3
"""BINANCE order book fetch sample

Sample program to fetch and display order book.
Displays bid and ask order lists, mid price, and spread.

.. code-block:: console

    # Fetch order book for BTC/USDT
    uv run python examples/binance/depth.py --pair BTCUSDT --price-band 100 --rows 10

    # Fetch order book for ETH/USDT
    uv run python examples/binance/depth.py --pair ETHUSDT --price-band 10 --rows 5
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
from crypto_api_client.binance import (
    Depth,
    DepthRequest,
)

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
            help="Currency pair (e.g., BTCUSDT, ETHUSDT)",
        ),
    ],
    price_band: Annotated[
        Decimal,
        typer.Option(
            "--price-band",
            help="Price band width for grouping orders (e.g., 1000 groups orders within 1000 unit ranges, or 0.1 for smaller price ranges)",
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
    asyncio.run(async_main(price_band, pair, rows, log_level))


async def async_main(price_band: Decimal, pair: str, rows: int, log_level: str) -> None:
    setup_logging(log_level)

    request = DepthRequest(
        symbol=pair, limit=5000
    )  # Fetch more data for price band aggregation

    async with create_session(Exchange.BINANCE) as session:
        depth = await session.api.depth(request)

    display_depth(depth, request, rows, price_band)


def display_depth(
    depth: Depth,
    request: DepthRequest,
    rows: int,
    price_band: Decimal,
) -> None:
    # Format price_band value according to precision (e.g., 1000 → "1,000", 0.1 → "0.1")
    price_band_str = format_price(price_band, align_to=price_band)

    title = f"Order Book: {request.symbol} (Price Band: {price_band_str} | Spread: {depth.spread:,.8f})"
    display_order_book_table_with_bands(
        title, depth, rows, price_band, size_precision=8
    )


if __name__ == "__main__":
    app()
