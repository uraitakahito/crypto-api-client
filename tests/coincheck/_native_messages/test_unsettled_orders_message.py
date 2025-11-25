"""Coincheck UnsettledOrdersMessage tests"""

from crypto_api_client.coincheck._native_messages.message_metadata import (
    MessageMetadata,
)
from crypto_api_client.coincheck._native_messages.unsettled_orders_message import (
    UnsettledOrdersMessage,
)


class TestUnsettledOrdersMessage:
    """Tests for UnsettledOrdersMessage."""

    def test_unsettled_orders_message_to_domain_model(self):
        """Test conversion from UnsettledOrdersMessage to Domain Model."""
        json_str = """{
            "success": true,
            "orders": [
                {
                    "id": 202835,
                    "order_type": "buy",
                    "rate": 26890,
                    "pair": "btc_jpy",
                    "pending_amount": "0.5527",
                    "pending_market_buy_amount": null,
                    "stop_loss_rate": null,
                    "created_at": "2015-01-10T05:55:38.000Z"
                }
            ]
        }"""

        message = UnsettledOrdersMessage(json_str)
        orders = message.to_domain_model()

        # Verify it is a list
        assert isinstance(orders, list)
        assert len(orders) == 1

        # Verify order content
        order = orders[0]
        assert order.id == 202835
        assert order.order_type.value == "buy"
        assert order.rate == 26890
        assert order.pair == "btc_jpy"

    def test_unsettled_orders_message_empty_orders(self):
        """Test when orders are empty."""
        json_str = """{
            "success": true,
            "orders": []
        }"""

        message = UnsettledOrdersMessage(json_str)
        orders = message.to_domain_model()

        assert isinstance(orders, list)
        assert len(orders) == 0

    def test_unsettled_orders_message_has_metadata(self):
        """Test that UnsettledOrdersMessage has metadata."""
        json_str = """{
            "success": true,
            "orders": []
        }"""

        message = UnsettledOrdersMessage(json_str)

        # Verify metadata
        assert message.metadata is not None
        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success is True
        assert message.metadata.json_str == '{"success": true}'

    def test_unsettled_orders_message_metadata_false(self):
        """Test when success=false."""
        json_str = """{
            "success": false,
            "orders": []
        }"""

        message = UnsettledOrdersMessage(json_str)

        assert message.metadata is not None
        assert message.metadata.success is False

    def test_unsettled_orders_message_payload_excludes_success(self):
        """Test that UnsettledOrdersPayload does not contain success field.

        This is a design principle verification test:
        - Message layer is responsible for excluding metadata (success)
        - Payload layer holds only pure payload
        """
        json_str = """{
            "success": true,
            "orders": [
                {
                    "id": 12345,
                    "order_type": "sell",
                    "rate": 30000,
                    "pair": "btc_jpy",
                    "pending_amount": "1.0",
                    "pending_market_buy_amount": null,
                    "stop_loss_rate": null,
                    "created_at": "2025-01-30T12:00:00.000Z"
                }
            ]
        }"""

        message = UnsettledOrdersMessage(json_str)

        # Verify Payload raw JSON string does not contain success
        payload_raw = message.payload._json_str
        assert "success" not in payload_raw

        # Verify metadata is correctly extracted
        assert message.metadata is not None
        assert message.metadata.success is True

        # Verify domain model conversion works correctly
        orders = message.to_domain_model()
        assert len(orders) == 1

    def test_unsettled_orders_message_payload_structure(self):
        """Test that Payload contains only pure payload."""
        import json

        json_str = """{
            "success": true,
            "orders": [
                {
                    "id": 100,
                    "order_type": "buy",
                    "rate": 25000,
                    "pair": "eth_jpy",
                    "pending_amount": "2.5",
                    "pending_market_buy_amount": null,
                    "stop_loss_rate": null,
                    "created_at": "2025-01-30T10:00:00.000Z"
                }
            ]
        }"""

        message = UnsettledOrdersMessage(json_str)

        # Parse Payload raw JSON
        payload_data = json.loads(message.payload._json_str)

        # Verify success key does not exist
        assert "success" not in payload_data

        # Verify orders key exists
        assert "orders" in payload_data
        assert isinstance(payload_data["orders"], list)
        assert len(payload_data["orders"]) == 1

        # Verify content_str returns only the array
        content_data = json.loads(message.payload.content_str)
        assert isinstance(content_data, list)
        assert len(content_data) == 1
        assert content_data[0]["id"] == 100
