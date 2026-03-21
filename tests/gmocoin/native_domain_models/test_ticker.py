"""Tests for GMO Coin Ticker domain model"""

# pyright: reportArgumentType=false

import datetime
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser
from crypto_api_client.gmocoin.native_domain_models.ticker import Ticker
from tests.common.test_data_factory import GmocoinDataFactory


class TestTicker:
    """Tests for Ticker model"""

    @pytest.fixture
    def valid_ticker_data(self) -> dict[str, Any]:
        """Valid ticker data based on official API documentation"""
        return GmocoinDataFactory.ticker().build()

    def test_init_with_valid_data(self, valid_ticker_data: dict[str, Any]) -> None:
        """Test initialization with valid API response data"""
        ticker = Ticker(**valid_ticker_data)

        assert ticker.symbol == "BTC"
        assert ticker.ask == Decimal("750760")
        assert ticker.bid == Decimal("750600")
        assert ticker.high == Decimal("762302")
        assert ticker.last == Decimal("756662")
        assert ticker.low == Decimal("704874")
        assert ticker.volume == Decimal("194785.8484")
        assert isinstance(ticker.timestamp, datetime.datetime)

    def test_str_to_decimal_conversion(self) -> None:
        """Test that string values are converted to Decimal"""
        data = (
            GmocoinDataFactory.ticker()
            .with_symbol("ETH")
            .with_prices(
                ask="123.456789",
                bid="123.456788",
                high="130.0",
                last="125.5",
                low="120.0",
            )
            .with_volume("999.12345678")
            .build()
        )
        ticker = Ticker(**data)

        assert ticker.ask == Decimal("123.456789")
        assert ticker.volume == Decimal("999.12345678")
        assert isinstance(ticker.ask, Decimal)
        assert isinstance(ticker.volume, Decimal)

    def test_decimal_values_passed_directly(self) -> None:
        """Test initialization with Decimal values directly"""
        data: dict[str, Any] = {
            "ask": Decimal("750760"),
            "bid": Decimal("750600"),
            "high": Decimal("762302"),
            "last": Decimal("756662"),
            "low": Decimal("704874"),
            "symbol": "BTC",
            "timestamp": "2018-03-30T12:34:56.789Z",
            "volume": Decimal("194785.8484"),
        }
        ticker = Ticker(**data)

        assert ticker.ask == Decimal("750760")
        assert ticker.volume == Decimal("194785.8484")

    def test_zero_values(self) -> None:
        """Test with zero price/volume values"""
        data = (
            GmocoinDataFactory.ticker()
            .with_prices(ask="0", bid="0", high="0", last="0", low="0")
            .with_volume("0")
            .build()
        )
        ticker = Ticker(**data)

        assert ticker.ask == Decimal("0")
        assert ticker.volume == Decimal("0")

    def test_large_values(self) -> None:
        """Test with large values"""
        data = (
            GmocoinDataFactory.ticker()
            .with_prices(
                ask="99999999999",
                bid="99999999998",
                high="99999999999",
                last="99999999999",
                low="1",
            )
            .with_volume("999999999.999999999")
            .build()
        )
        ticker = Ticker(**data)

        assert ticker.ask == Decimal("99999999999")
        assert ticker.volume == Decimal("999999999.999999999")

    def test_timestamp_is_utc_aware(self, valid_ticker_data: dict[str, Any]) -> None:
        """Test that timestamp is UTC-aware datetime"""
        ticker = Ticker(**valid_ticker_data)

        assert ticker.timestamp.tzinfo is not None

    def test_frozen_model(self, valid_ticker_data: dict[str, Any]) -> None:
        """Test that model is immutable"""
        ticker = Ticker(**valid_ticker_data)

        with pytest.raises(ValidationError):
            ticker.symbol = "ETH"  # type: ignore[misc]

    def test_missing_required_field(self) -> None:
        """Test that missing required fields raise ValidationError"""
        with pytest.raises(ValidationError):
            Ticker(
                ask="100",
                bid="99",
                high="110",
            )  # type: ignore[call-arg]

    def test_parse_from_json(self, valid_ticker_data: dict[str, Any]) -> None:
        """Test parsing from JSON via DecimalJsonParser"""
        json_str = GmocoinDataFactory.ticker().to_json()
        ticker = DecimalJsonParser.parse(json_str, Ticker)

        assert isinstance(ticker, Ticker)
        assert ticker.symbol == "BTC"
        assert ticker.ask == Decimal("750760")

    def test_symbol_is_base_currency_code(self) -> None:
        """Test that symbol contains only base currency code (e.g., 'BTC'), not pair"""
        data = GmocoinDataFactory.ticker().minimal().with_symbol("BTC").build()
        ticker = Ticker(**data)
        assert ticker.symbol == "BTC"
