#!/usr/bin/env python3
"""Sample script to check bitFlyer order book status

Checks the operational status of the order book for a specified currency pair.

.. code-block:: console

    uv run python examples/bitflyer/board_state.py --pair BTC_JPY
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import common.helpers as utils
import typer

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer import BoardStateRequest

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


async def async_main(pair: str) -> None:
    async with create_session(Exchange.BITFLYER) as session:
        request = BoardStateRequest(product_code=pair)
        board_state = await session.api.getboardstate(request)

        typer.echo("📋 Board Status:")
        health_emoji = utils.get_health_status_emoji(board_state.health)
        state_emoji = utils.get_board_state_emoji(board_state.state)
        typer.echo(f"{health_emoji} Health: {board_state.health.value}")
        typer.echo(f"{state_emoji} Operational State: {board_state.state.value}")


if __name__ == "__main__":
    app()
