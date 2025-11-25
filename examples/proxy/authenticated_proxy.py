#!/usr/bin/env python3
"""Example of using proxy with authentication

This sample demonstrates how to access APIs via a proxy server that requires authentication.

.. code-block:: console

    uv run python examples/proxy/authenticated_proxy.py --proxy-url http://host.docker.internal:8080 --username myuser --password mypass
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import typer
from pydantic import SecretStr

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer.native_requests import TickerRequest
from crypto_api_client.core.session_config import SessionConfig

app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=False,
)


@app.command()
def main(
    proxy_url: Annotated[
        str,
        typer.Option("--proxy-url", help="Proxy server URL"),
    ] = "http://host.docker.internal:8080",
    username: Annotated[
        str,
        typer.Option("--username", help="Proxy authentication username"),
    ] = "",
    password: Annotated[
        str,
        typer.Option("--password", help="Proxy authentication password"),
    ] = "",
) -> None:
    username = username or os.environ.get("PROXY_USERNAME", "")
    password = password or os.environ.get("PROXY_PASSWORD", "")

    if not username or not password:
        print("Error: Authentication credentials required")
        print("  Specify --username and --password, or")
        print("  set PROXY_USERNAME and PROXY_PASSWORD environment variables")
        raise typer.Exit(1)

    asyncio.run(async_main(proxy_url, username, password))


async def async_main(proxy_url: str, username: str, password: str) -> None:
    product_code = "BTC_JPY"

    print("=" * 60)
    print("Accessing API via authenticated proxy")
    print("=" * 60)

    print("\nAuthenticated proxy configuration via SessionConfig")
    config = SessionConfig(
        proxy_url=proxy_url,
        proxy_auth=(SecretStr(username), SecretStr(password)),
        verify_ssl=False,
    )
    async with create_session(Exchange.BITFLYER, session_config=config) as session:
        request = TickerRequest(product_code=product_code)
        ticker = await session.api.ticker(request)
        print(f"  BTC price: {ticker.ltp:,.0f} JPY")
        print(f"  Proxy settings: {session.config.proxy_url}")
        print(f"  Authentication: {session.config.proxy_auth}")

    print("\n✅ Complete")


if __name__ == "__main__":
    app()
