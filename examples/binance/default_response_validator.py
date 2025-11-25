#!/usr/bin/env python3
"""Sample using the default :term:`response validator`

The response validator validates API response errors and
raises appropriate exceptions.

This sample demonstrates how to obtain the exchange-specific default response validator
using :func:`~crypto_api_client.factories.create_response_validator`.

.. code-block:: console

    # Catch errors and display details
    uv run python examples/binance/default_response_validator.py --demo exception

    # Propagate errors as-is (typer traceback display)
    uv run python examples/binance/default_response_validator.py --demo callbacks

.. note::

    If you want to customize error handling (custom logging, conversion to
    business logic-specific exceptions, etc.), see
    ``examples/bitflyer/custom_response_validator.py``.

.. seealso::

    - :func:`~crypto_api_client.factories.create_response_validator`
    - :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
    - :doc:`glossary` - response validator definition
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from common.helpers import setup_logging
from rich.console import Console

from crypto_api_client import Exchange, create_session
from crypto_api_client.binance import TickerRequest
from crypto_api_client.errors.exceptions import ExchangeApiError
from crypto_api_client.factories import create_response_validator

app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=False,
)
console = Console()


@app.command()
def main(
    demo: Annotated[
        str,
        typer.Option(
            "--demo",
            help="Demo type: exception (exception handling), callbacks (callback)",
        ),
    ] = "exception",
    log_level: Annotated[
        str,
        typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    ] = "WARNING",
) -> None:
    asyncio.run(async_main(demo, log_level))


async def async_main(demo: str, log_level: str) -> None:
    setup_logging(log_level)

    console.print(
        "[bold magenta]Default Response Validator Usage Example (Binance)[/bold magenta]"
    )
    console.print("=" * 60)

    if demo == "exception":
        await demonstrate_exception_display()
    elif demo == "callbacks":
        await demonstrate_callbacks()


async def demonstrate_exception_display() -> None:
    console.print("\n[bold cyan]Public API + default response validator[/bold cyan]")
    console.print("   Generate exception with non-existent symbol and verify ExchangeApiError\n")

    validator = create_response_validator(Exchange.BINANCE)

    symbol = "INVALID_SYMBOL"

    console.print(f"   📍 Validator type: {type(validator).__name__}")
    console.print(f"   📊 Symbol: {symbol}\n")

    try:
        async with create_session(Exchange.BINANCE, callbacks=(validator,)) as session:
            request = TickerRequest(symbol=symbol)
            ticker = await session.api.ticker_24hr(request)  # pyright: ignore[reportUnusedVariable]  # noqa: F841

    except ExchangeApiError as e:
        console.print(f"   ❌ [red]error description: {e.error_description}[/red]")
        console.print(f"      [red]http status code: {e.http_status_code}[/red]")
        console.print(f"      [red]api status code 1: {e.api_status_code_1}[/red]")
        console.print(f"      [red]api error message 1: {e.api_error_message_1}[/red]")
        console.print(f"      [red]response body: {e.response_body}[/red]")


async def demonstrate_callbacks() -> None:
    console.print("\n[bold cyan]Public API + default response validator[/bold cyan]")
    console.print("   Call API with invalid symbol and verify validator behavior\n")

    validator = create_response_validator(Exchange.BINANCE)

    async with create_session(
        Exchange.BINANCE,
        callbacks=(validator,),
    ) as session:
        request = TickerRequest(symbol="INVALID_SYMBOL")
        ticker = await session.api.ticker_24hr(request)  # pyright: ignore[reportUnusedVariable]  # noqa: F841


if __name__ == "__main__":
    app()
