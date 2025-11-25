"""Tests for HealthStatusMessage"""

import pytest

from crypto_api_client.bitflyer._native_messages.health_status_message import (
    HealthStatusMessage,
)
from crypto_api_client.bitflyer.native_domain_models.health_status import HealthStatus


class TestHealthStatusMessage:
    """Tests for HealthStatusMessage class"""

    def test_init_with_valid_json(self) -> None:
        """Test initialization with valid JSON"""
        json_str = '{"status": "NORMAL"}'
        message = HealthStatusMessage(json_str)

        assert message.metadata is None
        assert message.payload is not None
        assert message.payload.content_str == json_str

    def test_to_domain_model_normal(self) -> None:
        """Test domain model conversion with NORMAL status"""
        json_str = '{"status": "NORMAL"}'
        message = HealthStatusMessage(json_str)

        health_status = message.to_domain_model()
        assert isinstance(health_status, HealthStatus)
        assert health_status.status.value == "NORMAL"

    def test_to_domain_model_stop(self) -> None:
        """Test domain model conversion with STOP status"""
        json_str = '{"status": "STOP"}'
        message = HealthStatusMessage(json_str)

        health_status = message.to_domain_model()
        assert isinstance(health_status, HealthStatus)
        assert health_status.status.value == "STOP"

    def test_to_health_status_alias_method(self) -> None:
        """Test to_health_status alias method"""
        json_str = '{"status": "NORMAL"}'
        message = HealthStatusMessage(json_str)

        health_status_1 = message.to_domain_model()
        health_status_2 = message.to_health_status()

        # Verify both methods return the same result
        assert health_status_1.status == health_status_2.status

    def test_invalid_json_format(self) -> None:
        """Test error handling with invalid JSON format"""
        json_str = '{"invalid": "data"}'
        message = HealthStatusMessage(json_str)

        with pytest.raises(Exception):  # Specific exception type depends on implementation
            message.to_domain_model()
