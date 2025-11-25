#!/usr/bin/env python3
"""Demonstration of header protection features

Demonstrates the API key concealment functionality provided by the SecretHeaders class.
Confirms that sensitive information is automatically masked
during log output and error occurrences.

.. code-block:: console

    # Run basic demo
    uv run python examples/security/headers_protection.py basic

    # Run logging demo
    uv run python examples/security/headers_protection.py logging

    # Run error handling demo
    uv run python examples/security/headers_protection.py error

    # Run all demos
    uv run python examples/security/headers_protection.py all
"""

import logging

import typer
from pydantic import SecretStr
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel

from crypto_api_client.security.secret_headers import SecretHeaders

# Rich console configuration
console = Console()
app = typer.Typer(help="SecretHeaders security features demo")


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging"""
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


def demo_secret_str() -> None:
    """SecretStr demonstration"""
    console.print("\n[bold cyan]📝 SecretStr Demonstration[/bold cyan]")

    # Create SecretStr instances
    api_key = SecretStr("sk-1234567890abcdefghijklmnop")
    api_secret = SecretStr("secret_password_123456")

    # Normal output (automatically masked)
    console.print(f"API Key: {api_key}")  # sk-********
    console.print(f"API Secret: {api_secret}")  # sec********

    # Get actual value (only when necessary)
    actual_value = api_key.get_secret_value()
    console.print(f"Actual value (normally not used): [dim]{actual_value[:10]}...[/dim]")

    # When included in dictionary
    config = {
        "api_key": api_key,
        "api_secret": api_secret,
        "endpoint": "https://api.example.com",
    }
    console.print(f"Config dictionary: {config}")


def demo_secret_headers() -> None:
    """SecretHeaders demonstration"""
    console.print("\n[bold cyan]🔒 SecretHeaders Demonstration[/bold cyan]")

    # Create headers with various sensitive headers
    headers = SecretHeaders(
        {
            "ACCESS-KEY": "api_key_1234567890",
            "ACCESS-SIGN": "signature_abcdefghij",
            "ACCESS-TIMESTAMP": "2025-01-30T12:34:56",
            "Authorization": "Bearer token_xyz123456789",
            "X-API-KEY": "x_api_key_secret",
            "Content-Type": "application/json",
            "User-Agent": "crypto-api-client/1.0",
            "Accept": "application/json",
        }
    )

    # String representation (masked format)
    console.print("\n[yellow]Masked header display:[/yellow]")
    for key, value in headers.get_masked_dict().items():
        is_sensitive = any(
            pattern in key.upper()
            for pattern in ["KEY", "SIGN", "SECRET", "TOKEN", "AUTH"]
        )
        if is_sensitive:
            console.print(f"  [red]{key}[/red]: [dim]{value}[/dim]")
        else:
            console.print(f"  [green]{key}[/green]: {value}")

    # Simulate log output
    logger = logging.getLogger(__name__)
    logger.info(f"HTTP Headers: {headers}")

    # Access actual values (only when necessary)
    console.print("\n[yellow]Actual values (for debugging):[/yellow]")
    actual_key = headers["ACCESS-KEY"]
    console.print(f"  ACCESS-KEY actual value: [dim]{actual_key[:10]}...[/dim]")


def demo_integration_example() -> None:
    """Integrated demo close to actual usage"""
    console.print("\n[bold cyan]🚀 Real-world Example (bitFlyer-style)[/bold cyan]")

    # Simulate API client
    api_key = SecretStr("bitFlyer_api_key_12345")
    api_secret = SecretStr("bitFlyer_secret_67890")

    # Generate authentication headers (bitFlyer-style)
    import hashlib
    import hmac
    from datetime import UTC, datetime

    timestamp = datetime.now(UTC).isoformat()
    method = "GET"
    path = "/v1/me/getbalance"
    body = ""

    text = timestamp + method + path + body
    sign = hmac.new(
        api_secret.get_secret_value().encode(), text.encode(), hashlib.sha256
    ).hexdigest()

    # Protect with SecretHeaders
    headers = SecretHeaders(
        {
            "ACCESS-KEY": api_key.get_secret_value(),
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-SIGN": sign,
            "Content-Type": "application/json",
        }
    )

    # Simulate request
    console.print("\n[yellow]API Request Simulation:[/yellow]")
    console.print(f"Method: {method}")
    console.print(f"Path: {path}")
    console.print(f"Headers: {headers}")  # Automatically masked

    # Convert to httpx.Headers (when sending actual request)
    _ = headers.to_httpx_headers()
    console.print("\n[dim]Converted to httpx.Headers type (ready to send)[/dim]")


@app.command()
def main(
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Log level (DEBUG, INFO, WARNING, ERROR)",
    ),
    demo_type: str = typer.Option(
        "all",
        "--demo",
        help="Demo type (str, integration, all)",
    ),
) -> None:
    """SecretHeaders security features demonstration"""

    setup_logging(log_level)

    console.print(
        Panel.fit(
            "[bold cyan]crypto-api-client Security Features Demo[/bold cyan]\n"
            "[dim]Protecting sensitive information with SecretStr and SecretHeaders[/dim]",
            border_style="cyan",
        )
    )

    demos = {
        "str": demo_secret_str,
        "headers": demo_secret_headers,
        "integration": demo_integration_example,
    }

    if demo_type == "all":
        for demo_func in demos.values():
            demo_func()
    elif demo_type in demos:
        demos[demo_type]()
    else:
        console.print(f"[red]Unknown demo type: {demo_type}[/red]")
        console.print(f"Available: {', '.join(demos.keys())}")

    console.print("\n[green]✅ Demonstration complete[/green]")


if __name__ == "__main__":
    app()
