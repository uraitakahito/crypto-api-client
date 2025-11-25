#!/usr/bin/env python3
"""This sample demonstrates how to access bitFlyer's public API via a proxy server.

.. code-block:: console

    uv run python examples/proxy/basic_proxy.py --proxy-url http://host.docker.internal:8080

Prerequisites:
    - Proxy server must be running at http://host.docker.internal:8080
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import typer

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
) -> None:
    asyncio.run(async_main(proxy_url))


async def async_main(proxy_url: str) -> None:
    product_code = "BTC_JPY"

    print("=" * 60)
    print("Access API via proxy")
    print("=" * 60)
    print()

    print("Proxy configuration via SessionConfig")
    config = SessionConfig(
        proxy_url=proxy_url,
        verify_ssl=False,
    )
    async with create_session(Exchange.BITFLYER, session_config=config) as session:
        request = TickerRequest(product_code=product_code)
        ticker = await session.api.ticker(request)
        print(f"  BTC price: {ticker.ltp:,.0f} JPY")
        print(f"  Proxy settings: {session.config.proxy_url}")
        print(f"  SSL verification: {session.config.verify_ssl}")

    print("\n✅ Complete")


if __name__ == "__main__":
    app()
