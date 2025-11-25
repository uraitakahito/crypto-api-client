"""Tests for TickerMessage"""

from decimal import Decimal

import pytest

from crypto_api_client.bitflyer._native_messages.ticker_message import TickerMessage
from crypto_api_client.bitflyer.native_domain_models.ticker import Ticker


class TestTickerMessage:
    """Tests for TickerMessage class"""

    @pytest.fixture
    def valid_ticker_json(self) -> str:
        """Valid ticker JSON data"""
        return """{
            "product_code": "BTC_JPY",
            "state": "RUNNING",
            "timestamp": "2015-07-08T02:50:59.97",
            "tick_id": 3579,
            "best_bid": 30000,
            "best_ask": 36640,
            "best_bid_size": 0.1,
            "best_ask_size": 5,
            "total_bid_depth": 15.13,
            "total_ask_depth": 20,
            "market_bid_size": 0,
            "market_ask_size": 0,
            "ltp": 31690,
            "volume": 16819.26,
            "volume_by_product": 6819.26
        }"""

    def test_init_with_valid_json(self, valid_ticker_json: str) -> None:
        """Test initialization with valid JSON"""
        message = TickerMessage(valid_ticker_json)

        assert message.metadata is None
        assert message.payload is not None
        assert message.payload.content_str == valid_ticker_json

    def test_to_domain_model(self, valid_ticker_json: str) -> None:
        """Test conversion to domain model"""
        message = TickerMessage(valid_ticker_json)

        ticker = message.to_domain_model()
        assert isinstance(ticker, Ticker)
        assert str(ticker.product_code) == "BTC_JPY"
        assert ticker.state == "RUNNING"
        # Verify Decimal type values directly
        assert ticker.best_bid == Decimal("30000")
        assert ticker.best_ask == Decimal("36640")
        assert ticker.ltp == Decimal("31690")

    def test_to_domain_model_consistency(self, valid_ticker_json: str) -> None:
        """Test consistency of to_domain_model method"""
        message = TickerMessage(valid_ticker_json)

        ticker_1 = message.to_domain_model()
        ticker_2 = message.to_domain_model()

        # Verify same values are returned
        assert str(ticker_1.product_code) == str(ticker_2.product_code)
        assert ticker_1.ltp == ticker_2.ltp
