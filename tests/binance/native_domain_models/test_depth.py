"""Tests for Depth domain model."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from crypto_api_client.binance.native_domain_models import Depth, DepthEntry


class TestDepthEntry:
    """Tests for DepthEntry."""

    def test_from_array_valid(self):
        """Test that DepthEntry is created correctly from array format."""
        data = ["100.50", "10.25"]
        entry = DepthEntry.from_array(data)

        assert entry.price == Decimal("100.50")
        assert entry.quantity == Decimal("10.25")

    def test_from_array_invalid_length(self):
        """Test that error is raised for invalid array length."""
        data = ["100.50"]
        with pytest.raises(ValueError, match="Expected 2 elements"):
            DepthEntry.from_array(data)

    def test_frozen_model(self):
        """Test that model is immutable."""
        entry = DepthEntry(price=Decimal("100.0"), quantity=Decimal("5.0"))
        with pytest.raises(ValidationError):
            entry.price = Decimal("200.0")


class TestDepth:
    """Tests for Depth."""

    @pytest.fixture
    def sample_depth_data(self):
        """Sample depth data."""
        return {
            "lastUpdateId": 1027024,
            "bids": [
                ["4.00000000", "431.00000000"],
                ["3.99000000", "100.00000000"],
                ["3.98000000", "50.00000000"],
            ],
            "asks": [
                ["4.00000200", "12.00000000"],
                ["4.00000400", "22.00000000"],
                ["4.00000600", "32.00000000"],
            ],
        }

    def test_depth_creation(self, sample_depth_data):
        """Test that Depth is created correctly."""
        depth = Depth(**sample_depth_data)

        assert depth.lastUpdateId == 1027024
        assert len(depth.bids) == 3
        assert len(depth.asks) == 3

        # Verify bids
        assert depth.bids[0].price == Decimal("4.00000000")
        assert depth.bids[0].quantity == Decimal("431.00000000")

        # Verify asks
        assert depth.asks[0].price == Decimal("4.00000200")
        assert depth.asks[0].quantity == Decimal("12.00000000")

    def test_best_bid(self, sample_depth_data):
        """Test that best bid is retrieved correctly."""
        depth = Depth(**sample_depth_data)
        best_bid = depth.best_bid

        assert best_bid is not None
        assert best_bid.price == Decimal("4.00000000")
        assert best_bid.quantity == Decimal("431.00000000")

    def test_best_bid_empty(self):
        """Test that None is returned when there are no bids."""
        depth = Depth(lastUpdateId=1, bids=[], asks=[])
        assert depth.best_bid is None

    def test_best_ask(self, sample_depth_data):
        """Test that best ask is retrieved correctly."""
        depth = Depth(**sample_depth_data)
        best_ask = depth.best_ask

        assert best_ask is not None
        assert best_ask.price == Decimal("4.00000200")
        assert best_ask.quantity == Decimal("12.00000000")

    def test_best_ask_empty(self):
        """Test that None is returned when there are no asks."""
        depth = Depth(lastUpdateId=1, bids=[], asks=[])
        assert depth.best_ask is None

    def test_spread(self, sample_depth_data):
        """Test that spread is calculated correctly."""
        depth = Depth(**sample_depth_data)
        spread = depth.spread

        assert spread is not None
        expected_spread = Decimal("4.00000200") - Decimal("4.00000000")
        assert spread == expected_spread

    def test_spread_missing_bids(self):
        """Test that spread is None when there are no bids."""
        depth = Depth(
            lastUpdateId=1,
            bids=[],
            asks=[["4.00000200", "12.00000000"]],  # type: ignore[arg-type]
        )
        assert depth.spread is None

    def test_spread_missing_asks(self):
        """Test that spread is None when there are no asks."""
        depth = Depth(
            lastUpdateId=1,
            bids=[["4.00000000", "431.00000000"]],  # type: ignore[arg-type]
            asks=[],
        )
        assert depth.spread is None

    def test_mid_price(self, sample_depth_data):
        """Test that mid price is calculated correctly."""
        depth = Depth(**sample_depth_data)
        mid_price = depth.mid_price

        assert mid_price is not None
        expected_mid = (Decimal("4.00000200") + Decimal("4.00000000")) / 2
        assert mid_price == expected_mid

    def test_mid_price_missing_data(self):
        """Test that mid price is None when there are no bids/asks."""
        depth = Depth(lastUpdateId=1, bids=[], asks=[])
        assert depth.mid_price is None

    def test_frozen_model(self, sample_depth_data):
        """Test that model is immutable."""
        depth = Depth(**sample_depth_data)
        with pytest.raises(ValidationError):
            depth.lastUpdateId = 9999
