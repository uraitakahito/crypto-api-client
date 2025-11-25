"""Tests for TradingCommissionMessage"""

from decimal import Decimal

import pytest

from crypto_api_client.bitflyer._native_messages.trading_commission_message import (
    TradingCommissionMessage,
)
from crypto_api_client.bitflyer.native_domain_models.trading_commission import (
    TradingCommission,
)


class TestTradingCommissionMessage:
    """Tests for TradingCommissionMessage class"""

    @pytest.fixture
    def valid_commission_json(self) -> str:
        """Valid commission JSON data"""
        return """{
            "commission_rate": 0.001
        }"""

    def test_init_with_valid_json(self, valid_commission_json: str) -> None:
        """Test initialization with valid JSON"""
        message = TradingCommissionMessage(valid_commission_json)

        assert message.metadata is None
        assert message.payload is not None
        assert message.payload.content_str == valid_commission_json

    def test_to_domain_model(self, valid_commission_json: str) -> None:
        """Test conversion to domain model"""
        message = TradingCommissionMessage(valid_commission_json)

        commission = message.to_domain_model()
        assert isinstance(commission, TradingCommission)
        assert commission.commission_rate == Decimal("0.001")

    def test_to_trading_commission_alias_method(
        self, valid_commission_json: str
    ) -> None:
        """Test to_domain_model method (no alias method exists)"""
        message = TradingCommissionMessage(valid_commission_json)

        commission = message.to_domain_model()
        assert commission.commission_rate == Decimal("0.001")

    def test_zero_commission(self) -> None:
        """Test conversion with zero commission"""
        json_str = '{"commission_rate": 0}'
        message = TradingCommissionMessage(json_str)

        commission = message.to_domain_model()
        assert commission.commission_rate == Decimal("0")

    def test_high_precision_commission(self) -> None:
        """Test conversion with high precision commission"""
        json_str = '{"commission_rate": 0.000125}'
        message = TradingCommissionMessage(json_str)

        commission = message.to_domain_model()
        assert commission.commission_rate == Decimal("0.000125")
