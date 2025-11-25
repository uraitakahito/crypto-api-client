#!/usr/bin/env python3
"""Sample script to cancel bitFlyer orders

Cancels a bitFlyer order with the specified order ID.
Order IDs can be checked using the getchildorders command.

.. code-block:: console

    # Cancel by specifying order ID
    uv run python examples/bitflyer/cancelchildorder.py --pair BTC_JPY JRF20250525-012345-001234

.. warning::

    This script actually cancels orders.
    Be careful not to enter the wrong order ID.
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from common.helpers import get_key_and_secret, setup_logging

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer import (
    CancelChildOrderRequest,
)

app = typer.Typer(
    pretty_exceptions_enable=True,  # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False,  # Show full traceback
)


@app.command()
def main(
    child_order_id: Annotated[str, typer.Argument(help="Child order acceptance ID")],
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
            "--log-level", help="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
        ),
    ] = "WARNING",
) -> None:
    asyncio.run(async_main(pair, child_order_id, log_level))


async def async_main(pair: str, child_order_id: str, log_level: str) -> None:
    setup_logging(log_level)

    api_key, api_secret = get_key_and_secret("bitflyer")

    request_type = CancelChildOrderRequest(
        product_code=pair,
        child_order_acceptance_id=child_order_id,
    )

    typer.echo(f"Currency pair: {pair}")
    typer.echo(f"Order acceptance ID: {child_order_id}")

    try:
        typer.echo("\n📡 Sending cancel request...")

        async with create_session(
            Exchange.BITFLYER,
            api_key=api_key,
            api_secret=api_secret,
        ) as session:
            result = await session.api.cancelchildorder(request_type=request_type)

            # Cancel may fail without indication
            typer.echo("\n✅ Cancel request has been sent")
            typer.echo(result)

            typer.echo(
                "\n💡 Hint: To check order status, use the following command:"
            )
            # Extract base and quote from pair for the hint
            # The pair already contains the unified information
            # We need to get the original currencies from the registry
            typer.echo(
                "   uv run python examples/bitflyer/getchildorders.py --pair BTC_JPY"
            )

    except Exception as e:
        typer.echo(f"\n❌ An error occurred: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()  # Typer automatically catches and displays exceptions beautifully
