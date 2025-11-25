"""CreateOrderMessage tests"""

from datetime import datetime, timezone
from decimal import Decimal

from crypto_api_client.bitbank._native_messages.create_order_message import (
    CreateOrderMessage,
)
from crypto_api_client.bitbank.native_domain_models import (
    Order,
    OrderStatus,
    OrderType,
    Side,
)


def test_to_domain_model_with_full_data():
    """Test domain model generation with full data"""
    json_str = """{
        "success": 1,
        "data": {
            "order_id": 12345678,
            "pair": "btc_jpy",
            "side": "buy",
            "type": "limit",
            "status": "UNFILLED",
            "price": "5000000",
            "amount": "0.001",
            "executed_amount": "0",
            "average_price": "0",
            "ordered_at": 1614556800000,
            "executed_at": 1614556900000,
            "canceled_at": null,
            "trigger_price": "4900000",
            "post_only": false
        }
    }"""

    message = CreateOrderMessage(json_str)
    order = message.to_domain_model()

    assert isinstance(order, Order)
    assert order.order_id == 12345678
    assert order.pair == "btc_jpy"
    assert order.side == Side.BUY
    assert order.type == OrderType.LIMIT
    assert order.status == OrderStatus.UNFILLED
    assert order.price == Decimal("5000000")
    assert order.amount == Decimal("0.001")
    assert order.executed_amount == Decimal("0")
    assert order.average_price == Decimal("0")
    assert order.ordered_at == datetime(2021, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert order.executed_at == datetime(2021, 3, 1, 0, 1, 40, tzinfo=timezone.utc)
    assert order.canceled_at is None
    assert order.trigger_price == Decimal("4900000")
    assert order.post_only is False


def test_to_domain_model_with_null_values():
    """Test domain model generation with null values"""
    json_str = """{
        "success": 1,
        "data": {
            "order_id": 87654321,
            "pair": "eth_jpy",
            "side": "sell",
            "type": "market",
            "status": "FULLY_FILLED",
            "price": null,
            "amount": null,
            "executed_amount": "0.5",
            "average_price": null,
            "ordered_at": 1614556800000,
            "executed_at": null,
            "canceled_at": null,
            "trigger_price": null,
            "post_only": null
        }
    }"""

    message = CreateOrderMessage(json_str)
    order = message.to_domain_model()

    assert order.order_id == 87654321
    assert order.pair == "eth_jpy"
    assert order.side == Side.SELL
    assert order.type == OrderType.MARKET
    assert order.status == OrderStatus.FULLY_FILLED
    assert order.price is None
    assert order.amount is None
    assert order.executed_amount == Decimal("0.5")
    assert order.average_price is None
    assert order.ordered_at == datetime(2021, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert order.executed_at is None
    assert order.canceled_at is None
    assert order.trigger_price is None
    assert order.post_only is None


def test_to_domain_model_with_canceled_order():
    """Test domain model generation for canceled order"""
    json_str = """{
        "success": 1,
        "data": {
            "order_id": 99999999,
            "pair": "xrp_jpy",
            "side": "buy",
            "type": "limit",
            "status": "CANCELED_UNFILLED",
            "price": "100",
            "amount": "10",
            "executed_amount": "0",
            "average_price": "0",
            "ordered_at": 1614556800000,
            "executed_at": null,
            "canceled_at": 1614557000000,
            "trigger_price": null,
            "post_only": true
        }
    }"""

    message = CreateOrderMessage(json_str)
    order = message.to_domain_model()

    assert order.status == OrderStatus.CANCELED_UNFILLED
    assert order.canceled_at == datetime(2021, 3, 1, 0, 3, 20, tzinfo=timezone.utc)
    assert order.post_only is True
