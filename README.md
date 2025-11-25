# crypto-api-client

A simple client library for multiple cryptocurrency exchange APIs.

## Features

- Multi-Exchange Support
  - Supports BINANCE, bitbank, bitFlyer, Coincheck, GMO Coin, and Upbit (*Most exchanges currently support ticker and order book retrieval. Additional endpoints can be added upon request or via pull requests*).
- Async/Await Support
  - Fully asynchronous implementation using Python's asyncio.
- HTTP/2 and Connection Pooling
  - Built-in support for HTTP/2 and connection pooling for efficient API communication.
- Decimal Precision
  - Uses `Decimal` type instead of `float` or `int` to maintain precision in financial calculations.
- Unified Timestamp Handling
  - All timestamps are normalized to UTC `datetime` objects, regardless of exchange location or data format.
- Callback System
  - Register callbacks to execute before and after HTTP requests.
- Automatic Secret Masking
  - Automatically masks sensitive information (*within reasonable limits*) to prevent accidental exposure in logs or error monitoring services.
- Shared Rate Limiting
  - Provides a mechanism to share rate limit state across multiple clients using Redis.
- Proxy Support
  - Full support for HTTP/HTTPS proxies with optional authentication.

## Examples

### Public API

Retrieve ticker from BINANCE:

```bash
uv run python examples/binance/ticker.py --pair BTCUSDT --zone Asia/Tokyo
```

Retrieve order book from bitFlyer:

```bash
uv run python examples/bitflyer/board.py --pair BTC_JPY --price-band 100000
```

## Documentation

Generate HTML documentation with the following commands:

```bash
# Generate API documentation
uv run sphinx-apidoc -f -o docs/source src/crypto_api_client

# Clean build directory
uv run sphinx-build -M clean docs/source docs/build

# Build English HTML documentation
uv run sphinx-build -M html docs/source docs/build

# Build Japanese HTML documentation
uv run sphinx-build -M html docs/source docs/build/ja -D language=ja
```

The generated documentation will be available at:
- English: [docs/build/html/index.html](docs/build/html/index.html)
- Japanese: [docs/build/ja/html/index.html](docs/build/ja/html/index.html)

For terminology used throughout this library, please refer to the [glossary](docs/source/glossary.rst).

## Non-Goals

This library explicitly does **not** aim to:

- Synchronous Support: Only asynchronous connections are supported. Synchronous connections are not provided.
- High-Frequency Trading (HFT): This library is not designed for HFT use cases.
- Business Logic Error Handling: Error handling and recovery strategies driven by business logic are not implemented.
- Intelligent Types: Advanced types better suited for higher-level abstractions are not implemented.
- Default Error Validation: HTTP request precondition/postcondition error handling is not invoked by default.
  - Error handling for exchange-detected errors is implemented as add-on callbacks.
    - Use default error handling like `examples/bitflyer/default_response_validator.py`, or integrate custom error handling like `examples/bitflyer/custom_response_validator.py`.

## Debugging with Visual Studio Code

Sample debug configurations are defined in [launch.json.sample](.vscode/launch.json.sample). Run them from the `Run and Debug` panel.

## Installation

```bash
pip install crypto-api-client
```

Or using uv:

```bash
uv add crypto-api-client
```

## Quick Start

### Public API Example

```python
import asyncio
from crypto_api_client import Exchange, create_session
from crypto_api_client.bitflyer import TickerRequest

async def main():
    async with create_session(Exchange.BITFLYER) as session:
        ticker = await session.api.ticker(TickerRequest(product_code="BTC_JPY"))
        print(f"Last Price: {ticker.ltp}")

asyncio.run(main())
```

### Private API Example (with Authentication)

```python
import asyncio
import os
from pydantic import SecretStr
from crypto_api_client import Exchange, create_session

async def main():
    async with create_session(
        Exchange.BITFLYER,
        api_key=SecretStr(os.environ["BITFLYER_API_KEY"]),
        api_secret=SecretStr(os.environ["BITFLYER_API_SECRET"])
    ) as session:
        balances = await session.api.getbalance()
        for balance in balances:
            print(f"{balance.currency_code}: {balance.available}")

asyncio.run(main())
```

## Requirements

- Python 3.13+
- See [pyproject.toml](pyproject.toml) for complete dependency list

## Development

### Running Tests

```bash
uv run pytest tests/ -v
```

### Running Examples

```bash
# Public API examples
uv run python examples/bitflyer/ticker.py --pair BTC_JPY --zone Asia/Tokyo
uv run python examples/binance/ticker.py --pair BTCUSDT --zone Asia/Tokyo

# Private API examples (requires API credentials)
export BITFLYER_API_KEY="your_api_key"
export BITFLYER_API_SECRET="your_api_secret"
uv run python examples/bitflyer/balances.py
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Adding support for additional exchange endpoints
- Bug fixes and improvements
- Documentation enhancements
- New examples

## License

[Unlicense](./LICENSE)

