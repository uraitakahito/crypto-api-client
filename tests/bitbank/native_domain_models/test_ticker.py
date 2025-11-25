"""Ticker model tests"""
# pyright: reportArgumentType=false

import datetime
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from crypto_api_client.bitbank.native_domain_models.ticker import Ticker


class TestTicker:
    """Ticker class tests"""

    @pytest.fixture
    def valid_ticker_data(self) -> dict[str, Any]:
        """Valid ticker data"""
        return {
            "sell": "15350001",
            "buy": "15350000",
            "open": "15572550",
            "high": "15836477",
            "low": "15271389",
            "last": "15350001",
            "vol": "273.5234",
            "timestamp": 1748558090326,
        }

    @pytest.fixture
    def ticker_data_with_decimals(self) -> dict[str, Any]:
        """Ticker data already containing Decimal types"""
        return {
            "sell": Decimal("15350001"),
            "buy": Decimal("15350000"),
            "open": Decimal("15572550"),
            "high": Decimal("15836477"),
            "low": Decimal("15271389"),
            "last": Decimal("15350001"),
            "vol": Decimal("273.5234"),
            "timestamp": 1748558090326,
        }

    def test_init_with_valid_data(self, valid_ticker_data: dict[str, Any]) -> None:
        """Test initialization with valid data"""
        ticker = Ticker(**valid_ticker_data)

        # Verify Decimal type values directly
        assert ticker.sell == Decimal("15350001")
        assert ticker.buy == Decimal("15350000")
        assert ticker.open == Decimal("15572550")
        assert ticker.high == Decimal("15836477")
        assert ticker.low == Decimal("15271389")
        assert ticker.last == Decimal("15350001")
        assert ticker.vol == Decimal("273.5234")

        expected_dt = datetime.datetime.fromtimestamp(
            1748558090326 / 1000, tz=datetime.UTC
        )
        assert ticker.timestamp == expected_dt

    def test_init_with_decimal_values(
        self, ticker_data_with_decimals: dict[str, Any]
    ) -> None:
        """Test initialization with Decimal values"""
        ticker = Ticker(**ticker_data_with_decimals)

        assert ticker.sell == Decimal("15350001")
        assert ticker.buy == Decimal("15350000")
        assert ticker.vol == Decimal("273.5234")

    def test_convert_str_to_decimal(self) -> None:
        """Test conversion from string to Decimal"""
        data: dict[str, Any] = {
            "pair": "btc_jpy",  # Add currency pair information
            "sell": "123.456",
            "buy": "123.457",
            "open": "123.458",
            "high": "123.459",
            "low": "123.455",
            "last": "123.456",
            "vol": "1000.123",
            "timestamp": 1748558090326,
        }

        ticker = Ticker(**data)
        assert ticker.sell == Decimal("123.456")
        assert ticker.buy == Decimal("123.457")
        assert ticker.open == Decimal("123.458")
        assert ticker.high == Decimal("123.459")
        assert ticker.low == Decimal("123.455")
        assert ticker.last == Decimal("123.456")
        assert ticker.vol == Decimal("1000.123")

    def test_convert_timestamp_int(self) -> None:
        """Test conversion from int timestamp to datetime"""
        data: dict[str, Any] = {
            "pair": "btc_jpy",  # Add currency pair information
            "sell": "100",
            "buy": "100",
            "open": "100",
            "high": "100",
            "low": "100",
            "last": "100",
            "vol": "100",
            "timestamp": 1748558090326,  # Milliseconds
        }

        ticker = Ticker(**data)
        expected_dt = datetime.datetime.fromtimestamp(
            1748558090326 / 1000, tz=datetime.UTC
        )
        assert ticker.timestamp == expected_dt

    def test_convert_timestamp_float(self) -> None:
        """Test conversion from float timestamp to datetime"""
        data: dict[str, Any] = {
            "pair": "btc_jpy",  # Add currency pair information
            "sell": "100",
            "buy": "100",
            "open": "100",
            "high": "100",
            "low": "100",
            "last": "100",
            "vol": "100",
            "timestamp": 1748558090326.5,  # Milliseconds (with decimal)
        }

        ticker = Ticker(**data)
        expected_dt = datetime.datetime.fromtimestamp(
            1748558090326.5 / 1000, tz=datetime.UTC
        )
        assert ticker.timestamp == expected_dt

    def test_convert_timestamp_decimal(self) -> None:
        """Test conversion from Decimal timestamp to datetime"""
        data: dict[str, Any] = {
            "pair": "btc_jpy",  # Add currency pair information
            "sell": "100",
            "buy": "100",
            "open": "100",
            "high": "100",
            "low": "100",
            "last": "100",
            "vol": "100",
            "timestamp": Decimal("1748558090326"),  # Milliseconds (Decimal)
        }

        ticker = Ticker(**data)
        expected_dt = datetime.datetime.fromtimestamp(
            1748558090326 / 1000, tz=datetime.UTC
        )
        assert ticker.timestamp == expected_dt

    def test_convert_timestamp_zero(self) -> None:
        """Test conversion of zero timestamp"""
        data: dict[str, Any] = {
            "pair": "btc_jpy",  # Add currency pair information
            "sell": "100",
            "buy": "100",
            "open": "100",
            "high": "100",
            "low": "100",
            "last": "100",
            "vol": "100",
            "timestamp": 0,
        }

        ticker = Ticker(**data)
        expected_dt = datetime.datetime.fromtimestamp(0, tz=datetime.UTC)
        assert ticker.timestamp == expected_dt

    def test_with_timezone_tokyo(self) -> None:
        """Test conversion to Tokyo timezone"""
        ticker = Ticker(  # type: ignore[call-arg]
            sell="100",
            buy="100",
            open="100",
            high="100",
            low="100",
            last="100",
            vol=Decimal("100"),
            timestamp=datetime.datetime.fromtimestamp(
                1748558090326 / 1000, tz=datetime.UTC
            ),
        )

        tokyo_tz = ZoneInfo("Asia/Tokyo")
        ticker_tokyo = ticker.with_timezone(tokyo_tz)

        # Original ticker is unchanged
        assert ticker.timestamp.tzinfo == datetime.UTC

        # New ticker is in Tokyo time
        assert ticker_tokyo.timestamp.tzinfo == tokyo_tz

        # Represents the same time
        assert ticker.timestamp == ticker_tokyo.timestamp

        # Other fields are the same
        assert ticker_tokyo.sell == ticker.sell
        assert ticker_tokyo.buy == ticker.buy
        assert ticker_tokyo.vol == ticker.vol

    def test_with_timezone_newyork(self) -> None:
        """Test conversion to New York timezone"""
        ticker = Ticker(  # type: ignore[call-arg]
            sell="100",
            buy="100",
            open="100",
            high="100",
            low="100",
            last="100",
            vol=Decimal("100"),
            timestamp=datetime.datetime.fromtimestamp(
                1748558090326 / 1000, tz=datetime.UTC
            ),
        )

        ny_tz = ZoneInfo("America/New_York")
        ticker_ny = ticker.with_timezone(ny_tz)

        assert ticker_ny.timestamp.tzinfo == ny_tz
        assert ticker.timestamp == ticker_ny.timestamp

    def test_frozen_model(self) -> None:
        """Test model immutability"""
        ticker = Ticker(  # type: ignore[call-arg]
            sell="100",
            buy="100",
            open="100",
            high="100",
            low="100",
            last="100",
            vol=Decimal("100"),
            timestamp=datetime.datetime.fromtimestamp(
                1748558090326 / 1000, tz=datetime.UTC
            ),
        )

        # When trying to change Rate type value
        with pytest.raises(ValidationError):
            ticker.sell = ticker.sell  # Cannot modify frozen model

        with pytest.raises(ValidationError):
            ticker.timestamp = datetime.datetime.now(tz=datetime.UTC)

    def test_zero_values(self) -> None:
        """Test initialization with zero values"""
        data: dict[str, Any] = {
            "pair": "btc_jpy",  # Add currency pair information
            "sell": "0",
            "buy": "0",
            "open": "0",
            "high": "0",
            "low": "0",
            "last": "0",
            "vol": "0",
            "timestamp": 0,
        }

        ticker = Ticker(**data)
        assert ticker.sell == Decimal("0")
        assert ticker.buy == Decimal("0")
        assert ticker.open == Decimal("0")
        assert ticker.high == Decimal("0")
        assert ticker.low == Decimal("0")
        assert ticker.last == Decimal("0")
        assert ticker.vol == Decimal("0")

    def test_large_values(self) -> None:
        """Test initialization with large values"""
        data: dict[str, Any] = {
            "pair": "btc_jpy",  # Add currency pair information
            "sell": "99999999999.99999999",
            "buy": "99999999999.99999998",
            "open": "99999999999.99999997",
            "high": "99999999999.99999999",
            "low": "99999999999.99999996",
            "last": "99999999999.99999999",
            "vol": "99999999999.99999999",
            "timestamp": 9999999999999,  # Milliseconds
        }

        ticker = Ticker(**data)
        assert ticker.sell == Decimal("99999999999.99999999")
        assert ticker.high == Decimal("99999999999.99999999")

    def test_model_dump(self) -> None:
        """Test model serialization"""
        ticker = Ticker(  # type: ignore[call-arg]
            sell="100.5",
            buy="100.4",
            open="100.0",
            high="101.0",
            low="99.0",
            last="100.5",
            vol=Decimal("1000.0"),
            timestamp=datetime.datetime.fromtimestamp(
                1748558090326 / 1000, tz=datetime.UTC
            ),
        )

        dumped = ticker.model_dump()

        # Decimal type returns Decimal value as-is in model_dump
        assert dumped["sell"] == Decimal("100.5")
        assert dumped["buy"] == Decimal("100.4")
        assert dumped["vol"] == Decimal("1000.0")
        assert isinstance(dumped["timestamp"], datetime.datetime)

    def test_datetime_already_converted(self) -> None:
        """Test processing when already datetime type"""
        dt = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.UTC)
        data: dict[str, Any] = {
            "pair": "btc_jpy",  # Add currency pair information
            "sell": "100",
            "buy": "100",
            "open": "100",
            "high": "100",
            "low": "100",
            "last": "100",
            "vol": "100",
            "timestamp": dt,
        }

        ticker = Ticker(**data)
        assert ticker.timestamp == dt
