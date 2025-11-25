"""Coincheck MessageMetadata tests"""

from crypto_api_client.coincheck._native_messages.message_metadata import (
    MessageMetadata,
)


class TestMessageMetadata:
    """Tests for MessageMetadata."""

    def test_message_metadata_success_true(self):
        """Test when success=true."""
        metadata = MessageMetadata(success=True)

        assert metadata.success is True
        assert metadata.json_str == '{"success": true}'

    def test_message_metadata_success_false(self):
        """Test when success=false."""
        metadata = MessageMetadata(success=False)

        assert metadata.success is False
        assert metadata.json_str == '{"success": false}'

    def test_message_metadata_frozen(self):
        """Test that metadata is frozen."""
        metadata = MessageMetadata(success=True)

        import pytest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            metadata.success = False  # type: ignore[misc]
