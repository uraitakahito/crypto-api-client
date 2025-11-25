"""Tests for TickerMessage."""

import datetime
from decimal import Decimal

import pytest

from crypto_api_client.bitbank._native_messages.message_metadata import (
    MessageMetadata,
)
from crypto_api_client.bitbank._native_messages.ticker_message import TickerMessage
from crypto_api_client.bitbank.native_domain_models import Ticker


class TestTickerMessage:
    """Tests for TickerMessage class."""

    @pytest.fixture
    def valid_ticker_json(self) -> str:
        """Valid ticker message JSON string."""
        return """{
            "success": 1,
            "data": {
                "sell": "15350001",
                "buy": "15350000",
                "open": "15572550",
                "high": "15836477",
                "low": "15271389",
                "last": "15350001",
                "vol": "273.5234",
                "timestamp": 1748558090326
            }
        }"""

    @pytest.fixture
    def zero_values_ticker_json(self) -> str:
        """Ticker message JSON string with zero values."""
        return """{
            "success": 1,
            "data": {
                "sell": "0",
                "buy": "0",
                "open": "0",
                "high": "0",
                "low": "0",
                "last": "0",
                "vol": "0",
                "timestamp": 0
            }
        }"""

    def test_init_with_valid_json(self, valid_ticker_json: str) -> None:
        """Test initialization with valid JSON."""
        message = TickerMessage(valid_ticker_json)

        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success == 1
        assert message.metadata.json_str == '{"success": 1}'
        assert message.payload is not None

    def test_to_domain_model(self, valid_ticker_json: str) -> None:
        """Test conversion to domain model."""
        message = TickerMessage(valid_ticker_json)

        ticker = message.to_domain_model()
        assert isinstance(ticker, Ticker)
        assert ticker.sell == Decimal("15350001")
        assert ticker.buy == Decimal("15350000")
        assert ticker.open == Decimal("15572550")
        assert ticker.high == Decimal("15836477")
        assert ticker.low == Decimal("15271389")
        assert ticker.last == Decimal("15350001")
        assert ticker.vol == Decimal("273.5234")

        # Timestamp is converted from milliseconds to datetime
        expected_dt = datetime.datetime.fromtimestamp(
            1748558090326 / 1000, tz=datetime.UTC
        )
        assert ticker.timestamp == expected_dt

    def test_to_domain_model_with_zero_values(
        self, zero_values_ticker_json: str
    ) -> None:
        """Test domain model conversion with zero values."""
        message = TickerMessage(zero_values_ticker_json)

        ticker = message.to_domain_model()
        assert ticker.sell == Decimal("0")
        assert ticker.buy == Decimal("0")
        assert ticker.open == Decimal("0")
        assert ticker.high == Decimal("0")
        assert ticker.low == Decimal("0")
        assert ticker.last == Decimal("0")
        assert ticker.vol == Decimal("0")

        # timestamp 0 is 1970-01-01 00:00:00 UTC
        expected_dt = datetime.datetime.fromtimestamp(0, tz=datetime.UTC)
        assert ticker.timestamp == expected_dt

    def test_init_missing_success_field(self) -> None:
        """Test error when success field is missing."""
        json_str = """{
            "data": {
                "sell": "15350001",
                "buy": "15350000",
                "open": "15572550",
                "high": "15836477",
                "low": "15271389",
                "last": "15350001",
                "vol": "273.5234",
                "timestamp": 1748558090326
            }
        }"""

        message = TickerMessage(json_str)
        with pytest.raises(
            ValueError,
            match="metadata \\('success' field\\) not found",
        ):
            _ = message.metadata

    def test_init_missing_data_field(self) -> None:
        """Test error when data field is missing."""
        json_str = """{
            "success": 1
        }"""

        message = TickerMessage(json_str)
        with pytest.raises(ValueError, match="Field 'data' not found"):
            _ = message.payload

    def test_extract_brace_content_with_whitespace(self) -> None:
        """Test JSON processing with whitespace."""
        json_str = """{
            "success"  :  1  ,
            "data"   :   {
                "sell": "15350001",
                "buy": "15350000",
                "open": "15572550",
                "high": "15836477",
                "low": "15271389",
                "last": "15350001",
                "vol": "273.5234",
                "timestamp": 1748558090326
            }
        }"""

        message = TickerMessage(json_str)
        # Whitespace is preserved
        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success == 1
        ticker = message.to_domain_model()
        assert ticker.sell == Decimal("15350001")

    def test_failure_response(self) -> None:
        """Test processing of failure message (success: 0)."""
        json_str = """{
            "success": 0,
            "data": {
                "sell": "0",
                "buy": "0",
                "open": "0",
                "high": "0",
                "low": "0",
                "last": "0",
                "vol": "0",
                "timestamp": 0
            }
        }"""

        message = TickerMessage(json_str)
        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success == 0
        assert message.metadata.json_str == '{"success": 0}'

        # Parsing is possible even with success: 0
        ticker = message.to_domain_model()
        assert isinstance(ticker, Ticker)

    def test_invalid_json_structure(self) -> None:
        """Test error with invalid JSON structure."""
        # Data brace is not closed
        json_str = """{
            "success": 1,
            "data": {"""  # Missing closing brace for data

        # Invalid structure causes data field extraction to fail
        message = TickerMessage(json_str)
        with pytest.raises(ValueError, match="Closing brace not found"):
            _ = message.payload

    def test_ticker_frozen_model(self) -> None:
        """Test Ticker model immutability."""
        message = TickerMessage("""{
            "success": 1,
            "data": {
                "sell": "15350001",
                "buy": "15350000",
                "open": "15572550",
                "high": "15836477",
                "low": "15271389",
                "last": "15350001",
                "vol": "273.5234",
                "timestamp": 1748558090326
            }
        }""")

        ticker = message.to_domain_model()

        # Ticker model is frozen=True so cannot be modified
        from pydantic import ValidationError

        # Rate type is frozen and cannot be modified
        with pytest.raises(ValidationError):
            ticker.sell = ticker.sell  # Assignment itself is not allowed
