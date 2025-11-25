#!/usr/bin/env python3
"""Example of loading proxy settings from environment variables

.. note::

    Automatic environment variable loading is an httpx feature.
    When trust_env=True, httpx automatically loads these environment variables:
    - HTTP_PROXY: Proxy for HTTP requests
    - HTTPS_PROXY: Proxy for HTTPS requests
    - ALL_PROXY: Common proxy for all requests
    - NO_PROXY: List of hosts that bypass proxy

    Details: https://www.python-httpx.org/environment_variables/

Usage::

    # Default (ignore environment variables)
    uv run python examples/proxy/env_proxy.py

    # Load proxy settings from environment variables
    SSL_CERT_FILE=/app/.mitmproxy/mitmproxy-ca-cert.pem HTTP_PROXY=http://host.docker.internal:8080 HTTPS_PROXY=http://host.docker.internal:8080 uv run python examples/proxy/env_proxy.py --trust-env

About trust_env:
    - Default: False (ignore environment variables)
    - Set to True to respect environment variables
"""

import asyncio
import os
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
    trust_env: Annotated[
        bool,
        typer.Option("--trust-env", help="Load proxy settings from environment variables"),
    ] = False,
) -> None:
    asyncio.run(async_main(trust_env=trust_env))


async def async_main(trust_env: bool) -> None:
    product_code = "BTC_JPY"

    print("=" * 60)
    print("Loading proxy settings from environment variables")
    print("=" * 60)
    print(f"HTTP_PROXY  = {os.environ.get('HTTP_PROXY', 'Not set')}")
    print(f"HTTPS_PROXY = {os.environ.get('HTTPS_PROXY', 'Not set')}")
    print(f"trust_env   = {trust_env}")

    if trust_env:
        print("\n✅ trust_env=True: Environment variables will be used automatically")
        # Explicitly specify trust_env=True
        # httpx automatically loads HTTP_PROXY/HTTPS_PROXY environment variables internally
        config = SessionConfig(trust_env=True)
        async with create_session(Exchange.BITFLYER, session_config=config) as session:
            request = TickerRequest(product_code=product_code)
            ticker = await session.api.ticker(request)
            print(f"  BTC price: {ticker.ltp:,.0f} JPY")
            print(f"  trust_env: {session.config.trust_env}")

    else:
        print("\n❌ trust_env=False (default): Environment variables are ignored")
        # Default is trust_env=False even without explicitly specifying SessionConfig
        async with create_session(Exchange.BITFLYER) as session:
            request = TickerRequest(product_code=product_code)
            ticker = await session.api.ticker(request)
            print(f"  BTC price: {ticker.ltp:,.0f} JPY")
            print(f"  trust_env: {session.config.trust_env}")

    print("\n✅ Complete")
    print(
        "\n💡 Hint: When trust_env=True, "
        "httpx automatically loads HTTP_PROXY/HTTPS_PROXY environment variables."
        "\nDefault is False (ignore environment variables)."
    )


if __name__ == "__main__":
    app()
