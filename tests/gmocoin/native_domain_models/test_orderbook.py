"""Tests for GMO Coin OrderBook domain model"""

# pyright: reportArgumentType=false

from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from crypto_api_client.gmocoin.native_domain_models.orderbook import (
    OrderBook,
    OrderBookEntry,
)


class TestOrderBookEntry:
    """Tests for OrderBookEntry model"""

    def test_init_with_string_values(self) -> None:
        """Test initialization with string values (as returned by API)"""
        entry = OrderBookEntry(price=Decimal("455659"), size=Decimal("0.1"))

        assert entry.price == Decimal("455659")
        assert entry.size == Decimal("0.1")
        assert isinstance(entry.price, Decimal)
        assert isinstance(entry.size, Decimal)

    def test_frozen_model(self) -> None:
        """Test that model is immutable"""
        entry = OrderBookEntry(price=Decimal("100"), size=Decimal("1"))

        with pytest.raises(ValidationError):
            entry.price = Decimal("200")  # type: ignore[misc]


class TestOrderBook:
    """Tests for OrderBook model"""

    @pytest.fixture
    def valid_orderbook_data(self) -> dict[str, Any]:
        """Valid orderbook data based on official API documentation"""
        return {
            "asks": [
                {"price": "455659", "size": "0.1"},
                {"price": "455660", "size": "0.5"},
            ],
            "bids": [
                {"price": "455658", "size": "0.2"},
                {"price": "455657", "size": "0.3"},
            ],
            "symbol": "BTC",
        }

    def test_init_with_valid_data(self, valid_orderbook_data: dict[str, Any]) -> None:
        """Test initialization with valid data"""
        orderbook = OrderBook(**valid_orderbook_data)

        assert len(orderbook.asks) == 2
        assert len(orderbook.bids) == 2
        assert orderbook.symbol == "BTC"
        assert all(isinstance(e, OrderBookEntry) for e in orderbook.asks)
        assert all(isinstance(e, OrderBookEntry) for e in orderbook.bids)

    def test_parse_order_entries_from_dicts(
        self, valid_orderbook_data: dict[str, Any]
    ) -> None:
        """Test that dicts are converted to OrderBookEntry via validator"""
        orderbook = OrderBook(**valid_orderbook_data)

        assert orderbook.asks[0].price == Decimal("455659")
        assert orderbook.asks[0].size == Decimal("0.1")
        assert orderbook.bids[0].price == Decimal("455658")
        assert orderbook.bids[0].size == Decimal("0.2")

    def test_parse_order_entries_rejects_non_list(self) -> None:
        """Test that non-list value for asks/bids raises error"""
        with pytest.raises(ValidationError):
            OrderBook(asks="not a list", bids=[], symbol="BTC")  # type: ignore[arg-type]

    def test_best_ask(self, valid_orderbook_data: dict[str, Any]) -> None:
        """Test best_ask property"""
        orderbook = OrderBook(**valid_orderbook_data)

        assert orderbook.best_ask is not None
        assert orderbook.best_ask.price == Decimal("455659")

    def test_best_bid(self, valid_orderbook_data: dict[str, Any]) -> None:
        """Test best_bid property"""
        orderbook = OrderBook(**valid_orderbook_data)

        assert orderbook.best_bid is not None
        assert orderbook.best_bid.price == Decimal("455658")

    def test_mid_price(self, valid_orderbook_data: dict[str, Any]) -> None:
        """Test mid_price property"""
        orderbook = OrderBook(**valid_orderbook_data)

        expected = (Decimal("455659") + Decimal("455658")) / 2
        assert orderbook.mid_price == expected

    def test_spread(self, valid_orderbook_data: dict[str, Any]) -> None:
        """Test spread property"""
        orderbook = OrderBook(**valid_orderbook_data)

        assert orderbook.spread == Decimal("1")

    def test_empty_orderbook(self) -> None:
        """Test orderbook with empty asks and bids"""
        orderbook = OrderBook(asks=[], bids=[], symbol="BTC")

        assert orderbook.best_ask is None
        assert orderbook.best_bid is None
        assert orderbook.mid_price is None
        assert orderbook.spread is None

    def test_only_asks(self) -> None:
        """Test orderbook with only asks"""
        orderbook = OrderBook(
            asks=[{"price": "100", "size": "1"}],  # type: ignore[list-item]
            bids=[],
            symbol="BTC",
        )

        assert orderbook.best_ask is not None
        assert orderbook.best_bid is None
        assert orderbook.mid_price is None
        assert orderbook.spread is None

    def test_only_bids(self) -> None:
        """Test orderbook with only bids"""
        orderbook = OrderBook(
            asks=[],
            bids=[{"price": "100", "size": "1"}],  # type: ignore[list-item]
            symbol="BTC",
        )

        assert orderbook.best_ask is None
        assert orderbook.best_bid is not None
        assert orderbook.mid_price is None
        assert orderbook.spread is None

    def test_symbol_is_base_currency_code(self) -> None:
        """Test that symbol is base currency code only (e.g., 'BTC', not 'BTC_JPY')"""
        orderbook = OrderBook(asks=[], bids=[], symbol="BTC")
        assert orderbook.symbol == "BTC"

        orderbook2 = OrderBook(asks=[], bids=[], symbol="ETH")
        assert orderbook2.symbol == "ETH"

    def test_frozen_model(self, valid_orderbook_data: dict[str, Any]) -> None:
        """Test that model is immutable"""
        orderbook = OrderBook(**valid_orderbook_data)

        with pytest.raises(ValidationError):
            orderbook.symbol = "ETH"  # type: ignore[misc]
