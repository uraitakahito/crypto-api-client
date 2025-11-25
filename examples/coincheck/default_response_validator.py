#!/usr/bin/env python3
"""Sample using the default :term:`response validator`

The response validator validates API response errors and
raises appropriate exceptions.

This sample demonstrates how to obtain the exchange-specific default response validator
using :func:`~crypto_api_client.factories.create_response_validator`.

Both demos use Private API (balance). Since Coincheck API returns a 404 HTML page
for invalid currency pairs, we test with authentication errors that return JSON errors.

.. code-block:: console

    # Catch errors and display details
    uv run python examples/coincheck/default_response_validator.py --demo exception

    # Propagate errors as-is (typer traceback display)
    uv run python examples/coincheck/default_response_validator.py --demo callbacks

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
from crypto_api_client.errors.exceptions import ExchangeApiError
from crypto_api_client.factories import create_response_validator

app = typer.Typer(
    pretty_exceptions_enable=True,  # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False,  # Show full traceback
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
        "[bold magenta]Default Response Validator Usage Example (Coincheck)[/bold magenta]"
    )
    console.print("=" * 60)

    if demo == "exception":
        await demonstrate_exception_display()
    elif demo == "callbacks":
        await demonstrate_callbacks()


async def demonstrate_exception_display() -> None:
    console.print("\n[bold cyan]Private API + default response validator[/bold cyan]")
    console.print("   Fetch balance with invalid API key and catch ExchangeApiError for display\n")

    validator = create_response_validator(Exchange.COINCHECK)

    console.print(f"   📍 Validator type: {type(validator).__name__}")
    console.print("   🔑 API Key: invalid_api_key (dummy)")
    console.print("   🔐 API Secret: invalid_api_secret (dummy)\n")

    try:
        # Register validator as callback
        async with create_session(
            Exchange.COINCHECK,
            api_key="invalid_api_key",
            api_secret="invalid_api_secret",
            callbacks=(validator,),
        ) as session:
            balances = await session.api.balance()  # pyright: ignore[reportUnusedVariable]  # noqa: F841
            # Skip processing on success

    except ExchangeApiError as e:
        console.print(f"   ❌ [red]error description: {e.error_description}[/red]")
        console.print(f"      [red]http status code: {e.http_status_code}[/red]")
        console.print(f"      [red]api status code 1: {e.api_status_code_1}[/red]")
        console.print(f"      [red]api error message 1: {e.api_error_message_1}[/red]")
        console.print(f"      [red]response body: {e.response_body}[/red]")


async def demonstrate_callbacks() -> None:
    console.print("\n[bold cyan]Private API + default response validator[/bold cyan]")
    console.print("   Intentionally fail authentication on API that requires authentication and verify validator behavior\n")

    validator = create_response_validator(Exchange.COINCHECK)

    async with create_session(
        Exchange.COINCHECK,
        api_key="dummy_api_key",
        api_secret="dummy_api_secret",
        callbacks=(validator,),
    ) as session:
        balances = await session.api.balance()  # pyright: ignore[reportUnusedVariable] # noqa: F841
        # Skip processing on success


if __name__ == "__main__":
    app()
