"""Order book domain model tests"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from crypto_api_client.bitbank.native_domain_models.depth import Depth, DepthEntry


class TestDepthEntry:
    """DepthEntry tests"""

    def test_create_depth_entry(self):
        """Test creating DepthEntry"""
        entry = DepthEntry(price=Decimal("15840000"), size=Decimal("0.1234"))
        assert entry.price == Decimal("15840000")
        assert entry.size == Decimal("0.1234")

    def test_depth_entry_is_frozen(self):
        """Test that DepthEntry is immutable"""
        from pydantic import ValidationError

        entry = DepthEntry(price=Decimal("15840000"), size=Decimal("0.1234"))
        with pytest.raises(ValidationError):
            entry.price = Decimal("15850000")


class TestDepth:
    """Depth tests"""

    def test_create_depth_with_basic_data(self):
        """Test creating basic Depth"""
        depth = Depth(
            asks=[
                DepthEntry(price=Decimal("15841000"), size=Decimal("0.1")),
                DepthEntry(price=Decimal("15842000"), size=Decimal("0.2")),
            ],
            bids=[
                DepthEntry(price=Decimal("15840000"), size=Decimal("0.3")),
                DepthEntry(price=Decimal("15839000"), size=Decimal("0.4")),
            ],
            timestamp=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
            sequenceId="12345",
        )

        assert len(depth.asks) == 2
        assert len(depth.bids) == 2
        assert depth.timestamp == datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        assert depth.sequenceId == "12345"

    def test_parse_array_format_orders(self):
        """Test parsing array format order data"""
        depth = Depth(
            asks=[
                DepthEntry(price=Decimal("15841000"), size=Decimal("0.1")),
                DepthEntry(price=Decimal("15842000"), size=Decimal("0.2")),
            ],
            bids=[
                DepthEntry(price=Decimal("15840000"), size=Decimal("0.3")),
                DepthEntry(price=Decimal("15839000"), size=Decimal("0.4")),
            ],
            timestamp=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
            sequenceId="12345",  # Also accepts alias names
        )

        assert len(depth.asks) == 2
        assert depth.asks[0].price == Decimal("15841000")
        assert depth.asks[0].size == Decimal("0.1")
        assert len(depth.bids) == 2
        assert depth.bids[0].price == Decimal("15840000")
        assert depth.bids[0].size == Decimal("0.3")

    def test_spread_calculation(self):
        """Test spread calculation"""
        depth = Depth(
            asks=[
                DepthEntry(price=Decimal("15841000"), size=Decimal("0.1")),
            ],
            bids=[
                DepthEntry(price=Decimal("15840000"), size=Decimal("0.3")),
            ],
            timestamp=datetime.now(UTC),
            sequenceId="12345",
        )

        assert depth.spread == Decimal("1000")

    def test_spread_with_empty_orders(self):
        """Test spread calculation when orders are empty"""
        depth = Depth(asks=[], bids=[], timestamp=datetime.now(UTC), sequenceId="12345")

        assert depth.spread is None

    def test_best_bid_and_ask(self):
        """Test best bid and ask prices"""
        depth = Depth(
            asks=[
                DepthEntry(price=Decimal("15841000"), size=Decimal("0.1")),
                DepthEntry(price=Decimal("15842000"), size=Decimal("0.2")),
            ],
            bids=[
                DepthEntry(price=Decimal("15840000"), size=Decimal("0.3")),
                DepthEntry(price=Decimal("15839000"), size=Decimal("0.4")),
            ],
            timestamp=datetime.now(UTC),
            sequenceId="12345",
        )

        assert depth.best_ask and depth.best_ask.price == Decimal("15841000")
        assert depth.best_ask and depth.best_ask.size == Decimal("0.1")
        assert depth.best_bid and depth.best_bid.price == Decimal("15840000")
        assert depth.best_bid and depth.best_bid.size == Decimal("0.3")

    def test_circuit_breaker_data(self):
        """Test circuit breaker mode data"""
        depth = Depth(
            asks=[],
            bids=[],
            asks_over=Decimal("100.5"),
            bids_under=Decimal("200.3"),
            timestamp=datetime.now(UTC),
            sequenceId="12345",
        )

        assert depth.has_circuit_breaker_data is True
        assert depth.asks_over == Decimal("100.5")
        assert depth.bids_under == Decimal("200.3")

    def test_no_circuit_breaker_data(self):
        """Test when no circuit breaker mode data"""
        depth = Depth(asks=[], bids=[], timestamp=datetime.now(UTC), sequenceId="12345")

        assert depth.has_circuit_breaker_data is False

    def test_market_order_data(self):
        """Test market order data"""
        depth = Depth(
            asks=[],
            bids=[],
            ask_market=Decimal("1.5"),
            bid_market=Decimal("2.3"),
            timestamp=datetime.now(UTC),
            sequenceId="12345",
        )

        assert depth.ask_market == Decimal("1.5")
        assert depth.bid_market == Decimal("2.3")

    def test_mid_price_with_both_sides(self):
        """Test mid_price calculation when both bid and ask exist"""
        depth = Depth(
            asks=[
                DepthEntry(price=Decimal("15841000"), size=Decimal("0.1")),
                DepthEntry(price=Decimal("15842000"), size=Decimal("0.2")),
            ],
            bids=[
                DepthEntry(price=Decimal("15840000"), size=Decimal("0.3")),
                DepthEntry(price=Decimal("15839000"), size=Decimal("0.4")),
            ],
            timestamp=datetime.now(UTC),
            sequenceId="12345",
        )

        expected_mid_price = (Decimal("15841000") + Decimal("15840000")) / 2
        assert depth.mid_price == expected_mid_price
        assert depth.mid_price == Decimal("15840500")

    def test_mid_price_with_only_asks(self):
        """Test mid_price when only asks exist"""
        depth = Depth(
            asks=[
                DepthEntry(price=Decimal("15841000"), size=Decimal("0.1")),
            ],
            bids=[],
            timestamp=datetime.now(UTC),
            sequenceId="12345",
        )

        assert depth.mid_price is None

    def test_mid_price_with_only_bids(self):
        """Test mid_price when only bids exist"""
        depth = Depth(
            asks=[],
            bids=[
                DepthEntry(price=Decimal("15840000"), size=Decimal("0.3")),
            ],
            timestamp=datetime.now(UTC),
            sequenceId="12345",
        )

        assert depth.mid_price is None

    def test_mid_price_with_empty_book(self):
        """Test mid_price when order book is empty"""
        depth = Depth(asks=[], bids=[], timestamp=datetime.now(UTC), sequenceId="12345")

        assert depth.mid_price is None

    def test_mid_price_precision(self):
        """Test mid_price calculation precision"""
        depth = Depth(
            asks=[
                DepthEntry(price=Decimal("15840001.123456"), size=Decimal("0.1")),
            ],
            bids=[
                DepthEntry(price=Decimal("15840000.123456"), size=Decimal("0.3")),
            ],
            timestamp=datetime.now(UTC),
            sequenceId="12345",
        )

        expected_mid_price = (
            Decimal("15840001.123456") + Decimal("15840000.123456")
        ) / 2
        assert depth.mid_price == expected_mid_price
        assert depth.mid_price == Decimal("15840000.623456")

    def test_depth_is_frozen(self):
        """Test that Depth is immutable"""
        from pydantic import ValidationError

        depth = Depth(asks=[], bids=[], timestamp=datetime.now(UTC), sequenceId="12345")

        with pytest.raises(ValidationError):
            depth.sequenceId = "67890"

    def test_invalid_asks_type_raises_error(self):
        """Test that raises error when asks is not an array"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="Expected list"):
            Depth(
                asks="invalid",  # type: ignore[arg-type]
                bids=[],
                timestamp=datetime.now(UTC),
                sequenceId="12345",
            )

    def test_invalid_bids_type_raises_error(self):
        """Test that raises error when bids is not an array"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="Expected list"):
            Depth(
                asks=[],
                bids={"invalid": "dict"},  # type: ignore[arg-type]
                timestamp=datetime.now(UTC),
                sequenceId="12345",
            )
