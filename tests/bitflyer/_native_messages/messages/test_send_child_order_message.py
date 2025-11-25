"""Tests for SendChildOrderMessage"""

import pytest

from crypto_api_client.bitflyer._native_messages.send_child_order_message import (
    SendChildOrderMessage,
)


class TestSendChildOrderMessage:
    """Tests for SendChildOrderMessage class"""

    @pytest.fixture
    def valid_send_order_json(self) -> str:
        """Valid order send message JSON data"""
        return """{
            "child_order_acceptance_id": "JRF20150707-050237-639234"
        }"""

    def test_init_with_valid_json(self, valid_send_order_json: str) -> None:
        """Test initialization with valid JSON"""
        message = SendChildOrderMessage(valid_send_order_json)

        assert message.metadata is None
        assert message.payload is not None
        assert message.payload.content_str == valid_send_order_json

    def test_to_domain_model(self, valid_send_order_json: str) -> None:
        """Test conversion to domain model (returns order acceptance ID string)"""
        message = SendChildOrderMessage(valid_send_order_json)

        result = message.to_domain_model()
        assert isinstance(result, str)
        assert result == "JRF20150707-050237-639234"

    def test_empty_acceptance_id(self) -> None:
        """Test conversion with empty acceptance ID"""
        json_str = '{"child_order_acceptance_id": ""}'
        message = SendChildOrderMessage(json_str)

        result = message.to_domain_model()
        assert result == ""

    def test_acceptance_id_with_special_chars(self) -> None:
        """Test conversion with acceptance ID containing special characters"""
        json_str = '{"child_order_acceptance_id": "JRF20250707-123456-789012"}'
        message = SendChildOrderMessage(json_str)

        result = message.to_domain_model()
        assert result == "JRF20250707-123456-789012"
