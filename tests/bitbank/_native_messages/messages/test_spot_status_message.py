"""Tests for SpotStatusMessage."""

from decimal import Decimal

import pytest

from crypto_api_client.bitbank._native_messages.spot_status_message import (
    SpotStatusMessage,
)
from crypto_api_client.bitbank.native_domain_models import SpotStatusType


class TestSpotStatusMessage:
    """Tests to verify SpotStatusMessage behavior."""

    def test_parse_valid_response(self) -> None:
        """Test parsing valid JSON response."""
        json_str = """{
            "success": 1,
            "data": {
                "statuses": [
                    {
                        "pair": "btc_jpy",
                        "status": "NORMAL",
                        "min_amount": "0.0001"
                    },
                    {
                        "pair": "eth_jpy",
                        "status": "BUSY",
                        "min_amount": "0.001"
                    }
                ]
            }
        }"""

        message = SpotStatusMessage(json_str)

        # Verify metadata
        assert message.metadata.success == 1

        # Convert to domain model
        spot_status = message.to_domain_model()

        assert len(spot_status.statuses) == 2
        assert spot_status.statuses[0].pair == "btc_jpy"
        assert spot_status.statuses[0].status == SpotStatusType.NORMAL
        assert spot_status.statuses[0].min_amount == Decimal("0.0001")
        assert spot_status.statuses[1].pair == "eth_jpy"
        assert spot_status.statuses[1].status == SpotStatusType.BUSY
        assert spot_status.statuses[1].min_amount == Decimal("0.001")

    def test_parse_all_status_types(self) -> None:
        """Test parsing all status types."""
        json_str = """{
            "success": 1,
            "data": {
                "statuses": [
                    {"pair": "btc_jpy", "status": "NORMAL", "min_amount": "0.0001"},
                    {"pair": "eth_jpy", "status": "BUSY", "min_amount": "0.001"},
                    {"pair": "xrp_jpy", "status": "VERY_BUSY", "min_amount": "1"},
                    {"pair": "ltc_jpy", "status": "HALT", "min_amount": "0.01"}
                ]
            }
        }"""

        message = SpotStatusMessage(json_str)
        spot_status = message.to_domain_model()

        assert spot_status.statuses[0].status == SpotStatusType.NORMAL
        assert spot_status.statuses[1].status == SpotStatusType.BUSY
        assert spot_status.statuses[2].status == SpotStatusType.VERY_BUSY
        assert spot_status.statuses[3].status == SpotStatusType.HALT

    def test_parse_empty_statuses(self) -> None:
        """Test parsing empty statuses array."""
        json_str = """{
            "success": 1,
            "data": {
                "statuses": []
            }
        }"""

        message = SpotStatusMessage(json_str)
        spot_status = message.to_domain_model()

        assert len(spot_status.statuses) == 0

    def test_parse_invalid_json(self) -> None:
        """Test error with invalid JSON."""
        json_str = "{ invalid json }"

        message = SpotStatusMessage(json_str)
        with pytest.raises(ValueError):
            _ = message.payload

    def test_parse_missing_success_field(self) -> None:
        """Test error when success field is missing."""
        json_str = """{
            "data": {
                "statuses": []
            }
        }"""

        message = SpotStatusMessage(json_str)
        with pytest.raises(ValueError, match="metadata.*success"):
            _ = message.metadata

    def test_decimal_precision_preserved(self) -> None:
        """Test that Decimal precision is preserved."""
        json_str = """{
            "success": 1,
            "data": {
                "statuses": [
                    {
                        "pair": "btc_jpy",
                        "status": "NORMAL",
                        "min_amount": "0.00010000"
                    }
                ]
            }
        }"""

        message = SpotStatusMessage(json_str)
        spot_status = message.to_domain_model()

        assert spot_status.statuses[0].min_amount == Decimal("0.00010000")
        assert str(spot_status.statuses[0].min_amount) == "0.00010000"
