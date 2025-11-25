#!/usr/bin/env python
"""Example of customizing request settings using SessionConfig

Demonstrates how to customize settings such as timeout, retry,
and HTTP/2 using SessionConfig.

Usage:
    uv run python examples/session_config_demo.py
    uv run python examples/session_config_demo.py --verbose
"""

import asyncio
import logging
import sys

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer.native_requests import TickerRequest
from crypto_api_client.core.session_config import SessionConfig

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def demo_custom_config() -> None:
    """Example session usage with custom configuration."""
    logger.info("=== SessionConfig Custom Configuration Demo ===\n")

    product_code = "BTC_JPY"

    logger.info("Fast response-oriented configuration:")
    fast_config = SessionConfig(
        request_timeout_seconds=3,
        request_max_retries=1,
        request_initial_delay_seconds=0.5,
        request_backoff_factor=1.5,
        request_jitter=False,
    )

    async with create_session(Exchange.BITFLYER, session_config=fast_config) as session:
        logger.info(f"  Timeout: {fast_config.request_timeout_seconds} seconds")
        logger.info(f"  Max retries: {fast_config.request_max_retries}")

        request = TickerRequest(product_code=product_code)
        ticker = await session.api.ticker(request)
        logger.info(f"  BTC price: {ticker.ltp:,.0f} JPY\n")


def main():
    if "--verbose" in sys.argv or "-v" in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)

    asyncio.run(demo_custom_config())


if __name__ == "__main__":
    main()
