#!/usr/bin/env python3
"""Sample script to fetch ticker from BINANCE

.. code-block:: console

    # Fetch ticker information for BTC/USDT pair
    uv run python examples/binance/ticker.py --pair BTCUSDT --zone Asia/Tokyo
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
from crypto_api_client.binance import Ticker, TickerRequest

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

    async with create_session(Exchange.BINANCE) as session:
        ticker = await session.api.ticker_24hr(TickerRequest(symbol=pair))
        display_ticker(ticker, zone_info)


def display_ticker(ticker: Ticker, zone_info: ZoneInfo) -> None:
    typer.echo(f"{'symbol':<{LABEL_WIDTH}}: {str(ticker.symbol)}")
    print(f"[{SELL_COLOR}]{'ask price':<{LABEL_WIDTH}}: {ticker.askPrice:,.2f}[/]")
    print(f"[{BUY_COLOR}]{'bid price':<{LABEL_WIDTH}}: {ticker.bidPrice:,.2f}[/]")

    spread = ticker.askPrice - ticker.bidPrice
    spread_pct = (spread / ticker.bidPrice) * 100 if ticker.bidPrice != 0 else 0
    typer.echo(f"{'spread':<{LABEL_WIDTH}}: {spread:,.2f} ({spread_pct:.3f}%)")

    typer.echo(f"{'last price':<{LABEL_WIDTH}}: {ticker.lastPrice:,.2f}")
    typer.echo(f"{'volume':<{LABEL_WIDTH}}: {ticker.volume:,.6f}")

    # Exchange-specific fields
    typer.echo(f"{'open price':<{LABEL_WIDTH}}: {ticker.openPrice:,.2f}")
    print(f"[{SELL_COLOR}]{'high price':<{LABEL_WIDTH}}: {ticker.highPrice:,.2f}[/]")
    print(f"[{BUY_COLOR}]{'low price':<{LABEL_WIDTH}}: {ticker.lowPrice:,.2f}[/]")
    typer.echo(f"{'trade count':<{LABEL_WIDTH}}: {ticker.count:,}")
    typer.echo(f"{'quote volume':<{LABEL_WIDTH}}: {ticker.quoteVolume:,.2f}")
    typer.echo(f"{'weighted avg':<{LABEL_WIDTH}}: {ticker.weightedAvgPrice:,.2f}")
    typer.echo(f"{'open time':<{LABEL_WIDTH}}: {ticker.openTime.astimezone(zone_info)}")
    typer.echo(
        f"{'close time':<{LABEL_WIDTH}}: {ticker.closeTime.astimezone(zone_info)}"
    )

    price_change = ticker.priceChange
    price_change_pct = ticker.priceChangePercent
    typer.echo(
        f"{'24h change':<{LABEL_WIDTH}}: {price_change:+,.2f} ({price_change_pct:+.2f}%)\n"
    )


if __name__ == "__main__":
    app()
