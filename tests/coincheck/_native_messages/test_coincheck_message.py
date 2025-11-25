"""Coincheck CoincheckMessage tests"""

from crypto_api_client._base import Payload
from crypto_api_client.coincheck._native_messages.coincheck_message import (
    CoincheckMessage,
)
from crypto_api_client.coincheck._native_messages.message_metadata import (
    MessageMetadata,
)


# Dummy class for testing
class DummyPayload(Payload):
    pass


class DummyMessage(CoincheckMessage[DummyPayload, dict]):
    def _create_payload(self, payload_json_str: str) -> DummyPayload:
        return DummyPayload(payload_json_str)

    def to_domain_model(self) -> dict:
        return {}


class TestCoincheckMessage:
    """Tests for CoincheckMessage."""

    def test_create_metadata_with_success_true(self):
        """Test extraction of success=true (Balance API etc.)."""
        json_str = '{"success": true, "btc": "1.0"}'
        message = DummyMessage(json_str)

        assert message.metadata is not None
        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success is True

    def test_create_metadata_with_success_false(self):
        """Test extraction of success=false (Balance API etc.)."""
        json_str = '{"success": false}'
        message = DummyMessage(json_str)

        assert message.metadata is not None
        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success is False

    def test_create_metadata_without_success(self):
        """Test that metadata is None when success field is missing (Ticker API etc.)."""
        json_str = '{"last": 15350000, "bid": 15340000}'
        message = DummyMessage(json_str)

        assert message.metadata is None

    def test_extract_payload_json_returns_whole_response(self):
        """Test that entire response is returned as payload when no metadata."""
        json_str = '{"last": "15350001", "bid": "15350000"}'
        message = DummyMessage(json_str)

        assert message.payload.content_str == json_str

    def test_public_api_pattern(self):
        """Test pattern without metadata (Ticker API etc.)."""
        json_str = '{"last": 15350000, "bid": 15340000, "ask": 15350001}'
        message = DummyMessage(json_str)

        # No metadata
        assert message.metadata is None
        # Payload is entire response
        assert message.payload.content_str == json_str

    def test_private_api_pattern(self):
        """Test pattern with metadata (Balance API etc.)."""
        json_str = '{"success": true, "btc": "7.75052654", "btc_reserved": "3.5002"}'
        message = DummyMessage(json_str)

        # Has metadata
        assert message.metadata is not None
        assert message.metadata.success is True
        # Payload excludes success
        payload_content = message.payload.content_str
        assert "success" not in payload_content
        assert "btc" in payload_content
        assert "btc_reserved" in payload_content

    def test_extract_payload_json_removes_success_when_metadata_present(self):
        """Test that _extract_payload_json() excludes success when metadata is present.

        Verifies that for APIs with success field (Balance, Unsettled Orders),
        the base class implementation correctly excludes success.
        """
        json_str = """{
            "success": true,
            "jpy": "1000.0",
            "btc": "2.5"
        }"""

        message = DummyMessage(json_str)

        # Verify _extract_payload_json() excludes success
        payload_json = message._extract_payload_json(json_str)
        assert "success" not in payload_json
        assert "jpy" in payload_json
        assert "btc" in payload_json

        # Verify payload does not contain success
        import json

        payload_data = json.loads(message.payload._json_str)
        assert "success" not in payload_data
        assert "jpy" in payload_data

    def test_extract_payload_json_preserves_when_no_metadata(self):
        """Test that _extract_payload_json() returns as-is when no metadata.

        Verifies that for APIs without success field (Ticker),
        the base class implementation returns the entire response as-is.
        """
        json_str = """{
            "last": "15350001",
            "bid": "15350000",
            "ask": "15350001"
        }"""

        message = DummyMessage(json_str)

        # Verify _extract_payload_json() returns as-is
        payload_json = message._extract_payload_json(json_str)
        # Compare parsed JSON since whitespace may differ
        import json

        assert json.loads(payload_json) == json.loads(json_str)

        # Verify metadata is None
        assert message.metadata is None

    def test_extract_payload_json_handles_success_at_various_positions(self):
        """Test success field exclusion at various positions."""

        # success at beginning
        json_str1 = '{"success": true, "data": "value"}'
        message1 = DummyMessage(json_str1)
        payload1 = message1._extract_payload_json(json_str1)
        assert "success" not in payload1
        assert "data" in payload1

        # success at end
        json_str2 = '{"data": "value", "success": false}'
        message2 = DummyMessage(json_str2)
        payload2 = message2._extract_payload_json(json_str2)
        assert "success" not in payload2
        assert "data" in payload2

        # success in middle
        json_str3 = '{"a": "1", "success": true, "b": "2"}'
        message3 = DummyMessage(json_str3)
        payload3 = message3._extract_payload_json(json_str3)
        assert "success" not in payload3
        assert "a" in payload3
        assert "b" in payload3

    def test_extract_payload_json_preserves_numeric_precision(self):
        """Test that _extract_payload_json() preserves numeric precision.

        Verifies that precision is maintained even for 30-digit high-precision numbers.
        Using json.loads() -> json.dumps() would lose precision through float,
        but regex-based string manipulation preserves precision.
        """
        # 30-digit high-precision number
        json_str = """{
            "success": true,
            "amount": 0.123456789012345678901234567890
        }"""

        message = DummyMessage(json_str)
        payload_json = message._extract_payload_json(json_str)

        # Verify precision is preserved
        assert "0.123456789012345678901234567890" in payload_json
        assert "success" not in payload_json
