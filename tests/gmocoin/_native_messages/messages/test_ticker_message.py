"""Tests for GMO Coin TickerMessage."""

import json
from decimal import Decimal

import pytest

from crypto_api_client.gmocoin._native_messages import TickerMessage
from crypto_api_client.gmocoin.native_domain_models import Ticker


class TestTickerMessage:
    """Tests for TickerMessage."""

    def test_single_ticker_returns_list(self) -> None:
        """Test that single ticker data returns a list with one element."""
        json_str = json.dumps(
            {
                "status": 0,
                "data": [
                    {
                        "ask": "5000000",
                        "bid": "4999000",
                        "high": "5100000",
                        "last": "4999500",
                        "low": "4900000",
                        "symbol": "BTC_JPY",
                        "timestamp": "2023-01-01T00:00:00.000Z",
                        "volume": "123.456",
                    }
                ],
                "responsetime": "2023-01-01T00:00:00.000Z",
            }
        )

        message = TickerMessage(json_str)
        result = message.to_domain_model()

        # Always returns a list
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Ticker)
        assert str(result[0].symbol) == "BTC_JPY"
        assert result[0].last == Decimal("4999500")

    def test_multiple_tickers_returns_list(self) -> None:
        """Test that multiple ticker data returns a list."""
        json_str = json.dumps(
            {
                "status": 0,
                "data": [
                    {
                        "ask": "5000000",
                        "bid": "4999000",
                        "high": "5100000",
                        "last": "4999500",
                        "low": "4900000",
                        "symbol": "BTC_JPY",
                        "timestamp": "2023-01-01T00:00:00.000Z",
                        "volume": "123.456",
                    },
                    {
                        "ask": "300000",
                        "bid": "299000",
                        "high": "310000",
                        "last": "299500",
                        "low": "290000",
                        "symbol": "ETH_JPY",
                        "timestamp": "2023-01-01T00:00:00.000Z",
                        "volume": "456.789",
                    },
                ],
                "responsetime": "2023-01-01T00:00:00.000Z",
            }
        )

        message = TickerMessage(json_str)
        result = message.to_domain_model()

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(t, Ticker) for t in result)
        assert str(result[0].symbol) == "BTC_JPY"
        assert str(result[1].symbol) == "ETH_JPY"

    def test_empty_data_returns_empty_list(self) -> None:
        """Test that empty data array returns empty list."""
        json_str = json.dumps(
            {"status": 0, "data": [], "responsetime": "2023-01-01T00:00:00.000Z"}
        )

        message = TickerMessage(json_str)
        result = message.to_domain_model()

        assert isinstance(result, list)
        assert len(result) == 0


    def test_non_list_data_raises_error(self) -> None:
        """Test that non-list data raises ValueError."""
        # When data is a single object (API specification violation)
        json_str = json.dumps(
            {
                "status": 0,
                "data": {
                    "ask": "5000000",
                    "bid": "4999000",
                    "high": "5100000",
                    "last": "4999500",
                    "low": "4900000",
                    "symbol": "BTC_JPY",
                    "timestamp": "2023-01-01T00:00:00.000Z",
                    "volume": "123.456",
                },
                "responsetime": "2023-01-01T00:00:00.000Z",
            }
        )

        message = TickerMessage(json_str)

        with pytest.raises(ValueError) as exc_info:
            message.to_domain_model()

        assert "not in expected array format" in str(exc_info.value)
        assert "dict" in str(exc_info.value)
