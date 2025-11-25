"""Tests for ChildOrdersMessage"""

from decimal import Decimal

import pytest

from crypto_api_client.bitflyer._native_messages.child_orders_message import (
    ChildOrdersMessage,
)
from crypto_api_client.bitflyer.native_domain_models.child_order import ChildOrder
from crypto_api_client.bitflyer.native_domain_models.child_order_state import (
    ChildOrderState,
)
from crypto_api_client.bitflyer.native_domain_models.child_order_type import (
    ChildOrderType,
)
from crypto_api_client.bitflyer.native_domain_models.side import Side


class TestChildOrdersMessage:
    """Tests for ChildOrdersMessage class"""

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
                "total_commission": 0,
                "time_in_force": "GTC"
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
                "total_commission": 0,
                "time_in_force": "GTC"
            }
        ]"""

    def test_init_with_valid_json(self, valid_child_orders_json: str) -> None:
        """Test initialization with valid JSON"""
        message = ChildOrdersMessage(valid_child_orders_json)

        assert message.metadata is None
        assert message.payload is not None
        assert message.payload.content_str == valid_child_orders_json

    def test_to_domain_model(self, valid_child_orders_json: str) -> None:
        """Test conversion to domain model"""
        message = ChildOrdersMessage(valid_child_orders_json)

        orders = message.to_domain_model()
        assert isinstance(orders, list)
        assert len(orders) == 2

        # Verify first order (completed)
        order1 = orders[0]
        assert isinstance(order1, ChildOrder)
        assert order1.id == 138398
        assert order1.child_order_id == "JOR20150707-084555-022523"
        assert str(order1.product_code) == "BTC_JPY"
        assert order1.side == Side.BUY
        assert order1.child_order_type == ChildOrderType.LIMIT
        assert order1.price == Decimal("30000")
        assert order1.size == Decimal("0.1")
        assert order1.child_order_state == ChildOrderState.COMPLETED
        assert order1.executed_size == Decimal("0.1")

        # Verify second order (canceled)
        order2 = orders[1]
        assert order2.child_order_state == ChildOrderState.CANCELED
        assert order2.cancel_size == Decimal("0.1")
        assert order2.executed_size == Decimal("0")

    def test_to_child_orders_alias_method(self, valid_child_orders_json: str) -> None:
        """Test to_domain_model method (no alias method exists)"""
        message = ChildOrdersMessage(valid_child_orders_json)

        orders = message.to_domain_model()
        assert len(orders) == 2
        assert orders[0].child_order_id == "JOR20150707-084555-022523"
        assert orders[0].price == Decimal("30000")

    def test_empty_orders(self) -> None:
        """Test conversion with empty order list"""
        message = ChildOrdersMessage("[]")

        orders = message.to_domain_model()
        assert isinstance(orders, list)
        assert len(orders) == 0
