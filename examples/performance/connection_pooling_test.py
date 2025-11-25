#!/usr/bin/env python
"""Sample program to measure Connection Pooling efficiency

.. code-block:: console

    $ uv sync --extra examples
    $ uv run python examples/performance/connection_pooling_test.py --total-requests 200 --max-parallel 20 --target-exchange bitbank

This program compares performance across the following 3 scenarios:
1. With Connection Pooling (using sessions)
2. Without Connection Pooling (creating new client each time)
3. Comparison of concurrent request processing
"""

import asyncio
import gc
import os
import time
from dataclasses import dataclass
from statistics import mean, median, stdev
from typing import Annotated

import psutil
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from crypto_api_client import Exchange, create_session
from crypto_api_client.bitbank.native_requests import (
    TickerRequest as BitbankTickerRequest,
)
from crypto_api_client.bitflyer import TickerRequest

console = Console()
app = typer.Typer()


@dataclass
class PerformanceMetrics:
    scenario: str
    total_time: float
    response_times: list[float]
    memory_usage_mb: float
    connections_created: int
    requests_count: int
    errors: int

    @property
    def avg_response_time(self) -> float:
        """Average response time"""
        return mean(self.response_times) if self.response_times else 0

    @property
    def median_response_time(self) -> float:
        """Median response time"""
        return median(self.response_times) if self.response_times else 0

    @property
    def stdev_response_time(self) -> float:
        """Standard deviation"""
        return stdev(self.response_times) if len(self.response_times) > 1 else 0

    @property
    def min_response_time(self) -> float:
        """Minimum response time"""
        return min(self.response_times) if self.response_times else 0

    @property
    def max_response_time(self) -> float:
        """Maximum response time"""
        return max(self.response_times) if self.response_times else 0

    @property
    def requests_per_second(self) -> float:
        """Requests per second"""
        return self.requests_count / self.total_time if self.total_time > 0 else 0


@app.command()
def main(
    total_requests: Annotated[
        int,
        typer.Option(
            "--total-requests",
            "--requests",
            "-r",
            min=1,
            max=10000,
            help="How many API requests to make in total",
            metavar="COUNT",
            rich_help_panel="Performance Parameters",
        ),
    ] = 100,
    max_parallel: Annotated[
        int,
        typer.Option(
            "--max-parallel",
            "--concurrent",
            "-c",
            min=1,
            max=100,
            help="Maximum parallel requests at once",
            metavar="COUNT",
            rich_help_panel="Performance Parameters",
        ),
    ] = 10,
    target_exchange: Annotated[
        str,
        typer.Option(
            "--target-exchange",
            "--exchange",
            "-e",
            help="Which exchange(s) to test (bitflyer/bitbank/all)",
            metavar="NAME",
            rich_help_panel="Test Configuration",
        ),
    ] = "all",
) -> None:
    asyncio.run(async_main(total_requests, max_parallel, target_exchange))


async def async_main(
    total_requests: int,
    max_parallel: int,
    target_exchange: str,
) -> None:
    print_header(total_requests, max_parallel)

    metrics_list = await run_tests(total_requests, max_parallel, target_exchange)

    console.print()
    display_results(metrics_list)


def print_header(total_requests: int, max_parallel: int) -> None:
    console.print("[bold cyan]🔬 Connection Pooling Efficiency Test[/bold cyan]")
    console.print(
        f"📝 Settings: {total_requests} total requests, {max_parallel} max parallel"
    )


async def run_tests(
    total_requests: int,
    max_parallel: int,
    target_exchange: str,
) -> list[PerformanceMetrics]:
    metrics_list: list[PerformanceMetrics] = []

    if target_exchange in ["bitflyer", "all"]:
        metrics_list.extend(await run_bitflyer_tests(total_requests, max_parallel))

    if target_exchange in ["bitbank", "all"]:
        metrics_list.extend(await run_bitbank_tests(total_requests, max_parallel))

    return metrics_list


async def run_bitflyer_tests(
    total_requests: int,
    max_parallel: int,
) -> list[PerformanceMetrics]:
    results: list[PerformanceMetrics] = []

    # With pooling
    results.append(await test_bitflyer_with_session(total_requests, max_parallel))

    # Without pooling
    results.append(await test_bitflyer_without_pooling(total_requests, max_parallel))

    return results


