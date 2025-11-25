"""Tests for CancelChildOrderMessage"""

from crypto_api_client.bitflyer._native_messages.cancel_child_order_message import (
    CancelChildOrderMessage,
)
from crypto_api_client.bitflyer._native_messages.cancel_child_order_payload import (
    CancelChildOrderPayload,
)


class TestCancelChildOrderMessage:
    """Tests for CancelChildOrderMessage class"""

    def test_init_with_empty_response(self) -> None:
        """Test initialization with empty response

        bitFlyer's cancel order API returns an empty response on success
        """
        message = CancelChildOrderMessage("")

        assert message.metadata is None
        assert isinstance(message.payload, CancelChildOrderPayload)
        assert message.payload.content_str == ""

    def test_payload_handling(self) -> None:
        """Test correct handling of Payload"""
        message = CancelChildOrderMessage("")
        payload = message.payload

        assert isinstance(payload, CancelChildOrderPayload)
        assert payload.content_str == ""
        assert payload.raw_json == ""

    def test_to_domain_model_returns_none(self) -> None:
        """Test that to_domain_model returns None"""
        message = CancelChildOrderMessage("")
        result = message.to_domain_model()

        assert result is None

    def test_follows_bitflyer_message_pattern(self) -> None:
        """Test that it follows the standard BitFlyerMessage pattern"""
        message = CancelChildOrderMessage("")

        # Metadata is None (bitFlyer does not have metadata)
        assert message.metadata is None

        # Payload is properly initialized
        assert message.payload is not None
        assert isinstance(message.payload, CancelChildOrderPayload)


class TestCancelChildOrderPayload:
    """Tests for CancelChildOrderPayload class"""

    def test_empty_string_handling(self) -> None:
        """Test correct handling of empty string"""
        payload = CancelChildOrderPayload("")

        assert payload.content_str == ""
        assert payload.raw_json == ""

    def test_inherits_from_payload_base_class(self) -> None:
        """Test that it inherits from the Payload base class"""
        from crypto_api_client._base import Payload

        payload = CancelChildOrderPayload("")

        assert isinstance(payload, Payload)
