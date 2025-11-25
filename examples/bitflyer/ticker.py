#!/usr/bin/env python3
"""Sample script to fetch and display bitFlyer ticker information

.. code-block:: console

    # Fetch ticker information for BTC/JPY pair
    uv run python examples/bitflyer/ticker.py --pair BTC_JPY --zone Asia/Tokyo

    # Fetch ticker information for ETH/JPY pair (debug mode)
    uv run python examples/bitflyer/ticker.py --pair ETH_JPY --zone Asia/Tokyo --log-level DEBUG
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

from zoneinfo import ZoneInfo

import typer
from common.display import BUY_COLOR, LABEL_WIDTH, SELL_COLOR
from common.helpers import setup_logging
from common.typer_custom_types import ZONE_INFO_TYPE
from rich import print

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer import TickerRequest
from crypto_api_client.bitflyer.native_domain_models import Ticker

app = typer.Typer(
    pretty_exceptions_enable=True,  # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False,  # Show full traceback
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
    zone_info: Annotated[
        ZoneInfo,
        typer.Option(
            "--zone", help="Timezone name like Asia/Tokyo", click_type=ZONE_INFO_TYPE
        ),
    ] = ZoneInfo("UTC"),
    log_level: Annotated[
        str,
        typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    ] = "WARNING",
) -> None:
    asyncio.run(async_main(pair, zone_info, log_level))


async def async_main(pair: str, zone_info: ZoneInfo, log_level: str) -> None:
    setup_logging(log_level)

    async with create_session(Exchange.BITFLYER) as session:
        ticker = await session.api.ticker(TickerRequest(product_code=pair))

        display_ticker(ticker, zone_info)


def display_ticker(ticker: Ticker, zone_info: ZoneInfo) -> None:
    # Basic information
    typer.echo(f"{'product code':<{LABEL_WIDTH}}: {str(ticker.product_code)}")
    print(f"[{SELL_COLOR}]{'ask price':<{LABEL_WIDTH}}: {ticker.best_ask:,.0f}[/]")
    print(f"[{BUY_COLOR}]{'bid price':<{LABEL_WIDTH}}: {ticker.best_bid:,.0f}[/]")

    spread = ticker.best_ask - ticker.best_bid
    spread_pct = (spread / ticker.best_bid) * 100 if ticker.best_bid != 0 else 0
    typer.echo(f"{'spread':<{LABEL_WIDTH}}: {spread:,.0f} ({spread_pct:.3f}%)")

    typer.echo(f"{'last price':<{LABEL_WIDTH}}: {ticker.ltp:,.0f}")
    typer.echo(f"{'volume':<{LABEL_WIDTH}}: {ticker.volume:,.6f}")

    # Exchange-specific fields
    typer.echo(f"{'volume by product':<{LABEL_WIDTH}}: {ticker.volume_by_product:,.6f}")
    print(
        f"[{BUY_COLOR}]{'best bid size':<{LABEL_WIDTH}}: {ticker.best_bid_size:,.6f}[/]"
    )
    print(
        f"[{SELL_COLOR}]{'best ask size':<{LABEL_WIDTH}}: {ticker.best_ask_size:,.6f}[/]"
    )
    print(
        f"[{BUY_COLOR}]{'total bid depth':<{LABEL_WIDTH}}: {ticker.total_bid_depth:,.6f}[/]"
    )
    print(
        f"[{SELL_COLOR}]{'total ask depth':<{LABEL_WIDTH}}: {ticker.total_ask_depth:,.6f}[/]"
    )
    typer.echo(f"{'state':<{LABEL_WIDTH}}: {ticker.state}")
    typer.echo(
        f"{'timestamp':<{LABEL_WIDTH}}: {ticker.timestamp.astimezone(zone_info)}\n"
    )


if __name__ == "__main__":
    app()
