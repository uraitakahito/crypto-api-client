"""Tests for TradingCommissionPayload"""

import pytest

from crypto_api_client.bitflyer._native_messages.trading_commission_payload import (
    TradingCommissionPayload,
)


class TestTradingCommissionPayload:
    """Tests for TradingCommissionPayload class"""

    @pytest.fixture
    def valid_commission_json(self) -> str:
        """Valid commission JSON data"""
        return """{
            "commission_rate": 0.001
        }"""

    def test_init_with_valid_json(self, valid_commission_json: str) -> None:
        """Test initialization with valid JSON"""
        payload = TradingCommissionPayload(valid_commission_json)

        assert payload.content_str == valid_commission_json

    def test_init_with_zero_commission(self) -> None:
        """Test initialization with zero commission"""
        json_str = '{"commission_rate": 0}'
        payload = TradingCommissionPayload(json_str)

        assert payload.content_str == json_str

    def test_init_with_high_commission(self) -> None:
        """Test initialization with high commission"""
        json_str = '{"commission_rate": 0.0015}'
        payload = TradingCommissionPayload(json_str)

        assert payload.content_str == json_str

    def test_init_with_decimal_commission(self) -> None:
        """Test initialization with long decimal commission"""
        json_str = '{"commission_rate": 0.000125}'
        payload = TradingCommissionPayload(json_str)

        assert payload.content_str == json_str
