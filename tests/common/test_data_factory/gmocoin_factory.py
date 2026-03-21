"""GMO Coin Test Data Factory

Provides builder classes for generating GMO Coin test data.

Usage:
    from tests.common.test_data_factory import GmocoinDataFactory

    # Generate ticker data
    ticker_data = GmocoinDataFactory.ticker().with_symbol("BTC").build()

    # Generate orderbook data
    orderbook_data = GmocoinDataFactory.orderbook().with_symbol("ETH").build()

    # Generate complete API response with metadata
    response_json = GmocoinDataFactory.message().with_ticker_data(
        GmocoinDataFactory.ticker().build()
    ).to_json()

    # Generate maintenance error response
    maintenance_json = GmocoinDataFactory.message().maintenance_preset().to_json()
"""

from __future__ import annotations

import json
from typing import Any

from .base import BaseDataValidator, BaseTestDataBuilder, TestDataConfig


class GmocoinDataValidator(BaseDataValidator):
    """Validator for GMO Coin test data"""

    VALID_SYMBOLS: list[str] = [
        "BTC",
        "ETH",
        "BCH",
        "LTC",
        "XRP",
        "XEM",
        "XLM",
        "BAT",
        "OMG",
        "XTZ",
        "QTUM",
        "ENJ",
        "DOT",
        "ATOM",
        "MKR",
        "DAI",
        "LINK",
        "DOGE",
        "SOL",
        "ASTR",
        "ADA",
        "FIL",
        "SAND",
        "CHZ",
    ]

    SUCCESS_STATUS: int = 0
    MAINTENANCE_STATUS: int = 5


class GmocoinTickerBuilder(BaseTestDataBuilder):
    """Builder for GMO Coin ticker data"""

    def _initialize_defaults(self) -> None:
        self._data = {
            "ask": "750760",
            "bid": "750600",
            "high": "762302",
            "last": "756662",
            "low": "704874",
            "symbol": "BTC",
            "timestamp": "2018-03-30T12:34:56.789Z",
            "volume": "194785.8484",
        }

    def build(self) -> dict[str, Any]:
        return dict(self._data)

    def with_symbol(self, symbol: str) -> GmocoinTickerBuilder:
        return self._set_field("symbol", symbol)

    def with_prices(
        self,
        *,
        ask: str,
        bid: str,
        high: str | None = None,
        last: str | None = None,
        low: str | None = None,
    ) -> GmocoinTickerBuilder:
        self._data["ask"] = ask
        self._data["bid"] = bid
        if high is not None:
            self._data["high"] = high
        if last is not None:
            self._data["last"] = last
        if low is not None:
            self._data["low"] = low
        return self

    def with_volume(self, volume: str) -> GmocoinTickerBuilder:
        return self._set_field("volume", volume)

    def with_timestamp(self, timestamp: str) -> GmocoinTickerBuilder:
        return self._set_field("timestamp", timestamp)

    def minimal(self) -> GmocoinTickerBuilder:
        """Set minimal valid values"""
        self._data = {
            "ask": "1",
            "bid": "1",
            "high": "1",
            "last": "1",
            "low": "1",
            "symbol": "BTC",
            "timestamp": "2023-01-01T00:00:00.000Z",
            "volume": "0",
        }
        return self


class GmocoinOrderBookBuilder(BaseTestDataBuilder):
    """Builder for GMO Coin orderbook data"""

    def _initialize_defaults(self) -> None:
        self._data = {
            "asks": [
                {"price": "455659", "size": "0.1"},
            ],
            "bids": [
                {"price": "455650", "size": "0.2"},
            ],
            "symbol": "BTC",
        }

    def build(self) -> dict[str, Any]:
        return dict(self._data)

    def with_symbol(self, symbol: str) -> GmocoinOrderBookBuilder:
        return self._set_field("symbol", symbol)

    def with_asks(self, asks: list[dict[str, str]]) -> GmocoinOrderBookBuilder:
        return self._set_field("asks", asks)

    def with_bids(self, bids: list[dict[str, str]]) -> GmocoinOrderBookBuilder:
        return self._set_field("bids", bids)

    def empty(self) -> GmocoinOrderBookBuilder:
        """Set empty asks and bids"""
        self._data["asks"] = []
        self._data["bids"] = []
        return self


