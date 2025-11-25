"""MessageMetadata tests"""

import pytest
from pydantic import ValidationError

from crypto_api_client.bitbank._native_messages.message_metadata import (
    MessageMetadata,
)


class TestMessageMetadata:
    """MessageMetadata class tests"""

    def test_init_with_success(self) -> None:
        """Test initialization with success status"""
        metadata = MessageMetadata(success=1)
        assert metadata.success == 1

    def test_init_with_failure(self) -> None:
        """Test initialization with failure status"""
        metadata = MessageMetadata(success=0)
        assert metadata.success == 0

    def test_frozen_model(self) -> None:
        """Test model immutability"""
        metadata = MessageMetadata(success=1)

        with pytest.raises(ValidationError):
            metadata.success = 0

    def test_model_dump(self) -> None:
        """Test model serialization"""
        metadata = MessageMetadata(success=1)
        assert metadata.model_dump() == {"success": 1}

    def test_json_str_property(self) -> None:
        """Test json_str property"""
        # Success status
        metadata = MessageMetadata(success=1)
        assert metadata.json_str == '{"success": 1}'

        # Failure status
        metadata = MessageMetadata(success=0)
        assert metadata.json_str == '{"success": 0}'

        # Other values
        metadata = MessageMetadata(success=999)
        assert metadata.json_str == '{"success": 999}'
