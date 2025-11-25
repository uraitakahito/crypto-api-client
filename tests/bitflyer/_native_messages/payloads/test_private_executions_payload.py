"""Tests for PrivateExecutionsPayload"""

import pytest

from crypto_api_client.bitflyer._native_messages.private_executions_payload import (
    PrivateExecutionsPayload,
)


class TestPrivateExecutionsPayload:
    """Tests for PrivateExecutionsPayload class"""

    @pytest.fixture
    def valid_json(self) -> str:
        """Valid JSON string"""
        return """[
            {
                "id": 100001,
                "side": "BUY",
                "price": 15900000,
                "size": 0.001,
                "exec_date": "2025-01-01T10:00:00Z",
                "commission": 0.0000015,
                "child_order_id": "JOR20250101-100000-123456",
                "child_order_acceptance_id": "JRF20250101-100000-123456"
            }
        ]"""

    def test_init(self, valid_json: str) -> None:
        """Test initialization"""
        payload = PrivateExecutionsPayload(valid_json)
        assert payload._json_str == valid_json

    def test_json_str_property(self, valid_json: str) -> None:
        """Test json_str property"""
        payload = PrivateExecutionsPayload(valid_json)
        assert payload.content_str == valid_json

    def test_empty_array(self) -> None:
        """Test with empty array JSON string"""
        empty_json = "[]"
        payload = PrivateExecutionsPayload(empty_json)
        assert payload.content_str == empty_json

    def test_multiple_executions(self) -> None:
        """Test with multiple execution data"""
        multi_json = """[
            {"id": 1, "side": "BUY", "price": 100},
            {"id": 2, "side": "SELL", "price": 200}
        ]"""
        payload = PrivateExecutionsPayload(multi_json)
        assert payload.content_str == multi_json
