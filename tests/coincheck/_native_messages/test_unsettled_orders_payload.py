"""Coincheck UnsettledOrdersPayload tests"""

import pytest

from crypto_api_client.coincheck._native_messages.unsettled_orders_payload import (
    UnsettledOrdersPayload,
)


class TestUnsettledOrdersPayload:
    """Tests for UnsettledOrdersPayload"""

    def test_content_str_preserves_numeric_precision(self):
        """Verify that content_str preserves numeric precision

        Validates that even 30-digit high-precision numbers do not lose precision.
        Using json.loads() -> json.dumps() loses precision via float conversion,
        but string manipulation via _JsonExtractor.extract_array() preserves precision.
        """
        # JSON with 30-digit high-precision numbers
        json_str = """{
            "orders": [
                {
                    "id": 202835,
                    "pending_amount": "0.123456789012345678901234567890",
                    "rate": 26890.123456789012345678901234567890
                }
            ]
        }"""

        payload = UnsettledOrdersPayload(json_str)
        content = payload.content_str

        # Verify precision is preserved
        assert "0.123456789012345678901234567890" in content
        assert "26890.123456789012345678901234567890" in content

    def test_content_str_extracts_orders_array(self):
        """Verify that content_str correctly extracts orders array"""
        json_str = """{
            "orders": [
                {
                    "id": 202835,
                    "order_type": "buy",
                    "rate": 26890,
                    "pair": "btc_jpy",
                    "pending_amount": "0.5527"
                }
            ]
        }"""

        payload = UnsettledOrdersPayload(json_str)
        content = payload.content_str

        # Verify only the array is extracted
        import json

        parsed = json.loads(content)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["id"] == 202835
        assert parsed[0]["pending_amount"] == "0.5527"

    def test_content_str_handles_empty_orders(self):
        """Verify correct handling of empty orders array"""
        json_str = '{"orders": []}'

        payload = UnsettledOrdersPayload(json_str)
        content = payload.content_str

        assert content == "[]"

    def test_content_str_raises_on_missing_orders_field(self):
        """Verify ValueError is raised when orders field is missing"""
        json_str = '{"other_field": "value"}'

        payload = UnsettledOrdersPayload(json_str)

        with pytest.raises(ValueError, match='"orders" field not found'):
            _ = payload.content_str
