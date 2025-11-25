"""Tests for GMO Coin OrderBookMessage."""

import json
from decimal import Decimal

from crypto_api_client.gmocoin._native_messages import OrderBookMessage
from crypto_api_client.gmocoin.native_domain_models import OrderBook, OrderBookEntry


class TestOrderBookMessage:
    """Tests for OrderBookMessage."""

    def test_orderbook_with_asks_and_bids(self) -> None:
        """Test that orderbook data is correctly parsed into OrderBook model."""
        json_str = json.dumps(
            {
                "status": 0,
                "data": {
                    "asks": [
                        {"price": "5000100", "size": "0.1"},
                        {"price": "5000200", "size": "0.2"},
                    ],
                    "bids": [
                        {"price": "4999900", "size": "0.15"},
                        {"price": "4999800", "size": "0.25"},
                    ],
                    "symbol": "BTC",
                },
                "responsetime": "2023-01-01T00:00:00.000Z",
            }
        )

        message = OrderBookMessage(json_str)
        result = message.to_domain_model()

        assert isinstance(result, OrderBook)
        assert result.symbol == "BTC"

        # Check asks
        assert len(result.asks) == 2
        assert all(isinstance(e, OrderBookEntry) for e in result.asks)
        assert result.asks[0].price == Decimal("5000100")
        assert result.asks[0].size == Decimal("0.1")
        assert result.asks[1].price == Decimal("5000200")
        assert result.asks[1].size == Decimal("0.2")

        # Check bids
        assert len(result.bids) == 2
        assert all(isinstance(e, OrderBookEntry) for e in result.bids)
        assert result.bids[0].price == Decimal("4999900")
        assert result.bids[0].size == Decimal("0.15")
        assert result.bids[1].price == Decimal("4999800")
        assert result.bids[1].size == Decimal("0.25")

    def test_orderbook_properties(self) -> None:
        """Test OrderBook convenience properties."""
        json_str = json.dumps(
            {
                "status": 0,
                "data": {
                    "asks": [
                        {"price": "5000000", "size": "0.1"},
                    ],
                    "bids": [
                        {"price": "4999000", "size": "0.15"},
                    ],
                    "symbol": "BTC",
                },
                "responsetime": "2023-01-01T00:00:00.000Z",
            }
        )

        message = OrderBookMessage(json_str)
        result = message.to_domain_model()

        # Test best_ask
        assert result.best_ask is not None
        assert result.best_ask.price == Decimal("5000000")

        # Test best_bid
        assert result.best_bid is not None
        assert result.best_bid.price == Decimal("4999000")

        # Test mid_price
        assert result.mid_price is not None
        assert result.mid_price == Decimal("4999500")

        # Test spread
        assert result.spread is not None
        assert result.spread == Decimal("1000")

    def test_empty_orderbook(self) -> None:
        """Test orderbook with empty asks and bids."""
        json_str = json.dumps(
            {
                "status": 0,
                "data": {
                    "asks": [],
                    "bids": [],
                    "symbol": "BTC",
                },
                "responsetime": "2023-01-01T00:00:00.000Z",
            }
        )

        message = OrderBookMessage(json_str)
        result = message.to_domain_model()

        assert isinstance(result, OrderBook)
        assert len(result.asks) == 0
        assert len(result.bids) == 0
        assert result.best_ask is None
        assert result.best_bid is None
        assert result.mid_price is None
        assert result.spread is None

    def test_orderbook_with_only_asks(self) -> None:
        """Test orderbook with only asks (no bids)."""
        json_str = json.dumps(
            {
                "status": 0,
                "data": {
                    "asks": [
                        {"price": "5000000", "size": "0.1"},
                    ],
                    "bids": [],
                    "symbol": "BTC",
                },
                "responsetime": "2023-01-01T00:00:00.000Z",
            }
        )

        message = OrderBookMessage(json_str)
        result = message.to_domain_model()

        assert isinstance(result, OrderBook)
        assert len(result.asks) == 1
        assert len(result.bids) == 0
        assert result.best_ask is not None
        assert result.best_bid is None
        assert result.mid_price is None
        assert result.spread is None

    def test_orderbook_with_only_bids(self) -> None:
        """Test orderbook with only bids (no asks)."""
        json_str = json.dumps(
            {
                "status": 0,
                "data": {
                    "asks": [],
                    "bids": [
                        {"price": "4999000", "size": "0.15"},
                    ],
                    "symbol": "BTC",
                },
                "responsetime": "2023-01-01T00:00:00.000Z",
            }
        )

        message = OrderBookMessage(json_str)
        result = message.to_domain_model()

        assert isinstance(result, OrderBook)
        assert len(result.asks) == 0
        assert len(result.bids) == 1
        assert result.best_ask is None
        assert result.best_bid is not None
        assert result.mid_price is None
        assert result.spread is None
