#!/usr/bin/env python3
"""Sample script to check bitFlyer exchange operational status

Checks the operational status of the entire exchange or a specified currency pair.

.. code-block:: console

    # Check overall exchange status
    uv run python examples/bitflyer/health.py

    # Check exchange status for BTC_JPY pair
    uv run python examples/bitflyer/health.py --pair BTC_JPY
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import common.helpers as utils
import typer

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer import HealthRequest

app = typer.Typer(
    pretty_exceptions_enable=True,  # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False,  # Show full traceback
)


@app.command()
def main(
    pair: Annotated[
        str | None,
        typer.Option(
            "--pair",
            help="Currency pair (e.g., BTC_JPY, ETH_JPY). If omitted, checks overall exchange health.",
        ),
    ] = None,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level",
            help="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
        ),
    ] = "WARNING",
) -> None:
    utils.setup_logging(log_level)

    asyncio.run(async_main(pair))


async def async_main(pair: str | None) -> None:
    async with create_session(Exchange.BITFLYER) as session:
        request = HealthRequest(product_code=pair)
        health_status = await session.api.gethealth(request)

        typer.echo("📊 Health Check Results:")
        status_emoji = utils.get_health_status_emoji(health_status.status)
        if pair:
            typer.echo(f"{status_emoji} {pair}: {health_status.status.value}")
        else:
            typer.echo(f"{status_emoji} Overall Exchange: {health_status.status.value}")


if __name__ == "__main__":
    app()
