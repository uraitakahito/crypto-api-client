"""Tests for DecimalJsonParser.

Verifies that the decimal_json_parser module raises exceptions correctly.
"""

import json
from decimal import Decimal

import pytest
from pydantic import ValidationError

from crypto_api_client.bitflyer.native_domain_models.ticker import Ticker
from crypto_api_client.core.decimal_json_parser import DecimalJsonParser
from tests.common.test_data_factory.common_factory import CommonDataFactory


class TestDecimalJsonParser:
    """Tests for DecimalJsonParser class."""

    def setup_method(self) -> None:
        """Test setup."""
        self.factory = CommonDataFactory()

    def test_parse_success(self) -> None:
        """Test successful JSON parsing (no exception raised)."""
        ticker_json = self.factory.create_ticker_data()

        # Verify no exception is raised
        ticker = DecimalJsonParser.parse(json.dumps(ticker_json), Ticker)

        assert str(ticker.product_code) == "BTC_JPY"
        # best_bid is Decimal type
        assert isinstance(ticker.best_bid, Decimal)

    def test_parse_error(self) -> None:
        """Verify exception is raised for invalid JSON."""
        # Verify exception is raised
        with pytest.raises(ValueError):
            DecimalJsonParser.parse("invalid json", Ticker)

    def test_parse_validation_error(self) -> None:
        """Verify exception is raised for validation errors."""
        invalid_ticker_json = {"invalid_field": "value"}

        # Verify ValidationError is raised
        with pytest.raises(ValidationError):
            DecimalJsonParser.parse(json.dumps(invalid_ticker_json), Ticker)

    def test_clear_cache(self) -> None:
        """Verify cache clearing works correctly."""
        # Create first adapter with complete Ticker data
        ticker_json = self.factory.create_ticker_data()

        # First create adapter and save to cache
        DecimalJsonParser.parse(json.dumps(ticker_json), Ticker)

        # Clear cache
        DecimalJsonParser.clear_cache()

        # Verify cache is cleared (test doesn't depend on internal implementation)
        # Verify creating adapter with same type again works fine
        ticker_json["product_code"] = "ETH_JPY"
        DecimalJsonParser.parse(json.dumps(ticker_json), Ticker)

    def test_decimal_precision_preserved(self) -> None:
        """Verify Decimal precision is preserved."""
        ticker_json = self.factory.create_ticker_data()
        # Set high precision number as string (to avoid JSON numeric precision limits)
        ticker_json["best_bid"] = "123456789.123456789123456789"

        ticker = DecimalJsonParser.parse(json.dumps(ticker_json), Ticker)

        # Verify precision is preserved as Decimal type
        assert isinstance(ticker.best_bid, Decimal)
        assert str(ticker.best_bid) == "123456789.123456789123456789"
