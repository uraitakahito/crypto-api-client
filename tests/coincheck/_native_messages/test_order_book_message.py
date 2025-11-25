"""Tests for OrderBookMessage."""

import json

from crypto_api_client.coincheck._native_messages.order_book_message import (
    OrderBookMessage,
)


class TestOrderBookMessage:
    """Test class for OrderBookMessage."""

    def test_parse_order_book_message(self) -> None:
        """Test that OrderBookMessage can be parsed from JSON."""
        json_data = {
            "asks": [["15350001", "0.1"], ["15350002", "0.5"]],
            "bids": [["15350000", "0.2"], ["15349999", "0.3"]],
        }
        json_str = json.dumps(json_data)

        message = OrderBookMessage(json_str)
        order_book = message.to_domain_model()

        assert len(order_book.asks) == 2
        assert len(order_book.bids) == 2

    def test_metadata_is_none(self) -> None:
        """Test that metadata is always None."""
        json_data = {
            "asks": [["15350001", "0.1"]],
            "bids": [["15350000", "0.2"]],
        }
        json_str = json.dumps(json_data)

        message = OrderBookMessage(json_str)

        assert message.metadata is None

    def test_extract_payload_returns_full_json(self) -> None:
        """Test that payload extraction returns full JSON."""
        json_data = {
            "asks": [["15350001", "0.1"]],
            "bids": [["15350000", "0.2"]],
        }
        json_str = json.dumps(json_data)

        message = OrderBookMessage(json_str)

        assert message.payload.content_str == json_str
