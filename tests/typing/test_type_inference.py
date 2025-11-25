"""Type inference tests

These tests do nothing at runtime but only have meaning during
static analysis by type checkers (pyright/mypy).
"""

from __future__ import annotations

from crypto_api_client import Exchange, create_session
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


async def test_bitflyer_type_inference() -> None:
    """bitFlyer type inference test"""
    session = create_session(Exchange.BITFLYER)
    # Type checker infers session.api as BitFlyerApiClient
    api: BitFlyerApiClient = session.api  # ← Verify no type error
    assert api is not None


async def test_binance_type_inference() -> None:
    """BINANCE type inference test"""
    session = create_session(Exchange.BINANCE)
    api: BinanceApiClient = session.api
    assert api is not None


async def test_bitbank_type_inference() -> None:
    """bitbank type inference test"""
    session = create_session(Exchange.BITBANK)
    api: BitbankApiClient = session.api
    assert api is not None


async def test_gmocoin_type_inference() -> None:
    """GMO Coin type inference test"""
    session = create_session(Exchange.GMOCOIN)
    api: GmoCoinApiClient = session.api
    assert api is not None


async def test_coincheck_type_inference() -> None:
    """Coincheck type inference test"""
    session = create_session(Exchange.COINCHECK)
    api: CoincheckApiClient = session.api
    assert api is not None
