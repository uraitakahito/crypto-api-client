#!/usr/bin/env python3
"""Debugging example using mitmproxy

This sample demonstrates how to use a proxy with CA certificate verification.

.. code-block:: console

    # 1. Start mitmproxy (in a separate terminal)
    mitmproxy -p 8080

    # 2. Run this script
    uv run python examples/proxy/proxy_with_cert.py --proxy-url http://host.docker.internal:8080 --cert ./.mitmproxy/mitmproxy-ca-cert.pem
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
    cert: Annotated[
        str | None,
        typer.Option("--cert", help="CA certificate path"),
    ] = None,
) -> None:
    asyncio.run(async_main(proxy_url, cert))


async def async_main(proxy_url: str, cert: str | None) -> None:
    product_code = "BTC_JPY"

    print("=" * 60)
    print("Debugging HTTP traffic using mitmproxy")
    print("=" * 60)
    print(f"Proxy URL: {proxy_url}")
    print("Prerequisite: mitmproxy must be running")
    print("              Run `mitmproxy -p 8080` in a separate terminal")

    if cert:
        print(f"\n✅ Using mitmproxy CA certificate: {cert}")
        config = SessionConfig(
            proxy_url=proxy_url,
            ssl_cert_file=cert,
        )
    else:
        print("\n💡 Hint: Recommended to specify CA certificate with --cert option")
        print("   Example: --cert ./.mitmproxy/mitmproxy-ca-cert.pem")
        config = SessionConfig(
            proxy_url=proxy_url,
        )

    print("\nRunning...")
    async with create_session(Exchange.BITFLYER, session_config=config) as session:
        request = TickerRequest(product_code=product_code)
        ticker = await session.api.ticker(request)
        print(f"  BTC price: {ticker.ltp:,.0f} JPY")
        print(f"  Proxy: {session.config.proxy_url}")
        print(f"  SSL verification: {session.config.verify_ssl}")

    print("\n✅ Complete")


if __name__ == "__main__":
    app()
