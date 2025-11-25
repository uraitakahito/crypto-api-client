#!/usr/bin/env python3
"""Sample script to fetch Ticker from Upbit

.. code-block:: console

    # Fetch ticker information for ETH/KRW pair
    uv run python examples/upbit/ticker.py --markets KRW-ETH --zone Asia/Seoul
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated
from zoneinfo import ZoneInfo

import typer
from rich import print

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.display import BUY_COLOR, LABEL_WIDTH, SELL_COLOR
from common.helpers import setup_logging
from common.typer_custom_types import ZONE_INFO_TYPE

from crypto_api_client import Exchange, create_session
from crypto_api_client.upbit import TickerRequest
from crypto_api_client.upbit.native_domain_models import Ticker

app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=False,
)


@app.command()
def main(
    markets: Annotated[
        str,
        typer.Option(
            "--markets",
            help="Market code (e.g., KRW-BTC, KRW-ETH)",
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
    asyncio.run(async_main(markets, zone_info, log_level))


async def async_main(markets: str, zone_info: ZoneInfo, log_level: str) -> None:
    setup_logging(log_level)

    async with create_session(Exchange.UPBIT) as session:
        tickers = await session.api.ticker(TickerRequest(markets=markets))

        # Upbit API always returns an array, so get the first element
        ticker = tickers[0]
        display_ticker(ticker, zone_info)


def display_ticker(ticker: Ticker, zone_info: ZoneInfo) -> None:
    typer.echo(f"{'market':<{LABEL_WIDTH}}: {str(ticker.market)}")

    # Upbit doesn't have direct ask/bid, so display current price
    print(
        f"[{SELL_COLOR}]{'current price':<{LABEL_WIDTH}}: {ticker.trade_price:,.0f}[/]"
    )
    typer.echo(f"{'opening price':<{LABEL_WIDTH}}: {ticker.opening_price:,.0f}")
    print(f"[{SELL_COLOR}]{'high price':<{LABEL_WIDTH}}: {ticker.high_price:,.0f}[/]")
    print(f"[{BUY_COLOR}]{'low price':<{LABEL_WIDTH}}: {ticker.low_price:,.0f}[/]")
    typer.echo(f"{'prev closing':<{LABEL_WIDTH}}: {ticker.prev_closing_price:,.0f}")

    change_symbol = (
        "▲"
        if ticker.change.value == "RISE"
        else ("▼" if ticker.change.value == "FALL" else "=")
    )
    change_color = (
        SELL_COLOR
        if ticker.change.value == "RISE"
        else (BUY_COLOR if ticker.change.value == "FALL" else "white")
    )
    print(
        f"[{change_color}]{'change':<{LABEL_WIDTH}}: {change_symbol} {ticker.change.value}[/]"
    )
    print(
        f"[{change_color}]{'change price':<{LABEL_WIDTH}}: {ticker.signed_change_price:+,.0f} "
        f"({ticker.signed_change_rate * 100:+.2f}%)[/]"
    )

    typer.echo(f"{'trade volume':<{LABEL_WIDTH}}: {ticker.trade_volume:,.6f}")
    typer.echo(
        f"{'acc trade price':<{LABEL_WIDTH}}: {ticker.acc_trade_price:,.0f} (24h: {ticker.acc_trade_price_24h:,.0f})"
    )
    typer.echo(
        f"{'acc trade volume':<{LABEL_WIDTH}}: {ticker.acc_trade_volume:,.4f} (24h: {ticker.acc_trade_volume_24h:,.4f})"
    )

    typer.echo(
        f"{'52w high':<{LABEL_WIDTH}}: {ticker.highest_52_week_price:,.0f} ({ticker.highest_52_week_date})"
    )
    typer.echo(
        f"{'52w low':<{LABEL_WIDTH}}: {ticker.lowest_52_week_price:,.0f} ({ticker.lowest_52_week_date})"
    )

    typer.echo(
        f"{'trade timestamp':<{LABEL_WIDTH}}: {ticker.trade_timestamp.astimezone(zone_info)}"
    )
    typer.echo(
        f"{'timestamp':<{LABEL_WIDTH}}: {ticker.timestamp.astimezone(zone_info)}\n"
    )


if __name__ == "__main__":
    app()
