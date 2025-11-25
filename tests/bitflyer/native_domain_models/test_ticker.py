"""Tests for Ticker model

Implements tests for JSON conversion using DecimalJsonParser and Ticker product_code validation functionality.
"""

import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from crypto_api_client.bitflyer.native_domain_models.ticker import Ticker
from crypto_api_client.core.decimal_json_parser import DecimalJsonParser
from tests.common.test_data_factory import BitFlyerDataFactory


class TestTickerProductCode:
    """Validation tests for Ticker's product_code field"""

    def test_product_code_validation_with_valid_string(self) -> None:
        ticker_data = BitFlyerDataFactory.ticker().build()

        ticker = Ticker(**ticker_data)
        # product_code is a string
        assert ticker.product_code == "BTC_JPY"

    def test_product_code_validation_with_string_instance(self) -> None:
        """Normal case: when product_code is specified as a string"""
        ticker_data = BitFlyerDataFactory.ticker().with_product_code("ETH_JPY").build()

        ticker = Ticker(**ticker_data)
        # product_code is a string
        assert ticker.product_code == "ETH_JPY"

    def test_product_code_validation_with_invalid_string(self) -> None:
        """Normal case: arbitrary strings (without underscore) are also allowed"""
        from tests.common.test_data_factory.base import TestDataConfig

        config = TestDataConfig(use_api_spec_validation=False)  # Disable validation
        ticker_data = (
            BitFlyerDataFactory.ticker(config)
            .invalid("product_code", "INVALID")
            .build()
        )

        # Any string value is allowed
        ticker = Ticker(**ticker_data)
        assert ticker.product_code == "INVALID"

    def test_product_code_validation_with_none(self) -> None:
        """Error case: None value"""
        ticker_data = BitFlyerDataFactory.ticker().build()
        ticker_data["product_code"] = None

        with pytest.raises(ValidationError):
            Ticker(**ticker_data)

    def test_product_code_validation_with_number(self) -> None:
        """Error case: numeric value"""
        ticker_data = BitFlyerDataFactory.ticker().build()
        ticker_data["product_code"] = 123

        with pytest.raises(ValidationError):
            Ticker(**ticker_data)


class TestTickerFromJson:
    """Tests for Ticker JSON conversion using DecimalJsonParser"""

    def test_from_json_success(self) -> None:
        """Normal case: Generate Ticker instance from valid JSON data"""
        json_data = BitFlyerDataFactory.ticker().to_json()

        ticker = DecimalJsonParser.parse(json_data, Ticker)

        # Verify basic fields
        assert isinstance(ticker, Ticker)
        assert str(ticker.product_code) == "BTC_JPY"
        assert ticker.state == "RUNNING"
        assert isinstance(ticker.timestamp, datetime.datetime)
        assert isinstance(ticker.tick_id, int)
        assert isinstance(ticker.best_bid, Decimal)
        assert isinstance(ticker.best_ask, Decimal)
        assert isinstance(ticker.best_bid_size, Decimal)
        assert isinstance(ticker.best_ask_size, Decimal)
        assert isinstance(ticker.ltp, Decimal)
        assert isinstance(ticker.volume, Decimal)
        assert isinstance(ticker.volume_by_product, Decimal)

    def test_from_json_with_different_product_code(self) -> None:
        """Normal case: Verify operation with different product_code"""
        json_data = (
            BitFlyerDataFactory.ticker()
            .with_product_code("ETH_JPY")
            .with_prices(ltp="500500.0", bid="500000.0", ask="501000.0")
            .with_timestamp("2025-02-27T14:00:00.000")
            .with_tick_id("123456789")
            .with_volume("100.0")
            .to_json()
        )

        ticker = DecimalJsonParser.parse(json_data, Ticker)
        assert str(ticker.product_code) == "ETH_JPY"

    def test_from_json_with_tick_id_as_number(self) -> None:
        """Normal case: when tick_id is a number"""
        # Manually create JSON to verify numeric tick_id
        json_str = """{
            "product_code": "BTC_JPY",
            "state": "RUNNING",
            "timestamp": "2025-02-27T13:50:43.957",
            "tick_id": 243332856,
            "best_bid": 12860000.0,
            "best_ask": 12870464.0,
            "best_bid_size": 0.1385912,
            "best_ask_size": 0.0106,
            "total_bid_depth": 123.24202636,
            "total_ask_depth": 279.49970104,
            "market_bid_size": 0.0,
            "market_ask_size": 0.0,
            "ltp": 12872459.0,
            "volume": 5691.9186518,
            "volume_by_product": 2042.29972298
        }"""

        ticker = DecimalJsonParser.parse(json_str, Ticker)
        assert ticker.tick_id == 243332856  # Stored as int type
        assert isinstance(ticker.tick_id, int)

    def test_from_json_invalid_json_format(self) -> None:
        """Error case: invalid JSON format"""
        invalid_json = '{"product_code": "BTC_JPY", "invalid": json}'

        with pytest.raises(ValueError):
            DecimalJsonParser.parse(invalid_json, Ticker)

    def test_from_json_missing_required_field(self) -> None:
        """Error case: missing required fields"""
        # Create JSON with minimal fields only
        incomplete_json = """{
            "product_code": "BTC_JPY",
            "state": "RUNNING"
        }"""

        with pytest.raises(ValidationError):
            DecimalJsonParser.parse(incomplete_json, Ticker)

    # test_from_json_invalid_product_code has been removed
    # product_code is now a plain string field without validation

    def test_from_json_invalid_decimal_field(self) -> None:
        """Error case: invalid value for Decimal field"""
        from tests.common.test_data_factory.base import TestDataConfig

        config = TestDataConfig(use_api_spec_validation=False)  # Disable validation
        ticker_data = BitFlyerDataFactory.ticker(config).build()
        ticker_data["best_bid"] = "invalid_decimal"

        # Manually create JSON since to_json() processes Decimal correctly
        import json

        json_data = json.dumps(ticker_data, default=str)

        with pytest.raises(ValidationError):
            DecimalJsonParser.parse(json_data, Ticker)

    def test_from_json_empty_string(self) -> None:
        """Error case: empty string"""
        with pytest.raises(ValueError):
            DecimalJsonParser.parse("", Ticker)


