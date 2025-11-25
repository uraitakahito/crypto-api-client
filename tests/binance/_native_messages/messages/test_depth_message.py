"""Tests for DepthMessage."""

import json
from decimal import Decimal

import pytest

from crypto_api_client.binance._native_messages.depth_message import DepthMessage


class TestDepthMessage:
    """Tests for DepthMessage."""

    @pytest.fixture
    def sample_depth_json(self):
        """Sample depth JSON response."""
        data = {
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
        return json.dumps(data)

    def test_depth_message_creation(self, sample_depth_json):
        """Test that DepthMessage is created correctly."""
        message = DepthMessage(sample_depth_json)

        assert message.metadata is None
        assert message.payload.content_str == sample_depth_json

    def test_to_domain_model(self, sample_depth_json):
        """Test conversion to domain model works correctly."""
        message = DepthMessage(sample_depth_json)
        depth = message.to_domain_model()

        assert depth.lastUpdateId == 1027024
        assert len(depth.bids) == 3
        assert len(depth.asks) == 3

        # Verify first bid
        first_bid = depth.bids[0]
        assert first_bid.price == Decimal("4.00000000")
        assert first_bid.quantity == Decimal("431.00000000")

        # Verify first ask
        first_ask = depth.asks[0]
        assert first_ask.price == Decimal("4.00000200")
        assert first_ask.quantity == Decimal("12.00000000")

    def test_empty_depth(self):
        """Test that empty depth can be processed."""
        empty_data = {
            "lastUpdateId": 999,
            "bids": [],
            "asks": [],
        }
        json_str = json.dumps(empty_data)

        message = DepthMessage(json_str)
        depth = message.to_domain_model()

        assert depth.lastUpdateId == 999
        assert len(depth.bids) == 0
        assert len(depth.asks) == 0
        assert depth.best_bid is None
        assert depth.best_ask is None

    def test_invalid_json(self):
        """Test that invalid JSON raises an error."""
        invalid_json = "invalid json"
        message = DepthMessage(invalid_json)

        with pytest.raises(Exception):  # JSON parse error should occur
            message.to_domain_model()

    def test_missing_required_fields(self):
        """Test that missing required fields raises an error."""
        incomplete_data = {
            "bids": [["4.00000000", "431.00000000"]],
            "asks": [["4.00000200", "12.00000000"]],
            # lastUpdateId is missing
        }
        json_str = json.dumps(incomplete_data)
        message = DepthMessage(json_str)

        with pytest.raises(Exception):  # Validation error should occur
            message.to_domain_model()
