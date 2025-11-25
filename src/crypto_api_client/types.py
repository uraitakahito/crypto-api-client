"""Type aliases for type annotations

This module provides type aliases for each exchange's API client class.
By importing within TYPE_CHECKING blocks, circular imports are avoided.

Usage example::

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from crypto_api_client.types import BitFlyerApiClient

    async def get_ticker(session: ExchangeSession[BitFlyerApiClient]) -> None:
        ticker = await session.api.ticker(request)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crypto_api_client.binance.exchange_api_client import (
        ExchangeApiClient as BinanceApiClient,
    )
    from crypto_api_client.bitbank.exchange_api_client import (
        ExchangeApiClient as BitbankApiClient,
    )
    from crypto_api_client.bitflyer.exchange_api_client import (
        ExchangeApiClient as BitFlyerApiClient,
    )
    from crypto_api_client.coincheck.exchange_api_client import (
        ExchangeApiClient as CoincheckApiClient,
    )
    from crypto_api_client.gmocoin.exchange_api_client import (
        ExchangeApiClient as GmoCoinApiClient,
    )

__all__ = [
    "BinanceApiClient",
    "BitbankApiClient",
    "BitFlyerApiClient",
    "CoincheckApiClient",
    "GmoCoinApiClient",
]
