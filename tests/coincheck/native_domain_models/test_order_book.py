"""Tests for OrderBook domain model"""

from decimal import Decimal

import pytest

from crypto_api_client.coincheck.native_domain_models.order_book import (
    OrderBook,
    OrderBookEntry,
)


class TestOrderBookEntry:
    """Test class for OrderBookEntry"""

    def test_create_order_book_entry(self) -> None:
        """Can create OrderBookEntry"""
        entry = OrderBookEntry(price=Decimal("15350000"), size=Decimal("0.5"))

        assert entry.price == Decimal("15350000")
        assert entry.size == Decimal("0.5")

    def test_order_book_entry_is_frozen(self) -> None:
        """OrderBookEntry is immutable"""
        entry = OrderBookEntry(price=Decimal("15350000"), size=Decimal("0.5"))

        with pytest.raises(Exception):
            entry.price = Decimal("15400000")  # type: ignore[misc]


class TestOrderBook:
    """Test class for OrderBook"""

    def test_create_empty_order_book(self) -> None:
        """Can create empty OrderBook"""
        order_book = OrderBook(asks=[], bids=[])

        assert order_book.asks == []
        assert order_book.bids == []
        assert order_book.spread is None
        assert order_book.best_bid is None
        assert order_book.best_ask is None
        assert order_book.mid_price is None

    def test_create_order_book_with_entries(self) -> None:
        """Can create OrderBook with entries"""
        asks = [
            OrderBookEntry(price=Decimal("15350001"), size=Decimal("0.1")),
            OrderBookEntry(price=Decimal("15350002"), size=Decimal("0.5")),
        ]
        bids = [
            OrderBookEntry(price=Decimal("15350000"), size=Decimal("0.2")),
            OrderBookEntry(price=Decimal("15349999"), size=Decimal("0.3")),
        ]

        order_book = OrderBook(asks=asks, bids=bids)

        assert len(order_book.asks) == 2
        assert len(order_book.bids) == 2
        assert order_book.asks[0].price == Decimal("15350001")
        assert order_book.bids[0].price == Decimal("15350000")

    def test_spread_calculation(self) -> None:
        """Can calculate spread correctly"""
        asks = [OrderBookEntry(price=Decimal("15350001"), size=Decimal("0.1"))]
        bids = [OrderBookEntry(price=Decimal("15350000"), size=Decimal("0.2"))]

        order_book = OrderBook(asks=asks, bids=bids)

        assert order_book.spread == Decimal("1")

    def test_best_bid_and_ask(self) -> None:
        """Can get best bid and best ask"""
        asks = [
            OrderBookEntry(price=Decimal("15350001"), size=Decimal("0.1")),
            OrderBookEntry(price=Decimal("15350002"), size=Decimal("0.5")),
        ]
        bids = [
            OrderBookEntry(price=Decimal("15350000"), size=Decimal("0.2")),
            OrderBookEntry(price=Decimal("15349999"), size=Decimal("0.3")),
        ]

        order_book = OrderBook(asks=asks, bids=bids)

        assert order_book.best_ask is not None
        assert order_book.best_ask.price == Decimal("15350001")
        assert order_book.best_bid is not None
        assert order_book.best_bid.price == Decimal("15350000")

    def test_mid_price_calculation(self) -> None:
        """Can calculate mid price correctly"""
        asks = [OrderBookEntry(price=Decimal("15350002"), size=Decimal("0.1"))]
        bids = [OrderBookEntry(price=Decimal("15350000"), size=Decimal("0.2"))]

        order_book = OrderBook(asks=asks, bids=bids)

        assert order_book.mid_price == Decimal("15350001")

    def test_parse_array_format(self) -> None:
        """Can parse data in array format"""
        order_book = OrderBook(
            asks=[["15350001", "0.1"], ["15350002", "0.5"]],  # type: ignore[arg-type]
            bids=[["15350000", "0.2"], ["15349999", "0.3"]],  # type: ignore[arg-type]
        )

        assert len(order_book.asks) == 2
        assert len(order_book.bids) == 2
        assert order_book.asks[0].price == Decimal("15350001")
        assert order_book.asks[0].size == Decimal("0.1")

    def test_order_book_is_frozen(self) -> None:
        """OrderBook is immutable"""
        order_book = OrderBook(asks=[], bids=[])

        with pytest.raises(Exception):
            order_book.asks = []  # type: ignore[misc]
