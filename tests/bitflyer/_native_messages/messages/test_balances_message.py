"""Tests for BalancesMessage"""

from decimal import Decimal

import pytest

from crypto_api_client.bitflyer._native_messages.balances_message import (
    BalancesMessage,
)
from crypto_api_client.bitflyer.native_domain_models.balance import Balance


class TestBalancesMessage:
    """Tests for BalancesMessage class"""

    @pytest.fixture
    def valid_balances_json(self) -> str:
        """Valid balance JSON data (array)"""
        return """[
            {
                "currency_code": "JPY",
                "amount": 1024078,
                "available": 508000
            },
            {
                "currency_code": "BTC",
                "amount": 10.24,
                "available": 4.12
            },
            {
                "currency_code": "ETH",
                "amount": 20.48,
                "available": 16.38
            }
        ]"""

    def test_init_with_valid_json(self, valid_balances_json: str) -> None:
        """Test initialization with valid JSON"""
        message = BalancesMessage(valid_balances_json)

        assert message.metadata is None
        assert message.payload is not None
        assert message.payload.content_str == valid_balances_json

    def test_to_domain_model(self, valid_balances_json: str) -> None:
        """Test conversion to domain model"""
        message = BalancesMessage(valid_balances_json)

        balances = message.to_domain_model()
        assert isinstance(balances, list)
        assert len(balances) == 3

        # Verify JPY balance
        jpy_balance = balances[0]
        assert isinstance(jpy_balance, Balance)
        assert jpy_balance.currency_code == "JPY"
        assert jpy_balance.amount == Decimal("1024078")
        assert jpy_balance.available == Decimal("508000")

        # Verify BTC balance
        btc_balance = balances[1]
        assert btc_balance.currency_code == "BTC"
        assert btc_balance.amount == Decimal("10.24")
        assert btc_balance.available == Decimal("4.12")

    def test_to_balances_alias_method(self, valid_balances_json: str) -> None:
        """Test to_domain_model method (no alias method exists)"""
        message = BalancesMessage(valid_balances_json)

        balances = message.to_domain_model()
        assert len(balances) == 3
        assert balances[0].currency_code == "JPY"
        assert balances[0].amount == Decimal("1024078")

    def test_empty_balances(self) -> None:
        """Test conversion with empty balance list"""
        message = BalancesMessage("[]")

        balances = message.to_domain_model()
        assert isinstance(balances, list)
        assert len(balances) == 0