async def run_bitbank_tests(
    total_requests: int,
    max_parallel: int,
) -> list[PerformanceMetrics]:
    results: list[PerformanceMetrics] = []

    # With pooling
    results.append(await test_bitbank_with_session(total_requests, max_parallel))

    # Without pooling
    results.append(await test_bitbank_without_pooling(total_requests, max_parallel))

    return results


async def measure_memory() -> float:
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # type: ignore


async def test_bitflyer_with_session(
    requests: int, concurrent: int
) -> PerformanceMetrics:
    response_times: list[float] = []
    errors = 0
    connections_created = 1  # One HTTP client for the session

    gc.collect()
    memory_start = await measure_memory()
    start_time = time.time()

    async with create_session(Exchange.BITFLYER) as session:

        async def fetch_ticker() -> None:
            nonlocal errors
            try:
                req_start = time.time()
                # bitFlyer currency pair format (uppercase, underscore separator)
                product_code = "BTC_JPY"
                request = TickerRequest(product_code=product_code)
                await session.api.ticker(request)
                response_times.append(time.time() - req_start)
            except Exception as e:
                errors += 1
                if errors == 1:  # Print details for first error only
                    console.print(f"[red]Error detail: {e}[/red]")

        semaphore = asyncio.Semaphore(concurrent)

        async def fetch_with_limit() -> None:
            async with semaphore:
                await fetch_ticker()

        tasks = [fetch_with_limit() for _ in range(requests)]
        await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    memory_end = await measure_memory()

    return PerformanceMetrics(
        scenario="BitFlyer with Session (Pooling)",
        total_time=total_time,
        response_times=response_times,
        memory_usage_mb=memory_end - memory_start,
        connections_created=connections_created,
        requests_count=requests,
        errors=errors,
    )


async def test_bitflyer_without_pooling(
    requests: int, concurrent: int
) -> PerformanceMetrics:
    response_times: list[float] = []
    errors = 0
    connections_created = 0

    gc.collect()
    memory_start = await measure_memory()
    start_time = time.time()

    async def fetch_ticker() -> None:
        nonlocal errors, connections_created
        try:
            req_start = time.time()
            # Create new HTTP client and session each time
            async with create_session(Exchange.BITFLYER) as temp_session:
                connections_created += 1
                # bitFlyer currency pair format (uppercase, underscore separator)
                product_code = "BTC_JPY"
                request = TickerRequest(product_code=product_code)
                await temp_session.api.ticker(request)
                response_times.append(time.time() - req_start)
        except Exception:
            errors += 1

    semaphore = asyncio.Semaphore(concurrent)

    async def fetch_with_limit() -> None:
        async with semaphore:
            await fetch_ticker()

    tasks = [fetch_with_limit() for _ in range(requests)]
    await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    memory_end = await measure_memory()

    return PerformanceMetrics(
        scenario="BitFlyer without Pooling",
        total_time=total_time,
        response_times=response_times,
        memory_usage_mb=memory_end - memory_start,
        connections_created=connections_created,
        requests_count=requests,
        errors=errors,
    )


async def test_bitbank_with_session(
    requests: int, concurrent: int
) -> PerformanceMetrics:
    response_times: list[float] = []
    errors = 0
    connections_created = 1  # bitbank has one public HTTP client

    gc.collect()
    memory_start = await measure_memory()
    start_time = time.time()

    async with create_session(Exchange.BITBANK) as session:

        async def fetch_ticker() -> None:
            nonlocal errors
            try:
                req_start = time.time()
                # bitbank currency pair format (lowercase, underscore separator)
                pair_str = "btc_jpy"
                request = BitbankTickerRequest(pair=pair_str)
                await session.api.ticker(request)
                response_times.append(time.time() - req_start)
            except Exception as e:
                errors += 1
                if errors == 1:  # Print details for first error only
                    console.print(f"[red]Error detail: {e}[/red]")

        semaphore = asyncio.Semaphore(concurrent)

        async def fetch_with_limit() -> None:
            async with semaphore:
                await fetch_ticker()

        tasks = [fetch_with_limit() for _ in range(requests)]
        await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    memory_end = await measure_memory()

    return PerformanceMetrics(
        scenario="Bitbank with Session (Pooling)",
        total_time=total_time,
        response_times=response_times,
        memory_usage_mb=memory_end - memory_start,
        connections_created=connections_created,
        requests_count=requests,
        errors=errors,
    )


