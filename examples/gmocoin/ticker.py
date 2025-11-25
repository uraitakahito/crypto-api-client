#!/usr/bin/env python3
"""Sample script to fetch ticker from GMO Coin

.. code-block:: console

    # Fetch ticker information for BTC/JPY pair
    uv run python examples/gmocoin/ticker.py --pair BTC_JPY --zone Asia/Tokyo

    # Fetch ticker information for ETH/JPY pair (debug mode)
    uv run python examples/gmocoin/ticker.py --pair ETH_JPY --zone Asia/Tokyo --log-level DEBUG
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich import print

sys.path.insert(0, str(Path(__file__).parent.parent))

from zoneinfo import ZoneInfo

from common.display import BUY_COLOR, LABEL_WIDTH, SELL_COLOR
from common.helpers import setup_logging
from common.typer_custom_types import ZONE_INFO_TYPE

from crypto_api_client import Exchange, create_session
from crypto_api_client.gmocoin import TickerRequest
from crypto_api_client.gmocoin.native_domain_models import Ticker

# Unified settings for development environment
app = typer.Typer(
    pretty_exceptions_enable=True,      # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False        # Show full traceback
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

    async with create_session(Exchange.GMOCOIN) as session:
        tickers = await session.api.ticker(TickerRequest(symbol=pair))
        ticker = tickers[0]  # GMO Coin returns an array, so get the first element

        display_ticker(ticker, zone_info)


def display_ticker(ticker: Ticker, zone_info: ZoneInfo) -> None:
    # Basic information
    typer.echo(f"{'symbol':<{LABEL_WIDTH}}: {str(ticker.symbol)}")
    print(f"[{SELL_COLOR}]{'ask price':<{LABEL_WIDTH}}: {ticker.ask:,.0f}[/]")
    print(f"[{BUY_COLOR}]{'bid price':<{LABEL_WIDTH}}: {ticker.bid:,.0f}[/]")

    # Subtraction between Decimal values
    spread = ticker.ask - ticker.bid
    spread_pct = (spread / ticker.bid) * 100 if ticker.bid != 0 else 0
    typer.echo(f"{'spread':<{LABEL_WIDTH}}: {spread:,.0f} ({spread_pct:.3f}%)")

    typer.echo(f"{'last price':<{LABEL_WIDTH}}: {ticker.last:,.0f}")
    typer.echo(f"{'volume':<{LABEL_WIDTH}}: {ticker.volume:,.6f}")

    # Exchange-specific fields
    print(f"[{SELL_COLOR}]{'high price':<{LABEL_WIDTH}}: {ticker.high:,.0f}[/]")
    print(f"[{BUY_COLOR}]{'low price':<{LABEL_WIDTH}}: {ticker.low:,.0f}[/]")
    typer.echo(
        f"{'timestamp':<{LABEL_WIDTH}}: {ticker.timestamp.astimezone(zone_info)}"
    )

    # Calculate 24-hour price fluctuation (estimated from low and high since previous close is unavailable)
    # Subtraction between Decimal values
    price_range = ticker.high - ticker.low
    price_range_pct = (price_range / ticker.low) * 100 if ticker.low != 0 else 0
    typer.echo(
        f"{'price range':<{LABEL_WIDTH}}: {price_range:,.0f} ({price_range_pct:.2f}%)\n"
    )


if __name__ == "__main__":
    app()  # Typer automatically catches and displays exceptions beautifully
