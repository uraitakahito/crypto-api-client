#!/usr/bin/env python3
"""Common module to fetch tickers from all exchanges

This module provides exchange-specific ticker fetching functionality used across multiple sample codes.
It absorbs differences between exchanges and returns data in a unified format.

Usage example:
    >>> from common.ticker_fetcher import fetch_all_btc_jpy_tickers
    >>> tickers = await fetch_all_btc_jpy_tickers()
    >>> for ticker in tickers:
    ...     print(f"{ticker['exchange']}: {ticker.get('bid_price')}")
"""

import asyncio
from typing import Any

from crypto_api_client import Exchange, create_session
from crypto_api_client.binance import (
    Ticker as BinanceTicker,
)
from crypto_api_client.binance import (
    TickerRequest as BinanceTickerRequest,
)
from crypto_api_client.bitbank import (
    TickerRequest as BitbankTickerRequest,
)
from crypto_api_client.bitflyer import (
    TickerRequest as BitflyerTickerRequest,
)
from crypto_api_client.coincheck import (
    TickerRequest as CoincheckTickerRequest,
)
from crypto_api_client.gmocoin import (
    TickerRequest as GmocoinTickerRequest,
)

# Define BTC/JPY currency pair format for each exchange
BINANCE_BTC_JPY = "BTCJPY"  # BINANCE: no separator
BITBANK_BTC_JPY = "btc_jpy"  # bitbank: lowercase, underscore
BITFLYER_BTC_JPY = "BTC_JPY"  # bitFlyer: uppercase, underscore
COINCHECK_BTC_JPY = "btc_jpy"  # Coincheck: lowercase, underscore
GMOCOIN_BTC_JPY = "BTC_JPY"  # GMO Coin: uppercase, underscore


async def fetch_all_btc_jpy_tickers() -> list[dict[str, Any]]:
    tasks = [
        fetch_binance_ticker(BINANCE_BTC_JPY),
        fetch_bitbank_ticker(BITBANK_BTC_JPY),
        fetch_bitflyer_ticker(BITFLYER_BTC_JPY),
        fetch_coincheck_ticker(COINCHECK_BTC_JPY),
        fetch_gmocoin_ticker(GMOCOIN_BTC_JPY),
    ]
    return await asyncio.gather(*tasks)


async def fetch_binance_ticker(pair: str) -> dict[str, Any]:
    try:
        async with create_session(Exchange.BINANCE) as session:
            request = BinanceTickerRequest(symbol=pair)
            ticker: BinanceTicker = await session.api.ticker_24hr(request)

            return {
                "exchange": "BINANCE",
                "symbol": pair,
                "last_price": ticker.lastPrice,
                "bid_price": ticker.bidPrice,
                "ask_price": ticker.askPrice,
                "volume": ticker.volume,
                "high": ticker.highPrice,
                "low": ticker.lowPrice,
                "timestamp": None,  # BINANCE ticker has no timestamp
                "raw": ticker,
            }
    except Exception as e:
        return {"exchange": "BINANCE", "error": str(e)}


async def fetch_bitbank_ticker(pair: str) -> dict[str, Any]:
    try:
        async with create_session(Exchange.BITBANK) as session:
            request = BitbankTickerRequest(pair=pair)
            ticker = await session.api.ticker(request)

            return {
                "exchange": "bitbank",
                "symbol": pair,
                "last_price": ticker.last,
                "bid_price": ticker.buy,
                "ask_price": ticker.sell,
                "volume": ticker.vol,
                "high": ticker.high,
                "low": ticker.low,
                "timestamp": ticker.timestamp,
                "raw": ticker,
            }
    except Exception as e:
        return {"exchange": "bitbank", "error": str(e)}


async def fetch_bitflyer_ticker(pair: str) -> dict[str, Any]:
    try:
        async with create_session(Exchange.BITFLYER) as session:
            request = BitflyerTickerRequest(product_code=pair)
            ticker = await session.api.ticker(request)

            return {
                "exchange": "bitFlyer",
                "symbol": str(ticker.product_code),
                "last_price": ticker.ltp,
                "bid_price": ticker.best_bid,
                "ask_price": ticker.best_ask,
                "volume": ticker.volume,
                "high": None,  # bitFlyer ticker has no high/low
                "low": None,
                "timestamp": ticker.timestamp,
                "raw": ticker,
            }
    except Exception as e:
        return {"exchange": "bitFlyer", "error": str(e)}


async def fetch_coincheck_ticker(pair: str) -> dict[str, Any]:
    try:
        async with create_session(Exchange.COINCHECK) as session:
            request = CoincheckTickerRequest(pair=pair)
            ticker = await session.api.ticker(request)

            return {
                "exchange": "Coincheck",
                "symbol": pair,
                "last_price": ticker.last,
                "bid_price": ticker.bid,
                "ask_price": ticker.ask,
                "volume": ticker.volume,
                "high": ticker.high,
                "low": ticker.low,
                "timestamp": ticker.timestamp,
                "raw": ticker,
            }
    except Exception as e:
        return {"exchange": "Coincheck", "error": str(e)}


async def fetch_gmocoin_ticker(pair: str) -> dict[str, Any]:
    try:
        async with create_session(Exchange.GMOCOIN) as session:
            request = GmocoinTickerRequest(symbol=pair)
            tickers = await session.api.ticker(request)

            if tickers and len(tickers) > 0:
                ticker = tickers[0]
                return {
                    "exchange": "GMO Coin",
                    "symbol": str(ticker.symbol),
                    "last_price": ticker.last,
                    "bid_price": ticker.bid,
                    "ask_price": ticker.ask,
                    "volume": ticker.volume,
                    "high": ticker.high,
                    "low": ticker.low,
                    "timestamp": ticker.timestamp,
                    "raw": ticker,
                }
    except Exception as e:
        return {"exchange": "GMO Coin", "error": str(e)}

    return {"exchange": "GMO Coin", "error": "No data"}