class TestTickerTimestampValidation:
    """Tests for Ticker timestamp processing

    Since bitFlyer's API returns timestamps in ISO format without timezone information,
    verify that they are correctly converted to UTC aware datetime.
    """

    def test_timestamp_naive_to_utc_aware(self) -> None:
        """Normal case: naive datetime is converted to UTC aware datetime"""
        # JSON in the format returned by bitFlyer's API (without timezone information)
        json_str = """{
            "product_code": "BTC_JPY",
            "state": "RUNNING",
            "timestamp": "2025-09-15T08:30:00.000",
            "tick_id": 243332856,
            "best_bid": 12860000.0,
            "best_ask": 12870464.0,
            "best_bid_size": 0.1385912,
            "best_ask_size": 0.0106,
            "total_bid_depth": 123.24202636,
            "total_ask_depth": 279.49970104,
            "market_bid_size": 0.0,
            "market_ask_size": 0.0,
            "ltp": 12872459.0,
            "volume": 5691.9186518,
            "volume_by_product": 2042.29972298
        }"""

        ticker = DecimalJsonParser.parse(json_str, Ticker)

        # Verify timestamp is aware datetime
        assert ticker.timestamp.tzinfo is not None
        assert ticker.timestamp.tzinfo == datetime.UTC

        # Verify time is parsed correctly
        expected = datetime.datetime(2025, 9, 15, 8, 30, 0, 0, tzinfo=datetime.UTC)
        assert ticker.timestamp == expected

    def test_timestamp_with_microseconds(self) -> None:
        """Normal case: timestamp with microseconds is processed correctly"""
        json_str = """{
            "product_code": "BTC_JPY",
            "state": "RUNNING",
            "timestamp": "2025-09-15T08:30:45.123456",
            "tick_id": 243332856,
            "best_bid": 12860000.0,
            "best_ask": 12870464.0,
            "best_bid_size": 0.1385912,
            "best_ask_size": 0.0106,
            "total_bid_depth": 123.24202636,
            "total_ask_depth": 279.49970104,
            "market_bid_size": 0.0,
            "market_ask_size": 0.0,
            "ltp": 12872459.0,
            "volume": 5691.9186518,
            "volume_by_product": 2042.29972298
        }"""

        ticker = DecimalJsonParser.parse(json_str, Ticker)

        # Verify timestamp is aware datetime
        assert ticker.timestamp.tzinfo is not None
        assert ticker.timestamp.tzinfo == datetime.UTC

        # Verify microseconds are preserved
        assert ticker.timestamp.microsecond == 123456

    def test_timestamp_timezone_conversion(self) -> None:
        """Normal case: conversion from UTC aware datetime to other timezones works correctly"""
        from zoneinfo import ZoneInfo

        json_str = """{
            "product_code": "BTC_JPY",
            "state": "RUNNING",
            "timestamp": "2025-09-15T08:30:00.000",
            "tick_id": 243332856,
            "best_bid": 12860000.0,
            "best_ask": 12870464.0,
            "best_bid_size": 0.1385912,
            "best_ask_size": 0.0106,
            "total_bid_depth": 123.24202636,
            "total_ask_depth": 279.49970104,
            "market_bid_size": 0.0,
            "market_ask_size": 0.0,
            "ltp": 12872459.0,
            "volume": 5691.9186518,
            "volume_by_product": 2042.29972298
        }"""

        ticker = DecimalJsonParser.parse(json_str, Ticker)

        # Convert to JST
        jst_time = ticker.timestamp.astimezone(ZoneInfo("Asia/Tokyo"))

        # Verify JST time is correct (UTC+9 hours)
        expected_jst = datetime.datetime(
            2025, 9, 15, 17, 30, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo")
        )
        assert jst_time == expected_jst

        # Verify conversion to other timezones
        est_time = ticker.timestamp.astimezone(ZoneInfo("America/New_York"))
        expected_est = datetime.datetime(
            2025, 9, 15, 4, 30, 0, 0, tzinfo=ZoneInfo("America/New_York")
        )
        assert est_time == expected_est

    def test_timestamp_already_aware(self) -> None:
        """Normal case: if already aware datetime, it is preserved as is"""
        # Test for when API returns with timezone information
        json_str = """{
            "product_code": "BTC_JPY",
            "state": "RUNNING",
            "timestamp": "2025-09-15T08:30:00.000+00:00",
            "tick_id": 243332856,
            "best_bid": 12860000.0,
            "best_ask": 12870464.0,
            "best_bid_size": 0.1385912,
            "best_ask_size": 0.0106,
            "total_bid_depth": 123.24202636,
            "total_ask_depth": 279.49970104,
            "market_bid_size": 0.0,
            "market_ask_size": 0.0,
            "ltp": 12872459.0,
            "volume": 5691.9186518,
            "volume_by_product": 2042.29972298
        }"""

        ticker = DecimalJsonParser.parse(json_str, Ticker)

        # Verify timestamp is aware datetime
        assert ticker.timestamp.tzinfo is not None
        # Verify it is processed as UTC
        assert ticker.timestamp.utcoffset() == datetime.timedelta(0)
