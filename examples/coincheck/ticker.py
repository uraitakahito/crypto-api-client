#!/usr/bin/env python3
"""Sample script to fetch ticker from Coincheck

.. code-block:: console

    # Fetch ticker information for BTC/JPY pair
    uv run python examples/coincheck/ticker.py --pair btc_jpy --zone Asia/Tokyo
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

from rich import print

sys.path.insert(0, str(Path(__file__).parent.parent))

from zoneinfo import ZoneInfo

import typer
from common.display import BUY_COLOR, LABEL_WIDTH, SELL_COLOR
from common.helpers import setup_logging
from common.typer_custom_types import ZONE_INFO_TYPE

from crypto_api_client import Exchange, create_session
from crypto_api_client.coincheck import TickerRequest
from crypto_api_client.coincheck.native_domain_models import Ticker

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

    async with create_session(Exchange.COINCHECK) as session:
        ticker = await session.api.ticker(TickerRequest(pair=pair))

        display_ticker(ticker, pair, zone_info)


def display_ticker(ticker: Ticker, pair: str, zone_info: ZoneInfo) -> None:
    # Basic information
    typer.echo(f"{'pair':<{LABEL_WIDTH}}: {pair}")
    print(f"[{SELL_COLOR}]{'ask':<{LABEL_WIDTH}}: {ticker.ask:,.0f}[/]")
    print(f"[{BUY_COLOR}]{'bid':<{LABEL_WIDTH}}: {ticker.bid:,.0f}[/]")

    spread = ticker.ask - ticker.bid
    spread_pct = (spread / ticker.bid) * 100 if ticker.bid != 0 else 0
    typer.echo(f"{'spread':<{LABEL_WIDTH}}: {spread:,.0f} ({spread_pct:.3f}%)")

    typer.echo(f"{'last':<{LABEL_WIDTH}}: {ticker.last:,.0f}")
    typer.echo(f"{'volume':<{LABEL_WIDTH}}: {ticker.volume:,.4f}")

    # Exchange-specific fields
    print(f"[{SELL_COLOR}]{'high':<{LABEL_WIDTH}}: {ticker.high:,.0f}[/]")
    print(f"[{BUY_COLOR}]{'low':<{LABEL_WIDTH}}: {ticker.low:,.0f}[/]")
    typer.echo(
        f"{'timestamp':<{LABEL_WIDTH}}: {ticker.timestamp.astimezone(zone_info)}"
    )

    price_range = ticker.high - ticker.low
    price_range_pct = (price_range / ticker.low) * 100 if ticker.low != 0 else 0
    typer.echo(
        f"{'price range':<{LABEL_WIDTH}}: {price_range:,.0f} ({price_range_pct:.2f}%)\n"
    )


if __name__ == "__main__":
    app()
