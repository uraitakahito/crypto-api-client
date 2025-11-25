"""WithdrawalFee model tests"""

from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from crypto_api_client.bitbank.native_domain_models import WithdrawalFee


class TestWithdrawalFee:
    """WithdrawalFee model tests"""

    def test_withdrawal_fee_fiat_valid(self) -> None:
        """Create valid WithdrawalFee for fiat currency"""
        fee = WithdrawalFee(
            threshold=Decimal("30000.0000"),
            under=Decimal("550.0000"),
            over=Decimal("770.0000"),
        )
        assert fee.threshold == Decimal("30000.0000")
        assert fee.under == Decimal("550.0000")
        assert fee.over == Decimal("770.0000")
        assert fee.min is None
        assert fee.max is None

    def test_withdrawal_fee_crypto_valid(self) -> None:
        """Create valid WithdrawalFee for cryptocurrency"""
        fee = WithdrawalFee(
            min=Decimal("0.00060000"),
            max=Decimal("0.00060000"),
        )
        assert fee.min == Decimal("0.00060000")
        assert fee.max == Decimal("0.00060000")
        assert fee.threshold is None
        assert fee.under is None
        assert fee.over is None

    def test_withdrawal_fee_fiat_from_dict(self) -> None:
        """Create WithdrawalFee for fiat currency from dictionary"""
        data: dict[str, Any] = {
            "threshold": Decimal("30000.0000"),
            "under": Decimal("550.0000"),
            "over": Decimal("770.0000"),
        }
        fee = WithdrawalFee(**data)
        assert fee.threshold == Decimal("30000.0000")
        assert fee.under == Decimal("550.0000")
        assert fee.over == Decimal("770.0000")

    def test_withdrawal_fee_crypto_from_dict(self) -> None:
        """Create WithdrawalFee for cryptocurrency from dictionary"""
        data: dict[str, Any] = {
            "min": Decimal("0.00060000"),
            "max": Decimal("0.00060000"),
        }
        fee = WithdrawalFee(**data)
        assert fee.min == Decimal("0.00060000")
        assert fee.max == Decimal("0.00060000")

    def test_withdrawal_fee_frozen(self) -> None:
        """Verify WithdrawalFee is immutable"""
        fee = WithdrawalFee(
            threshold=Decimal(30000),
            under=Decimal(550),
            over=Decimal(770),
        )
        with pytest.raises(ValidationError, match="frozen"):
            fee.threshold = Decimal(40000)  # type: ignore

    def test_withdrawal_fee_mixed_fields_error(self) -> None:
        """Error when mixing fiat and cryptocurrency fields"""
        with pytest.raises(ValidationError, match="Cannot have both fiat"):
            WithdrawalFee(
                threshold=Decimal(30000),
                under=Decimal(550),
                over=Decimal(770),
                min=Decimal("0.001"),
                max=Decimal("0.001"),
            )

    def test_withdrawal_fee_incomplete_fiat_error(self) -> None:
        """Error when fiat currency fields are incomplete"""
        with pytest.raises(ValidationError, match="All fiat fee fields"):
            WithdrawalFee(
                threshold=Decimal(30000),
                under=Decimal(550),
                # over is missing
            )

    def test_withdrawal_fee_incomplete_crypto_error(self) -> None:
        """Error when cryptocurrency fields are incomplete"""
        with pytest.raises(ValidationError, match="All crypto fee fields"):
            WithdrawalFee(
                min=Decimal("0.001"),
                # max is missing
            )

    def test_withdrawal_fee_no_fields_error(self) -> None:
        """Error when no fields are set"""
        with pytest.raises(ValidationError, match="Must have either fiat"):
            WithdrawalFee()

    def test_withdrawal_fee_btc_example(self) -> None:
        """BTC withdrawal fee example (cryptocurrency format)"""
        fee = WithdrawalFee(
            min=Decimal("0.00060000"),
            max=Decimal("0.00060000"),
        )
        assert fee.min == Decimal("0.00060000")
        assert fee.max == Decimal("0.00060000")

    def test_withdrawal_fee_jpy_example(self) -> None:
        """JPY withdrawal fee example (fiat currency format)"""
        fee = WithdrawalFee(
            threshold=Decimal("30000.0000"),
            under=Decimal("550.0000"),
            over=Decimal("770.0000"),
        )
        assert fee.threshold == Decimal("30000.0000")
        assert fee.under == Decimal("550.0000")
        assert fee.over == Decimal("770.0000")

    def test_withdrawal_fee_zero_values_fiat(self) -> None:
        """Fiat WithdrawalFee with zero values"""
        fee = WithdrawalFee(
            threshold=Decimal(0),
            under=Decimal(0),
            over=Decimal(0),
        )
        assert fee.threshold == Decimal("0")
        assert fee.under == Decimal("0")
        assert fee.over == Decimal("0")

    def test_withdrawal_fee_zero_values_crypto(self) -> None:
        """Cryptocurrency WithdrawalFee with zero values"""
        fee = WithdrawalFee(
            min=Decimal(0),
            max=Decimal(0),
        )
        assert fee.min == Decimal("0")
        assert fee.max == Decimal("0")

    def test_withdrawal_fee_high_precision(self) -> None:
        """WithdrawalFee with high precision decimals"""
        fee = WithdrawalFee(
            threshold=Decimal("0.123456789012345678"),
            under=Decimal("0.000000000000000001"),
            over=Decimal("999999999999999999.999999999999999999"),
        )
        assert fee.threshold == Decimal("0.123456789012345678")
        assert fee.under == Decimal("0.000000000000000001")
        assert fee.over == Decimal("999999999999999999.999999999999999999")
