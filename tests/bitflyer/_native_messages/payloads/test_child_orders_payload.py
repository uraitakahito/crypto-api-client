"""Tests for ChildOrdersPayload"""

import pytest

from crypto_api_client.bitflyer._native_messages.child_orders_payload import (
    ChildOrdersPayload,
)


class TestChildOrdersPayload:
    """Tests for ChildOrdersPayload class"""

    @pytest.fixture
    def valid_child_orders_json(self) -> str:
        """Valid child order JSON data (array)"""
        return """[
            {
                "id": 138398,
                "child_order_id": "JOR20150707-084555-022523",
                "product_code": "BTC_JPY",
                "side": "BUY",
                "child_order_type": "LIMIT",
                "price": 30000,
                "average_price": 30000,
                "size": 0.1,
                "child_order_state": "COMPLETED",
                "expire_date": "2015-07-14T07:25:52",
                "child_order_date": "2015-07-07T08:45:53",
                "child_order_acceptance_id": "JRF20150707-084552-031927",
                "outstanding_size": 0,
                "cancel_size": 0,
                "executed_size": 0.1,
                "total_commission": 0
            },
            {
                "id": 138397,
                "child_order_id": "JOR20150707-084549-022519",
                "product_code": "BTC_JPY",
                "side": "SELL",
                "child_order_type": "LIMIT",
                "price": 30000,
                "average_price": 0,
                "size": 0.1,
                "child_order_state": "CANCELED",
                "expire_date": "2015-07-14T07:25:47",
                "child_order_date": "2015-07-07T08:45:47",
                "child_order_acceptance_id": "JRF20150707-084547-396699",
                "outstanding_size": 0,
                "cancel_size": 0.1,
                "executed_size": 0,
                "total_commission": 0
            }
        ]"""

    def test_init_with_valid_json(self, valid_child_orders_json: str) -> None:
        """Test initialization with valid JSON"""
        payload = ChildOrdersPayload(valid_child_orders_json)

        assert payload.content_str == valid_child_orders_json

    def test_init_with_empty_array(self) -> None:
        """Test initialization with empty array"""
        json_str = "[]"
        payload = ChildOrdersPayload(json_str)

        assert payload.content_str == json_str

    def test_init_with_single_order(self) -> None:
        """Test initialization with single order"""
        json_str = """[
            {
                "id": 138398,
                "child_order_id": "JOR20150707-084555-022523",
                "product_code": "BTC_JPY",
                "side": "BUY",
                "child_order_type": "LIMIT",
                "price": 30000,
                "size": 0.1,
                "child_order_state": "ACTIVE"
            }
        ]"""
        payload = ChildOrdersPayload(json_str)

        assert payload.content_str == json_str
