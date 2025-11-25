"""Tests for TradingCommission model."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from crypto_api_client.bitflyer.native_domain_models.trading_commission import (
    TradingCommission,
)


class TestTradingCommission:
    """Test class for TradingCommission model."""

    def test_create_trading_commission(self) -> None:
        """Test normal TradingCommission creation."""
        commission = TradingCommission(commission_rate=Decimal("0.001"))
        assert commission.commission_rate == Decimal("0.001")

    def test_create_trading_commission_from_float(self) -> None:
        """Test creating TradingCommission from float."""
        commission = TradingCommission(commission_rate=Decimal("0.001"))
        assert commission.commission_rate == Decimal("0.001")

    def test_create_trading_commission_from_string(self) -> None:
        """Test creating TradingCommission from string."""
        commission = TradingCommission(commission_rate=Decimal("0.001"))
        assert commission.commission_rate == Decimal("0.001")

    def test_create_trading_commission_zero(self) -> None:
        """Test with commission rate of 0."""
        commission = TradingCommission(commission_rate=Decimal("0"))
        assert commission.commission_rate == Decimal("0")

    def test_create_trading_commission_high_rate(self) -> None:
        """Test with high commission rate."""
        commission = TradingCommission(commission_rate=Decimal("0.15"))
        assert commission.commission_rate == Decimal("0.15")

    def test_trading_commission_frozen(self) -> None:
        """Test that TradingCommission is frozen."""
        commission = TradingCommission(commission_rate=Decimal("0.001"))
        with pytest.raises(ValidationError):
            commission.commission_rate = Decimal("0.002")

    def test_trading_commission_from_json(self) -> None:
        """Test creating TradingCommission from JSON."""
        json_data = '{"commission_rate": 0.001}'
        commission = TradingCommission.model_validate_json(json_data)
        assert commission.commission_rate == Decimal("0.001")

    def test_trading_commission_invalid_type(self) -> None:
        """Test creating TradingCommission with invalid type."""
        with pytest.raises(ValidationError):
            TradingCommission(commission_rate="invalid")  # type: ignore

    def test_trading_commission_missing_field(self) -> None:
        """Test when required field is missing."""
        with pytest.raises(ValidationError):
            TradingCommission()  # type: ignore[call-arg]