async def test_bitbank_without_pooling(
    requests: int, concurrent: int
) -> PerformanceMetrics:
    response_times: list[float] = []
    errors = 0
    connections_created = 0

    gc.collect()
    memory_start = await measure_memory()
    start_time = time.time()

    async def fetch_ticker() -> None:
        nonlocal errors, connections_created
        try:
            req_start = time.time()
            # Create new HTTP client and session each time
            async with create_session(Exchange.BITBANK) as temp_session:
                connections_created += 1
                # bitbank currency pair format (lowercase, underscore separator)
                pair_str = "btc_jpy"
                request = BitbankTickerRequest(pair=pair_str)
                await temp_session.api.ticker(request)
                response_times.append(time.time() - req_start)
        except Exception:
            errors += 1

    semaphore = asyncio.Semaphore(concurrent)

    async def fetch_with_limit() -> None:
        async with semaphore:
            await fetch_ticker()

    tasks = [fetch_with_limit() for _ in range(requests)]
    await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    memory_end = await measure_memory()

    return PerformanceMetrics(
        scenario="Bitbank without Pooling",
        total_time=total_time,
        response_times=response_times,
        memory_usage_mb=memory_end - memory_start,
        connections_created=connections_created,
        requests_count=requests,
        errors=errors,
    )


def display_results(metrics_list: list[PerformanceMetrics]) -> None:
    table = Table(title="🚀 Connection Pooling Performance Comparison", box=box.ROUNDED)
    table.add_column("Scenario", style="cyan", no_wrap=True)
    table.add_column("Total Time (s)", justify="right", style="yellow")
    table.add_column("Requests/sec", justify="right", style="green")
    table.add_column("Avg Response (ms)", justify="right")
    table.add_column("Median Response (ms)", justify="right")
    table.add_column("StdDev (ms)", justify="right")
    table.add_column("Min/Max (ms)", justify="right")
    table.add_column("Memory (MB)", justify="right", style="magenta")
    table.add_column("Connections", justify="right", style="blue")
    table.add_column("Errors", justify="right", style="red")

    for metrics in metrics_list:
        table.add_row(
            metrics.scenario,
            f"{metrics.total_time:.2f}",
            f"{metrics.requests_per_second:.1f}",
            f"{metrics.avg_response_time * 1000:.1f}",
            f"{metrics.median_response_time * 1000:.1f}",
            f"{metrics.stdev_response_time * 1000:.1f}",
            f"{metrics.min_response_time * 1000:.1f}/{metrics.max_response_time * 1000:.1f}",
            f"{metrics.memory_usage_mb:.1f}",
            str(metrics.connections_created),
            str(metrics.errors) if metrics.errors > 0 else "0",
        )

    console.print(table)

    console.print("\n📊 [bold cyan]Performance Analysis:[/bold cyan]")

    # BitFlyer analysis
    bitflyer_with = next(
        (m for m in metrics_list if "BitFlyer with" in m.scenario), None
    )
    bitflyer_without = next(
        (m for m in metrics_list if "BitFlyer without" in m.scenario), None
    )

    if bitflyer_with and bitflyer_without:
        time_improvement = (
            (bitflyer_without.total_time - bitflyer_with.total_time)
            / bitflyer_without.total_time
        ) * 100
        memory_diff = bitflyer_without.memory_usage_mb - bitflyer_with.memory_usage_mb
        console.print("\n[bold]BitFlyer:[/bold]")
        console.print(
            f"  • Connection pooling is [green]{time_improvement:.1f}%[/green] faster"
        )
        console.print(f"  • Memory savings: [green]{memory_diff:.1f} MB[/green]")
        console.print(
            f"  • Connection reduction: [blue]{bitflyer_without.connections_created - bitflyer_with.connections_created}[/blue] connections saved"
        )

    # Bitbank analysis
    bitbank_with = next((m for m in metrics_list if "Bitbank with" in m.scenario), None)
    bitbank_without = next(
        (m for m in metrics_list if "Bitbank without" in m.scenario), None
    )

    if bitbank_with and bitbank_without:
        time_improvement = (
            (bitbank_without.total_time - bitbank_with.total_time)
            / bitbank_without.total_time
        ) * 100
        memory_diff = bitbank_without.memory_usage_mb - bitbank_with.memory_usage_mb
        console.print("\n[bold]Bitbank:[/bold]")
        console.print(
            f"  • Connection pooling is [green]{time_improvement:.1f}%[/green] faster"
        )
        console.print(f"  • Memory savings: [green]{memory_diff:.1f} MB[/green]")
        console.print(
            f"  • Connection reduction: [blue]{bitbank_without.connections_created - bitbank_with.connections_created}[/blue] connections saved"
        )


if __name__ == "__main__":
    app()
