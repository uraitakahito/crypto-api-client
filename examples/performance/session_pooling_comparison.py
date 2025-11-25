#!/usr/bin/env python3
"""Performance comparison test for shared HTTP client

Measures the performance difference between using a shared HTTP client
and creating a new client each time.

.. code-block:: console

    # Run with default settings (10 requests × 5 parallel)
    uv run python examples/performance/session_pooling_comparison.py

    # Specify number of requests and concurrency
    uv run python examples/performance/session_pooling_comparison.py --requests-per-client 20 --parallel-clients 10

    # Test with bitbank
    uv run python examples/performance/session_pooling_comparison.py --exchange bitbank

    # Run in debug mode
    uv run python examples/performance/session_pooling_comparison.py --log-level DEBUG

Measurement items:
- Execution time and throughput
- Response time statistics
- Memory usage
- HTTP client/session creation count
"""

import asyncio
import gc
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, median, stdev
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import psutil
import typer
from common.helpers import setup_logging
from rich import box  # pyright: ignore[reportMissingModuleSource]
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitbank.native_requests import (
    TickerRequest as BitbankTickerRequest,
)
from crypto_api_client.bitflyer import TickerRequest
from crypto_api_client.core.session_config import SessionConfig

console = Console()
# Unified configuration for development environment
app = typer.Typer(
    pretty_exceptions_enable=True,      # Enable Rich traceback
    pretty_exceptions_show_locals=True,  # Show local variables
    pretty_exceptions_short=False        # Show full traceback
)


@dataclass
class PerformanceMetrics:
    """Performance measurement results"""

    scenario: str
    total_time: float
    response_times: list[float] = field(default_factory=lambda: [])
    memory_usage_mb: float = 0.0
    http_clients_created: int = 0
    sessions_created: int = 0
    requests_count: int = 0
    errors: int = 0

    @property
    def avg_response_time(self) -> float:
        """Average response time (seconds)"""
        return mean(self.response_times) if self.response_times else 0

    @property
    def median_response_time(self) -> float:
        """Median response time (seconds)"""
        return median(self.response_times) if self.response_times else 0

    @property
    def stdev_response_time(self) -> float:
        """Standard deviation (seconds)"""
        return stdev(self.response_times) if len(self.response_times) > 1 else 0

    @property
    def min_response_time(self) -> float:
        """Minimum response time (seconds)"""
        return min(self.response_times) if self.response_times else 0

    @property
    def max_response_time(self) -> float:
        """Maximum response time (seconds)"""
        return max(self.response_times) if self.response_times else 0

    @property
    def requests_per_second(self) -> float:
        """Requests per second"""
        return self.requests_count / self.total_time if self.total_time > 0 else 0