class GmocoinMessageBuilder(BaseTestDataBuilder):
    """Builder for complete GMO Coin API response (with metadata)"""

    def _initialize_defaults(self) -> None:
        self._data = {
            "status": GmocoinDataValidator.SUCCESS_STATUS,
            "data": [],
            "responsetime": "2025-01-30T12:34:56.789Z",
        }

    def build(self) -> dict[str, Any]:
        return dict(self._data)

    def with_status(self, status: int) -> GmocoinMessageBuilder:
        return self._set_field("status", status)

    def with_data(self, data: Any) -> GmocoinMessageBuilder:
        return self._set_field("data", data)

    def with_ticker_data(self, *tickers: dict[str, Any]) -> GmocoinMessageBuilder:
        """Set data field with ticker array"""
        return self._set_field("data", list(tickers))

    def with_orderbook_data(self, orderbook: dict[str, Any]) -> GmocoinMessageBuilder:
        """Set data field with orderbook object"""
        return self._set_field("data", orderbook)

    def with_responsetime(self, responsetime: str) -> GmocoinMessageBuilder:
        return self._set_field("responsetime", responsetime)

    def maintenance_preset(self) -> GmocoinMessageBuilder:
        """Set maintenance error response (actual observed response)"""
        self._data = {
            "status": GmocoinDataValidator.MAINTENANCE_STATUS,
            "messages": [
                {
                    "message_code": "ERR-5201",
                    "message_string": "MAINTENANCE. Please wait for a while",
                }
            ],
        }
        return self

    def error_preset(
        self, *, status: int = 1, code: str = "ERR-0001", message: str = "System error"
    ) -> GmocoinMessageBuilder:
        """Set generic error response"""
        self._data = {
            "status": status,
            "messages": [
                {
                    "message_code": code,
                    "message_string": message,
                }
            ],
        }
        return self


class GmocoinDataFactory:
    """Factory class for creating GMO Coin test data builders

    Usage::

        # Ticker
        data = GmocoinDataFactory.ticker().with_symbol("ETH").build()
        json_str = GmocoinDataFactory.ticker().to_json()

        # OrderBook
        data = GmocoinDataFactory.orderbook().with_symbol("BTC").build()

        # Complete API response
        json_str = GmocoinDataFactory.message().with_ticker_data(
            GmocoinDataFactory.ticker().build()
        ).to_json()

        # Maintenance response
        json_str = GmocoinDataFactory.message().maintenance_preset().to_json()
    """

    __test__ = False  # Exclude from pytest collection

    @staticmethod
    def ticker(config: TestDataConfig | None = None) -> GmocoinTickerBuilder:
        return GmocoinTickerBuilder(config)

    @staticmethod
    def orderbook(config: TestDataConfig | None = None) -> GmocoinOrderBookBuilder:
        return GmocoinOrderBookBuilder(config)

    @staticmethod
    def message(config: TestDataConfig | None = None) -> GmocoinMessageBuilder:
        return GmocoinMessageBuilder(config)

    @staticmethod
    def ticker_response_json(
        *tickers: dict[str, Any],
        config: TestDataConfig | None = None,
    ) -> str:
        """Convenience method: generate complete ticker API response JSON"""
        msg = GmocoinMessageBuilder(config)
        msg.with_ticker_data(*tickers)
        return msg.to_json()

    @staticmethod
    def orderbook_response_json(
        orderbook: dict[str, Any],
        config: TestDataConfig | None = None,
    ) -> str:
        """Convenience method: generate complete orderbook API response JSON"""
        msg = GmocoinMessageBuilder(config)
        msg.with_orderbook_data(orderbook)
        return msg.to_json()

    @staticmethod
    def maintenance_response_json() -> str:
        """Convenience method: generate maintenance response JSON"""
        return json.dumps(
            {
                "status": GmocoinDataValidator.MAINTENANCE_STATUS,
                "messages": [
                    {
                        "message_code": "ERR-5201",
                        "message_string": "MAINTENANCE. Please wait for a while",
                    }
                ],
            }
        )
