#!/usr/bin/env python3
"""Sample script to fetch and display bitFlyer order book

.. code-block:: console

    uv run python examples/bitflyer/board.py --pair BTC_JPY --price-band 100000
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
from crypto_api_client.bitflyer import (
    Board,
    BoardRequest,
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
            help="Currency pair (e.g., BTC_JPY, ETH_JPY)",
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
    asyncio.run(async_main(price_band, pair, rows, log_level))


async def async_main(price_band: Decimal, pair: str, rows: int, log_level: str) -> None:
    setup_logging(log_level)

    request = BoardRequest(product_code=pair)

    async with create_session(Exchange.BITFLYER) as session:
        board = await session.api.board(request)

    display_board(board, request, rows, price_band)


def display_board(
    board: Board,
    request: BoardRequest,
    rows: int,
    price_band: Decimal,
) -> None:
    # Format price_band value according to precision (e.g., 1000 → "1,000", 0.1 → "0.1")
    price_band_str = format_price(price_band, align_to=price_band)

    title = f"Order Book: {request.product_code if request.product_code else 'N/A'} (Price Band: {price_band_str} | Spread: {board.spread:,.0f})"
    display_order_book_table_with_bands(
        title, board, rows, price_band, size_precision=6
    )


if __name__ == "__main__":
    app()
