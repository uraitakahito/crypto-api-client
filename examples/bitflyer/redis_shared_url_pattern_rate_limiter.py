#!/usr/bin/env python3
"""Sample implementing rate limiting per URL pattern using Redis.

Can share rate limit information across multiple processes.

.. code-block:: console

    # Test with strict ticker rate limit
    uv run python examples/bitflyer/redis_shared_url_pattern_rate_limiter.py \\
        --pair BTC_JPY \\
        --window-seconds 300 \\
        --max-safe-count-ticker 5

    # Test with strict general rate limit
    uv run python examples/bitflyer/redis_shared_url_pattern_rate_limiter.py \\
        --pair BTC_JPY \\
        --window-seconds 300 \\
        --max-safe-count-general 1

.. note::

    Make sure Redis is running before execution.
    Can be specified via REDIS_HOST environment variable or --redis-host option.
"""

import asyncio
import re
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import redis.asyncio
import typer
from common.helpers import filter_callbacks_by_type, setup_logging
from common.redis_client_factory import create_redis_client

from crypto_api_client import Exchange, callbacks, create_session
from crypto_api_client.bitflyer import TickerRequest
from crypto_api_client.bitflyer.exchange_api_client import (
    ExchangeApiClient as BitFlyerApiClient,
)
from crypto_api_client.core.exchange_session import ExchangeSession
from crypto_api_client.errors import RateLimitApproachingError
from crypto_api_client.factories import create_response_validator

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
            help="Currency pair (e.g., BTC_JPY, ETH_JPY)",
        ),
    ] = "BTC_JPY",
    window_seconds: Annotated[
        int,
        typer.Option(
            "--window-seconds",
            help="Rate limit window (seconds)",
        ),
    ] = 300,
    max_safe_count_general: Annotated[
        int,
        typer.Option(
            "--max-safe-count-general",
            help="Maximum requests within window for general limit",
        ),
    ] = 100,
    max_safe_count_ticker: Annotated[
        int,
        typer.Option(
            "--max-safe-count-ticker",
            help="Maximum requests for ticker-specific limit (60 second window)",
        ),
    ] = 100,
    max_safe_count_markets: Annotated[
        int,
        typer.Option(
            "--max-safe-count-markets",
            help="Maximum requests within window for market info limit",
        ),
    ] = 100,
    redis_host: Annotated[
        str | None,
        typer.Option("--redis-host", help="Redis hostname"),
    ] = None,
    redis_port: Annotated[
        int,
        typer.Option("--redis-port", help="Redis port number"),
    ] = 6379,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level", help="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
        ),
    ] = "WARNING",
) -> None:
    asyncio.run(
        async_main(
            pair,
            window_seconds,
            max_safe_count_general,
            max_safe_count_ticker,
            max_safe_count_markets,
            redis_host,
            redis_port,
            log_level,
        )
    )


async def async_main(
    pair: str,
    window_seconds: int,
    max_safe_count_general: int,
    max_safe_count_ticker: int,
    max_safe_count_markets: int,
    redis_host: str | None,
    redis_port: int,
    log_level: str,
) -> None:
    setup_logging(log_level)

    redis_client = create_redis_client(
        host=redis_host,
        port=redis_port,
        decode_responses=False,
        socket_keepalive=True,
        socket_timeout=5,
    )

    limiters = await create_rate_limiters(
        redis_client,
        window_seconds,
        max_safe_count_general,
        max_safe_count_ticker,
        max_safe_count_markets,
    )

    async with create_session(Exchange.BITFLYER, callbacks=limiters) as session:
        await test_ticker_requests(session, pair)
        await test_markets_request(session)
        display_limiter_status(session.callbacks)


async def create_rate_limiters(
    redis_client: redis.asyncio.Redis,
    window_seconds: int,
    max_safe_count_general: int,
    max_safe_count_ticker: int,
    max_safe_count_markets: int,
) -> tuple[callbacks.AbstractRequestCallback, ...]:
    key_prefix = "RATE_LIMIT:EXAMPLES"

    general_limiter = await callbacks.RedisSharedUrlPatternRateLimiter.create(
        redis_client=redis_client,
        url_patterns=[re.compile(r".*")],
        window_seconds=window_seconds,
        max_safe_count=max_safe_count_general,
        label="GENERAL",
        key_prefix=key_prefix,
    )

    ticker_limiter = await callbacks.RedisSharedUrlPatternRateLimiter.create(
        redis_client=redis_client,
        url_patterns=["v1/ticker"],
        window_seconds=window_seconds,
        max_safe_count=max_safe_count_ticker,
        label="TICKER_STRICT",
        key_prefix=key_prefix,
    )

    markets_limiter = await callbacks.RedisSharedUrlPatternRateLimiter.create(
        redis_client=redis_client,
        url_patterns=[
            re.compile(r"v1/markets.*"),
            re.compile(r"v1/getmarkets"),
        ],
        window_seconds=window_seconds,
        max_safe_count=max_safe_count_markets,
        label="MARKETS",
        key_prefix=key_prefix,
    )

    response_validator = create_response_validator(Exchange.BITFLYER)

    return (
        response_validator,
        general_limiter,
        ticker_limiter,
        markets_limiter,
    )


async def test_ticker_requests(
    session: ExchangeSession[BitFlyerApiClient],
    product_code: str,
) -> None:
    typer.echo("1️⃣ Ticker information fetch test:")
    for i in range(3):
        try:
            ticker_request = TickerRequest(product_code=product_code)
            ticker = await session.api.ticker(ticker_request)
            typer.echo(f"   ✅ Attempt {i + 1}: Success - BTC price: {ticker.best_bid:,.0f} yen")
        except RateLimitApproachingError as e:
            typer.echo(f"   ❌ Attempt {i + 1}: Rate limit - {e}")


async def test_markets_request(session: ExchangeSession[BitFlyerApiClient]) -> None:
    typer.echo("\n2️⃣ Market information fetch test:")
    try:
        markets = await session.api.markets()
        typer.echo(f"   ✅ Fetch success: {len(markets)} markets")
    except RateLimitApproachingError as e:
        typer.echo(f"   ❌ Rate limit: {e}")


def display_limiter_status(
    limiters: list[callbacks.AbstractRequestCallback]
    | tuple[callbacks.AbstractRequestCallback, ...],
) -> None:
    rate_limiters = filter_callbacks_by_type(
        limiters, callbacks.RedisSharedUrlPatternRateLimiter
    )

    general_limiter, ticker_limiter, markets_limiter = rate_limiters
    typer.echo("\n📊 Rate limiter status:")
    typer.echo(f"all    : {general_limiter}")
    typer.echo(f"ticker : {ticker_limiter}")
    typer.echo(f"markets: {markets_limiter}")


if __name__ == "__main__":
    app()
