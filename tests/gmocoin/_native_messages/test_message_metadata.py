"""Tests for GMO Coin MessageMetadata"""

import pytest
from pydantic import ValidationError

from crypto_api_client.gmocoin._native_messages.message_metadata import (
    MessageMetadata,
)


class TestMessageMetadata:
    """Tests for MessageMetadata model"""

    def test_init_with_valid_data(self) -> None:
        """Test initialization with valid status and responsetime"""
        metadata = MessageMetadata(status=0, responsetime="2019-03-19T02:15:06.014Z")

        assert metadata.status == 0
        assert metadata.responsetime == "2019-03-19T02:15:06.014Z"

    def test_json_str_property(self) -> None:
        """Test json_str property returns expected format"""
        metadata = MessageMetadata(status=0, responsetime="2025-01-30T12:34:56.789Z")

        expected = '{"status": 0, "responsetime": "2025-01-30T12:34:56.789Z"}'
        assert metadata.json_str == expected

    def test_json_str_with_error_status(self) -> None:
        """Test json_str property with non-zero status"""
        metadata = MessageMetadata(status=5, responsetime="2025-01-30T12:34:56.789Z")

        assert '"status": 5' in metadata.json_str

    def test_frozen_model(self) -> None:
        """Test that model is immutable"""
        metadata = MessageMetadata(status=0, responsetime="2025-01-30T12:34:56.789Z")

        with pytest.raises(ValidationError):
            metadata.status = 1  # type: ignore[misc]
