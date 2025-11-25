"""Tests for BINANCE Ticker domain model."""

import datetime
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from crypto_api_client.binance.native_domain_models import Ticker


class TestTicker:
    """Test class for Ticker model."""

    def test_ticker_creation_with_valid_data(self) -> None:
        """Test that Ticker can be created with valid data."""
        data: dict[str, Any] = {
            "symbol": "BTCUSDT",
            "priceChange": "-154.13000000",
            "priceChangePercent": "-0.740",
            "weightedAvgPrice": "20677.46305250",
            "prevClosePrice": "20825.27000000",
            "lastPrice": "20671.14000000",
            "lastQty": "0.00030000",
            "bidPrice": "20671.13000000",
            "bidQty": "0.05000000",
            "askPrice": "20671.14000000",
            "askQty": "0.94620000",
            "openPrice": "20825.27000000",
            "highPrice": "20972.46000000",
            "lowPrice": "20327.92000000",
            "volume": "72.65112300",
            "quoteVolume": "1502240.91155513",
            "openTime": 1655432400000,
            "closeTime": 1655446835460,
            "firstId": 11147809,
            "lastId": 11149775,
            "count": 1967,
        }

        ticker = Ticker(**data)

        assert str(ticker.symbol) == "BTCUSDT"
        assert ticker.priceChange == Decimal("-154.13000000")
        assert ticker.priceChangePercent == Decimal("-0.740")
        assert ticker.lastPrice == Decimal("20671.14000000")
        assert ticker.bidPrice == Decimal("20671.13000000")
        assert ticker.askPrice == Decimal("20671.14000000")
        assert ticker.volume == Decimal("72.65112300")
        assert ticker.count == 1967

        # Verify timestamps are converted to UTC datetime
        assert isinstance(ticker.openTime, datetime.datetime)
        assert isinstance(ticker.closeTime, datetime.datetime)
        assert ticker.openTime.tzinfo == datetime.UTC
        assert ticker.closeTime.tzinfo == datetime.UTC

    def test_ticker_frozen(self) -> None:
        """Test that Ticker is frozen."""
        data: dict[str, Any] = {
            "symbol": "BTCUSDT",
            "priceChange": "0",
            "priceChangePercent": "0",
            "weightedAvgPrice": "0",
            "prevClosePrice": "0",
            "lastPrice": "100",
            "lastQty": "0",
            "bidPrice": "0",
            "bidQty": "0",
            "askPrice": "0",
            "askQty": "0",
            "openPrice": "0",
            "highPrice": "0",
            "lowPrice": "0",
            "volume": "0",
            "quoteVolume": "0",
            "openTime": 1655432400000,
            "closeTime": 1655446835460,
            "firstId": "1",
            "lastId": "2",
            "count": 1,
        }

        ticker = Ticker(**data)

        # Verify that attributes cannot be changed because it is frozen
        with pytest.raises(ValidationError):
            ticker.lastPrice = Decimal("200")

    def test_ticker_trade_id_validation(self) -> None:
        """Test that trade IDs are processed correctly as integers."""
        # Integer values are preserved as-is
        data: dict[str, Any] = {
            "symbol": "BTCUSDT",
            "priceChange": "0",
            "priceChangePercent": "0",
            "weightedAvgPrice": "0",
            "prevClosePrice": "0",
            "lastPrice": "0",
            "lastQty": "0",
            "bidPrice": "0",
            "bidQty": "0",
            "askPrice": "0",
            "askQty": "0",
            "openPrice": "0",
            "highPrice": "0",
            "lowPrice": "0",
            "volume": "0",
            "quoteVolume": "0",
            "openTime": 1655432400000,
            "closeTime": 1655446835460,
            "firstId": 12345,  # Integer
            "lastId": 67890,  # Integer
            "count": 1,
        }

        ticker = Ticker(**data)
        assert ticker.firstId == 12345
        assert ticker.lastId == 67890

    def test_ticker_with_decimal_values(self) -> None:
        """Test that Decimal values are processed correctly."""
        # BINANCE API may convert large numbers to Decimal during JSON processing
        data: dict[str, Any] = {
            "symbol": "BTCUSDT",
            "priceChange": Decimal("-154.13000000"),
            "priceChangePercent": Decimal("-0.740"),
            "weightedAvgPrice": Decimal("20677.46305250"),
            "prevClosePrice": Decimal("20825.27000000"),
            "lastPrice": Decimal("20671.14000000"),
            "lastQty": Decimal("0.00030000"),
            "bidPrice": Decimal("20671.13000000"),
            "bidQty": Decimal("0.05000000"),
            "askPrice": Decimal("20671.14000000"),
            "askQty": Decimal("0.94620000"),
            "openPrice": Decimal("20825.27000000"),
            "highPrice": Decimal("20972.46000000"),
            "lowPrice": Decimal("20327.92000000"),
            "volume": Decimal("72.65112300"),
            "quoteVolume": Decimal("1502240.91155513"),
            "openTime": Decimal("1655432400000"),  # Decimal timestamp
            "closeTime": Decimal("1655446835460"),  # Decimal timestamp
            "firstId": Decimal("11147809"),  # Decimal ID
            "lastId": Decimal("11149775"),  # Decimal ID
            "count": 1967,
        }

        ticker = Ticker(**data)

        # Verify values are converted correctly
        assert ticker.lastPrice == Decimal("20671.14000000")
        assert ticker.firstId == 11147809
        assert ticker.lastId == 11149775
        assert isinstance(ticker.openTime, datetime.datetime)
        assert isinstance(ticker.closeTime, datetime.datetime)
