#!/usr/bin/env python3
"""bitbank new order submission sample.

.. code-block:: console

    uv run python examples/bitbank/create_order.py --pair btc_jpy --side sell --type limit --amount 0.0001 --price 17000000 --dry-run
"""

import asyncio
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
from pydantic import SecretStr

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitbank import (
    CreateOrderRequest,
    Order,
)
from crypto_api_client.bitbank.native_domain_models import (
    OrderType as BitbankOrderType,
)
from crypto_api_client.bitbank.native_domain_models import (
    Side as BitbankSide,
)

# Unified settings for development environment
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
            help="Currency pair (e.g., btc_jpy, eth_jpy)",
        ),
    ],
    side: Annotated[BitbankSide, typer.Option("--side", case_sensitive=False)],
    type_: Annotated[
        BitbankOrderType | None, typer.Option("--type", case_sensitive=False)
    ] = None,
    amount: Annotated[
        Decimal | None, typer.Option("--amount", click_type=POSITIVE_DECIMAL_TYPE)
    ] = None,
    price: Annotated[
        Decimal | None, typer.Option("--price", click_type=PRICE_DECIMAL_TYPE)
    ] = None,
    trigger_price: Annotated[
        Decimal | None, typer.Option("--trigger-price", click_type=PRICE_DECIMAL_TYPE)
    ] = None,
    post_only: Annotated[bool, typer.Option("--post-only")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    log_level: Annotated[str, typer.Option("--log-level", "-l")] = "WARNING",
) -> None:
    asyncio.run(
        async_main(
            pair,
            type_,
            side,
            amount,
            price,
            trigger_price,
            post_only,
            dry_run,
            log_level,
        )
    )


async def async_main(
    pair: str,
    type_: BitbankOrderType | None,
    side: BitbankSide,
    amount: Decimal | None,
    price: Decimal | None,
    trigger_price: Decimal | None,
    post_only: bool,
    dry_run: bool,
    log_level: str,
) -> None:
    setup_logging(log_level)

    if type_ is None:
        type_ = BitbankOrderType.LIMIT

    api_key, api_secret = get_key_and_secret("bitbank")

    request = build_create_order_request(
        pair, type_, side, amount, price, trigger_price, post_only
    )

    display_order_details(pair, type_, side, amount, price, trigger_price, post_only)

    if dry_run:
        typer.echo("\n✅ Dry run mode: Actual order will not be sent")
        return

    try:
        order = await send_order(request, api_key, api_secret)
        display_order_result(order)
    except Exception as e:
        typer.echo(f"\n❌ Error: {e}", err=True)
        raise typer.Exit(1)


def build_create_order_request(
    pair: str,
    type_: BitbankOrderType,
    side: BitbankSide,
    amount: Decimal | None,
    price: Decimal | None,
    trigger_price: Decimal | None,
    post_only: bool,
) -> CreateOrderRequest:
    return CreateOrderRequest(
        pair=pair,
        side=side,
        type=type_,
        amount=amount,
        price=price,
        trigger_price=trigger_price,
        post_only=post_only if type_ == BitbankOrderType.LIMIT else None,
    )


def display_order_details(
    pair: str,
    type_: BitbankOrderType,
    side: BitbankSide,
    amount: Decimal | None,
    price: Decimal | None,
    trigger_price: Decimal | None,
    post_only: bool,
) -> None:
    """Display order details.

    :param pair: Currency pair
    :param type_: Order type
    :param side: Buy/sell side
    :param amount: Order amount
    :param price: Limit price
    :param trigger_price: Trigger price
    :param post_only: Post-only flag
    """
    typer.echo("\n📋 Order details:")
    typer.echo("-" * 50)
    typer.echo(f"Currency pair: {pair}")
    typer.echo(f"Side: {side.value}")
    typer.echo(f"Type: {type_.value}")
    if amount:
        typer.echo(f"Amount: {amount}")
    if price:
        typer.echo(f"Price: {price}")
    if trigger_price:
        typer.echo(f"Trigger price: {trigger_price}")
    if post_only and type_ == BitbankOrderType.LIMIT:
        typer.echo(f"Post-only: {post_only}")


def display_order_result(order: Order) -> None:
    """Display order result.

    :param order: Order result object
    """
    typer.echo("\n✅ Order sent successfully!")
    typer.echo(f"Order ID: {order.order_id}")
    typer.echo(f"Status: {order.status.value}")
    typer.echo(f"Order time: {order.ordered_at}")

    # Display price information
    if order.price:
        typer.echo(f"Order price: {order.price}")
    if order.amount:
        typer.echo(f"Order amount: {order.amount}")
    if order.executed_amount:
        typer.echo(f"Executed amount: {order.executed_amount}")
    if order.average_price:
        typer.echo(f"Average execution price: {order.average_price}")


async def send_order(
    request: CreateOrderRequest, api_key: SecretStr, api_secret: SecretStr
) -> Order:
    """Send order.

    :param request: Order request
    :param api_key: API key
    :param api_secret: API secret
    :return: Order result
    :raises Exception: Order sending error
    """
    async with create_session(
        Exchange.BITBANK, api_key=api_key, api_secret=api_secret
    ) as session:
        return await session.api.create_order(request)


if __name__ == "__main__":
    app()  # Typer automatically catches and displays exceptions beautifully
