"""Coincheck CurrencyBalance domain model tests"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from crypto_api_client.coincheck.native_domain_models.currency_balance import (
    CurrencyBalance,
)


class TestCurrencyBalance:
    """Tests for CurrencyBalance domain model"""

    def test_currency_balance_minimal(self):
        """Create instance with minimal fields"""
        balance = CurrencyBalance(
            currency="btc",
            available=Decimal("1.5"),
        )

        assert balance.currency == "btc"
        assert balance.available == Decimal("1.5")
        assert balance.reserved == Decimal(0)
        assert balance.lending == Decimal(0)
        assert balance.lend_in_use == Decimal(0)
        assert balance.lent == Decimal(0)
        assert balance.debt == Decimal(0)
        assert balance.tsumitate == Decimal(0)

    def test_currency_balance_full(self):
        """Create instance with all fields"""
        balance = CurrencyBalance(
            currency="btc",
            available=Decimal("7.75052654"),
            reserved=Decimal("3.5002"),
            lending=Decimal("0.1"),
            lend_in_use=Decimal("0.3"),
            lent=Decimal("1.2"),
            debt=Decimal("0.05"),
            tsumitate=Decimal("0.4034"),
        )

        assert balance.currency == "btc"
        assert balance.available == Decimal("7.75052654")
        assert balance.reserved == Decimal("3.5002")
        assert balance.lending == Decimal("0.1")
        assert balance.lend_in_use == Decimal("0.3")
        assert balance.lent == Decimal("1.2")
        assert balance.debt == Decimal("0.05")
        assert balance.tsumitate == Decimal("0.4034")

    def test_currency_balance_frozen(self):
        """Verify that it is frozen"""
        balance = CurrencyBalance(
            currency="btc",
            available=Decimal("1.0"),
        )

        with pytest.raises(ValidationError):
            balance.currency = "eth"  # type: ignore[misc]

    def test_currency_balance_validation_currency_required(self):
        """currency is required"""
        with pytest.raises(ValidationError):
            CurrencyBalance(available=Decimal("1.0"))  # type: ignore[call-arg]

    def test_currency_balance_validation_available_required(self):
        """available is required"""
        with pytest.raises(ValidationError):
            CurrencyBalance(currency="btc")  # type: ignore[call-arg]

    def test_currency_balance_string_to_decimal(self):
        """Verify that strings are converted to Decimal"""
        balance = CurrencyBalance(
            currency="btc",
            available="1.5",  # type: ignore[arg-type]
            reserved="0.5",  # type: ignore[arg-type]
        )

        assert isinstance(balance.available, Decimal)
        assert isinstance(balance.reserved, Decimal)
        assert balance.available == Decimal("1.5")
        assert balance.reserved == Decimal("0.5")
