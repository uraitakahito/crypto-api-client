#!/usr/bin/env python3
"""Tool to inspect rate limit information stored in Redis

Inspects and visualizes rate limit information stored in Redis.
You can check request counts per URL pattern, reset times,
and limit states.

.. code-block:: console

    # Basic usage
    uv run python examples/rate_limit_inspector.py

    # Specify Redis host
    uv run python examples/rate_limit_inspector.py --redis-host localhost --redis-port 6379

    # Run in clear mode (delete all rate limit information)
    uv run python examples/rate_limit_inspector.py --clear

.. note::

    Ensure Redis is running before execution.
    Can be specified via REDIS_HOST environment variable or --redis-host option.
"""

import asyncio
import time
from datetime import datetime, timezone

import redis.asyncio as redis
import typer
from common.redis_client_factory import create_redis_client
from rich.console import Console
from rich.table import Table

from crypto_api_client.callbacks import (
    RateLimitKeyBuilder,
    RedisSharedUrlPatternRateLimiter,
)

app = typer.Typer()
console = Console()


@app.command()
def main(
    redis_host: str = typer.Option(
        None, "--redis-host", help="Redis hostname", envvar="REDIS_HOST"
    ),
    redis_port: int = typer.Option(6379, "--redis-port", help="Redis port number"),
    key_prefix: str = typer.Option(
        RedisSharedUrlPatternRateLimiter.DEFAULT_KEY_PREFIX,
        "--key-prefix",
        help="Key prefix to inspect",
    ),
    window_seconds: int = typer.Option(
        RedisSharedUrlPatternRateLimiter.DEFAULT_WINDOW_SECONDS,
        "--window-seconds",
        help="Window seconds",
    ),
) -> None:
    asyncio.run(
        async_main(
            redis_host,
            redis_port,
            key_prefix,
            window_seconds,
        )
    )


async def async_main(
    redis_host: str | None,
    redis_port: int,
    key_prefix: str,
    window_seconds: int,
) -> None:
    redis_client = create_redis_client(host=redis_host, port=redis_port)
    await run_inspection(
        redis_client,
        key_prefix,
        window_seconds,
    )


async def inspect_rate_limits(
    redis_client: redis.Redis,
    key_prefix: str = RedisSharedUrlPatternRateLimiter.DEFAULT_KEY_PREFIX,
    window_seconds: int = RedisSharedUrlPatternRateLimiter.DEFAULT_WINDOW_SECONDS,
) -> None:
    """Inspect rate limit information stored in Redis

    :param redis_client: Redis client
    :param key_prefix: Key prefix
    :param window_seconds: Window seconds
    """
    # Get all keys
    pattern = RateLimitKeyBuilder.build_search_pattern(key_prefix)
    keys: list[bytes] = await redis_client.keys(pattern)  # type: ignore[assignment]

    if not keys:
        console.print("[yellow]No rate limit keys found[/yellow]")
        return

    # Calculate current window
    current_timestamp = int(time.time())
    current_window = RateLimitKeyBuilder.get_window_for_timestamp(
        current_timestamp, window_seconds
    )

    # Create table
    table = Table(
        title="Rate Limit Status", show_header=True, header_style="bold magenta"
    )
    table.add_column("Label", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="green")
    table.add_column("Window", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Remaining", justify="right")

    # Get information for each key
    for key_bytes in sorted(keys):
        key_str = key_bytes.decode()

        # Parse key
        parsed = RateLimitKeyBuilder.parse_key(key_str)
        if not parsed:
            continue

        # Get count
        count_bytes = await redis_client.get(key_str)
        count = int(count_bytes) if count_bytes else 0

        # Determine status
        is_active = parsed["window"] == current_window
        status = "🟢 Active" if is_active else "⚪ Expired"

        # Calculate remaining time
        if is_active:
            window_end = (current_window + 1) * window_seconds
            remaining_seconds = window_end - current_timestamp
            remaining_time = f"{remaining_seconds}s"
        else:
            remaining_time = "-"

        table.add_row(
            str(parsed["label"]),
            str(count),
            str(parsed["window"]),
            status,
            remaining_time,
        )

    console.print(table)

    # Summary information
    console.print("\n📊 [bold]Summary[/bold]")
    console.print(f"  Total keys: {len(keys)}")
    console.print(f"  Current window: {current_window}")
    console.print(f"  Window size: {window_seconds}s")
    console.print(
        f"  Current time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )


async def run_inspection(
    redis_client: redis.Redis,
    key_prefix: str,
    window_seconds: int,
) -> None:
    """Run inspection

    :param redis_client: Redis client
    :param key_prefix: Key prefix
    :param window_seconds: Window seconds
    """
    try:
        # Connection test
        await redis_client.ping()  # type: ignore[misc]

        # Execute inspection
        await inspect_rate_limits(redis_client, key_prefix, window_seconds)

    except redis.ConnectionError:
        console.print("[red]Cannot connect to Redis[/red]")
        raise typer.Exit(1)
    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    app()
