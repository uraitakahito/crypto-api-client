#!/usr/bin/env python3
"""Sample script to send new orders to bitFlyer

Sends new orders to bitFlyer with specified conditions.
Supports both LIMIT (limit order) and MARKET (market order).
Dry-run mode allows operation verification without actually sending orders.

.. code-block:: console

    # Dry run (does not actually place orders)
    uv run python examples/bitflyer/sendchildorder.py --product-code BTC_JPY --child-order-type LIMIT --side SELL --size 0.001 --price 17525000 --dry-run

.. warning::

    This script actually places orders.
    Exercise caution when not using the --dry-run option.
"""

import asyncio
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from common.helpers import get_key_and_secret, setup_logging
from common.typer_custom_types import (
    POSITIVE_DECIMAL_TYPE,
    PRICE_DECIMAL_TYPE,
)

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer import (
    ChildOrderType,
    SendChildOrderRequest,
    Side,
    TimeInForce,
)

# Unified settings for development environment
app = typer.Typer(
    pretty_exceptions_enable=True,  # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False,  # Show full traceback
)


@app.command()
def main(
    product_code: Annotated[
        str,
        typer.Option(
            "--product-code",
            help="Currency pair (e.g., BTC_JPY, ETH_JPY)",
        ),
    ],
    side: Annotated[
        Side,
        typer.Option("--side", help="Side (BUY or SELL)", case_sensitive=False),
    ],
    size: Annotated[
        Decimal,
        typer.Option("--size", help="Order size", click_type=POSITIVE_DECIMAL_TYPE),
    ],
    child_order_type: Annotated[
        ChildOrderType,
        typer.Option(
            "--child-order-type",
            help="Child order type (LIMIT or MARKET)",
            case_sensitive=False,
        ),
    ] = ChildOrderType.LIMIT,
    price: Annotated[
        Decimal | None,
        typer.Option(
            "--price",
            help="Order price (required for LIMIT orders)",
            click_type=PRICE_DECIMAL_TYPE,
        ),
    ] = None,
    minute_to_expire: Annotated[
        int | None,
        typer.Option(
            "--minute-to-expire",
            help="Minute to expire (default: 43200 = 30 days)",
        ),
    ] = None,
    time_in_force: Annotated[
        TimeInForce,
        typer.Option(
            "--time-in-force",
            help="Time in force (GTC, IOC, or FOK)",
            case_sensitive=False,
        ),
    ] = TimeInForce.GTC,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level",
            "-l",
            help="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
        ),
    ] = "WARNING",
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Dry run mode (display order details without sending)",
        ),
    ] = False,
) -> None:
    """Send a new order to bitFlyer asynchronously."""
    asyncio.run(
        async_main(
            product_code,
            child_order_type,
            side,
            size,
            price,
            minute_to_expire,
            time_in_force,
            log_level,
            dry_run,
        )
    )


async def async_main(
    product_code: str,
    child_order_type: ChildOrderType,
    side: Side,
    size: Decimal,
    price: Decimal | None,
    minute_to_expire: int | None,
    time_in_force: TimeInForce,
    log_level: str,
    dry_run: bool,
) -> None:
    setup_logging(log_level)

    # Workaround:
    # launch.json args cannot expand environment variables,
    # so explicitly get environment variable here for convenience during development
    if price is None and os.environ.get("PRICE"):
        price = Decimal(os.environ["PRICE"])

    # Price is required for LIMIT orders
    if child_order_type == ChildOrderType.LIMIT and not price:
        typer.echo("❌ Error: Price (--price) is required for LIMIT orders")
        raise typer.Exit(1)

    # Get API keys
    api_key, api_secret = get_key_and_secret("bitflyer")

    # Create request object
    request_type = SendChildOrderRequest(
        product_code=product_code,
        child_order_type=child_order_type,
        side=side,
        size=size,
        price=price,
        minute_to_expire=minute_to_expire,
        time_in_force=time_in_force,
    )

    # Display order details
    typer.echo("\n📋 Order details:")
    typer.echo("-" * 50)
    typer.echo(f"Currency pair: {product_code}")
    typer.echo(f"Order type: {child_order_type.value}")
    typer.echo(f"Side: {side.value}")
    typer.echo(f"Size: {size} BTC")
    if price:
        typer.echo(f"Price: ¥{int(price):,}")
        typer.echo(f"Estimated amount: ¥{int(price * size):,}")
    else:
        typer.echo("Price: Market")
    if minute_to_expire:
        typer.echo(
            f"Expiration: {minute_to_expire} minutes ({minute_to_expire / 60 / 24:.1f} days)"
        )
    typer.echo(f"Time in force: {time_in_force.value}")
    typer.echo("-" * 50)

    if dry_run:
        typer.echo("\n⚠️  Dry run mode: Actual order will not be sent")
        typer.echo("✅ Order details verified")
        return

    try:
        typer.echo("\n📡 Sending order...")

        # Send order using Session
        async with create_session(
            Exchange.BITFLYER,
            api_key=api_key,
            api_secret=api_secret,
        ) as session:
            result = await session.api.sendchildorder(request_type)

            typer.echo("\n✅ Order sent successfully!")
            typer.echo(f"📝 Order acceptance ID: {result}")
            typer.echo(
                "\n💡 Hint: To check order status, use getchildorders.py"
            )

    except Exception as e:
        typer.echo(f"\n❌ An error occurred: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()  # Typer automatically catches and displays exceptions beautifully