async def measure_memory() -> float:
    """Measure current memory usage (MB)"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # type: ignore


async def test_with_shared_client(
    exchange: str, requests_count: int, concurrent: int
) -> PerformanceMetrics:
    """Scenario 1: Create new session each time + use shared HTTP client"""
    response_times: list[float] = []
    errors = 0
    sessions_created = 0

    gc.collect()
    memory_start = await measure_memory()
    start_time = time.time()

    # Create shared HTTP client
    config = SessionConfig(
        max_connections=concurrent * 2,
        max_keepalive_connections=concurrent,
        keepalive_expiry=30,
        http2_enabled=True,
    )

    shared_client = httpx.AsyncClient(
        limits=config.to_httpx_limits(),
        timeout=config.to_httpx_timeout(),
        http2=config.http2_enabled,
        headers={"User-Agent": config.user_agent},
        follow_redirects=False,
    )

    try:

        async def fetch_ticker() -> None:
            nonlocal errors, sessions_created
            try:
                req_start = time.time()
                sessions_created += 1

                if exchange == "bitflyer":
                    # Pass shared client to create session
                    async with create_session(
                        Exchange.BITFLYER, http_client=shared_client
                    ) as session:
                        # bitFlyer currency pair format (uppercase, underscore separator)
                        product_code = "BTC_JPY"
                        request = TickerRequest(product_code=product_code)
                        await session.api.ticker(request)
                elif exchange == "bitbank":
                    # Pass shared client to create session
                    async with create_session(
                        Exchange.BITBANK, http_client=shared_client
                    ) as session:
                        # bitbank currency pair format (lowercase, underscore separator)
                        pair_str = "btc_jpy"
                        request = BitbankTickerRequest(pair=pair_str)
                        await session.api.ticker(request)

                response_times.append(time.time() - req_start)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                errors += 1

        semaphore = asyncio.Semaphore(concurrent)

        async def fetch_with_limit() -> None:
            async with semaphore:
                await fetch_ticker()

        tasks = [fetch_with_limit() for _ in range(requests_count)]
        await asyncio.gather(*tasks)

    finally:
        await shared_client.aclose()

    total_time = time.time() - start_time
    memory_end = await measure_memory()

    return PerformanceMetrics(
        scenario=f"{exchange.title()} - With Shared HTTP Client",
        total_time=total_time,
        response_times=response_times,
        memory_usage_mb=memory_end - memory_start,
        http_clients_created=1,  # One shared client
        sessions_created=sessions_created,
        requests_count=requests_count,
        errors=errors,
    )


async def test_without_shared_client(
    exchange: str, requests_count: int, concurrent: int
) -> PerformanceMetrics:
    """Scenario 2: Create new session each time + also create new HTTP client each time"""
    response_times: list[float] = []
    errors = 0
    sessions_created = 0

    gc.collect()
    memory_start = await measure_memory()
    start_time = time.time()

    async def fetch_ticker() -> None:
        nonlocal errors, sessions_created
        try:
            req_start = time.time()
            sessions_created += 1

            if exchange == "bitflyer":
                # Don't pass HTTP client (created internally)
                async with create_session(Exchange.BITFLYER) as session:
                    # bitFlyer currency pair format (uppercase, underscore separator)
                    product_code = "BTC_JPY"
                    request = TickerRequest(product_code=product_code)
                    await session.api.ticker(request)
            elif exchange == "bitbank":
                # Don't pass HTTP client (created internally)
                async with create_session(Exchange.BITBANK) as session:
                    # bitbank currency pair format (lowercase, underscore separator)
                    pair_str = "btc_jpy"
                    request = BitbankTickerRequest(pair=pair_str)
                    await session.api.ticker(request)

            response_times.append(time.time() - req_start)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            errors += 1

    semaphore = asyncio.Semaphore(concurrent)

    async def fetch_with_limit() -> None:
        async with semaphore:
            await fetch_ticker()

    tasks = [fetch_with_limit() for _ in range(requests_count)]
    await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    memory_end = await measure_memory()

    return PerformanceMetrics(
        scenario=f"{exchange.title()} - Without Shared HTTP Client",
        total_time=total_time,
        response_times=response_times,
        memory_usage_mb=memory_end - memory_start,
        http_clients_created=sessions_created,  # Each session creates a new client
        sessions_created=sessions_created,
        requests_count=requests_count,
        errors=errors,
    )


def display_results(metrics_list: list[PerformanceMetrics]) -> None:
    """Display results in table format"""

    # Performance comparison table
    table = Table(title="🚀 Shared HTTP Client Effect Comparison", box=box.ROUNDED)
    table.add_column("Scenario", style="cyan", no_wrap=True)
    table.add_column("Total Time", justify="right", style="yellow")
    table.add_column("Req/s", justify="right", style="green")
    table.add_column("Avg (ms)", justify="right")
    table.add_column("Med (ms)", justify="right")
    table.add_column("StdDev", justify="right")
    table.add_column("Min/Max (ms)", justify="right")
    table.add_column("Memory", justify="right", style="magenta")
    table.add_column("HTTP Clients", justify="right", style="blue")
    table.add_column("Sessions", justify="right", style="blue")
    table.add_column("Errors", justify="right", style="red")

    for metrics in metrics_list:
        table.add_row(
            metrics.scenario,
            f"{metrics.total_time:.2f}s",
            f"{metrics.requests_per_second:.1f}",
            f"{metrics.avg_response_time * 1000:.1f}",
            f"{metrics.median_response_time * 1000:.1f}",
            f"{metrics.stdev_response_time * 1000:.1f}",
            f"{metrics.min_response_time * 1000:.0f}/{metrics.max_response_time * 1000:.0f}",
            f"{metrics.memory_usage_mb:.1f}MB",
            str(metrics.http_clients_created),
            str(metrics.sessions_created),
            str(metrics.errors) if metrics.errors > 0 else "0",
        )

    console.print(table)

    # Analyze improvement rate
    console.print("\n📊 [bold cyan]Performance Analysis:[/bold cyan]")

    # Analyze each exchange
    for exchange in ["bitflyer", "bitbank"]:
        exchange_metrics = [m for m in metrics_list if exchange in m.scenario.lower()]
        if len(exchange_metrics) < 2:
            continue

        console.print(f"\n[bold]{exchange.title()}:[/bold]")

        # Compare with and without shared client
        with_shared = next(
            (m for m in exchange_metrics if "With Shared" in m.scenario), None
        )
        without_shared = next(
            (m for m in exchange_metrics if "Without Shared" in m.scenario), None
        )

        if with_shared and without_shared:
            time_improvement = (
                (without_shared.total_time - with_shared.total_time)
                / without_shared.total_time
            ) * 100
            memory_diff = without_shared.memory_usage_mb - with_shared.memory_usage_mb
            client_diff = (
                without_shared.http_clients_created - with_shared.http_clients_created
            )

            console.print(
                f"  • Shared HTTP client is [green]{time_improvement:.1f}%[/green] faster"
            )
            console.print(f"  • Memory savings: [green]{memory_diff:.1f} MB[/green]")
            console.print(f"  • HTTP clients saved: [blue]{client_diff}[/blue]")

            # Response time improvement
            avg_improvement = (
                (without_shared.avg_response_time - with_shared.avg_response_time)
                / without_shared.avg_response_time
            ) * 100
            console.print(
                f"  • Avg response time improvement: [green]{avg_improvement:.1f}%[/green]"
            )

            # Session creation overhead
            console.print(
                f"  • Sessions created: [yellow]{with_shared.sessions_created}[/yellow] (same in both scenarios)"
            )
            console.print(
                f"  • Overhead per session: [yellow]{(without_shared.total_time - with_shared.total_time) / without_shared.sessions_created * 1000:.2f}ms[/yellow]"
            )


@app.command()
def main(
    requests: Annotated[
        int, typer.Option("--requests", "-r", help="Total number of requests to make")
    ] = 100,
    concurrent: Annotated[
        int, typer.Option("--concurrent", "-c", help="Number of concurrent requests")
    ] = 10,
    exchange: Annotated[
        str,
        typer.Option(
            "--exchange", "-e", help="Exchange to test (bitflyer/bitbank/all)"
        ),
    ] = "all",
    log_level: Annotated[
        str, typer.Option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)")
    ] = "WARNING",
) -> None:
    """Measure the effect of shared HTTP client

    Compare performance when creating new sessions each time,
    using a shared HTTP client vs not using one.

    Examples:
        # Test all exchanges (100 requests, concurrency 10)
        uv run python examples/performance/session_pooling_comparison.py

        # bitFlyer only, 500 requests, concurrency 50
        uv run python examples/performance/session_pooling_comparison.py -r 3 -c 3 -e bitbank

        # bitbank only, test with fewer requests
        uv run python examples/performance/session_pooling_comparison.py -r 20 -c 5 -e bitbank
    """
    asyncio.run(async_main(requests, concurrent, exchange, log_level))


async def async_main(
    requests: int, concurrent: int, exchange: str, log_level: str
) -> None:
    setup_logging(log_level)

    console.print("[bold cyan]🔬 Shared HTTP Client Effect Test[/bold cyan]")
    console.print(f"📝 Settings: {requests} requests, {concurrent} concurrent")
    console.print(f"🎯 Exchange: {exchange}\n")

    metrics_list: list[PerformanceMetrics] = []

    exchanges_to_test: list[str] = []
    if exchange in ["all", "bitflyer"]:
        exchanges_to_test.append("bitflyer")
    if exchange in ["all", "bitbank"]:
        exchanges_to_test.append("bitbank")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        for ex in exchanges_to_test:
            # Test with shared client
            task_desc = f"Testing {ex} with shared client..."
            task = progress.add_task(task_desc, total=None)
            try:
                metrics = await test_with_shared_client(ex, requests, concurrent)
                metrics_list.append(metrics)
            except Exception as e:
                console.print(f"[red]Error in {ex} with shared client: {e}[/red]")
            progress.update(task, completed=True)

            # Wait a bit for API rate limit
            await asyncio.sleep(1)

            # Test without shared client
            task_desc = f"Testing {ex} without shared client..."
            task = progress.add_task(task_desc, total=None)
            try:
                metrics = await test_without_shared_client(ex, requests, concurrent)
                metrics_list.append(metrics)
            except Exception as e:
                console.print(f"[red]Error in {ex} without shared client: {e}[/red]")
            progress.update(task, completed=True)

            # Wait a bit for API rate limit
            await asyncio.sleep(1)

    console.print()
    display_results(metrics_list)


if __name__ == "__main__":
    app()  # Typer automatically catches exceptions and displays them nicely
