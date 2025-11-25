"""Tests for HealthStatusPayload"""

from crypto_api_client.bitflyer._native_messages.health_status_payload import (
    HealthStatusPayload,
)


class TestHealthStatusPayload:
    """Tests for HealthStatusPayload class"""

    def test_init_with_valid_json(self) -> None:
        """Test initialization with valid JSON"""
        json_str = '{"status": "NORMAL"}'
        payload = HealthStatusPayload(json_str)

        assert payload.content_str == json_str

    def test_init_with_empty_json(self) -> None:
        """Test initialization with empty JSON"""
        json_str = "{}"
        payload = HealthStatusPayload(json_str)

        assert payload.content_str == json_str

    def test_init_with_complex_json(self) -> None:
        """Test initialization with complex JSON"""
        json_str = '{"status": "NORMAL", "extra": {"info": "test"}}'
        payload = HealthStatusPayload(json_str)

        assert payload.content_str == json_str
