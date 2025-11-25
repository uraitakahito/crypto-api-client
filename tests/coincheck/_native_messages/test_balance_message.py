"""Coincheck Balance message tests"""

from decimal import Decimal

from crypto_api_client.coincheck._native_messages.balance_message import BalanceMessage
from crypto_api_client.coincheck._native_messages.message_metadata import (
    MessageMetadata,
)


class TestBalanceMessage:
    """Tests for BalanceMessage."""

    def test_balance_message_to_domain_model(self):
        """Test conversion from BalanceMessage to Domain Model."""
        json_str = """{
            "success": true,
            "jpy": "1000.8401",
            "btc": "7.75052654",
            "jpy_reserved": "3000.0",
            "btc_reserved": "3.5002"
        }"""

        message = BalanceMessage(json_str)
        balances = message.to_domain_model()

        # Verify it is a list
        assert isinstance(balances, list)
        assert len(balances) == 2

        # Verify sorted by currency (btc, jpy)
        btc_balance = balances[0]
        jpy_balance = balances[1]

        assert btc_balance.currency == "btc"
        assert btc_balance.available == Decimal("7.75052654")
        assert btc_balance.reserved == Decimal("3.5002")

        assert jpy_balance.currency == "jpy"
        assert jpy_balance.available == Decimal("1000.8401")
        assert jpy_balance.reserved == Decimal("3000.0")

    def test_balance_message_full_response(self):
        """Test with complete response (sample from official documentation)."""
        json_str = """{
            "success": true,
            "jpy": "0.8401",
            "btc": "7.75052654",
            "jpy_reserved": "3000.0",
            "btc_reserved": "3.5002",
            "jpy_lending": "0",
            "btc_lending": "0.1",
            "jpy_lend_in_use": "0",
            "btc_lend_in_use": "0.3",
            "jpy_lent": "0",
            "btc_lent": "1.2",
            "jpy_debt": "0",
            "btc_debt": "0",
            "jpy_tsumitate": "10000.0",
            "btc_tsumitate": "0.4034"
        }"""

        message = BalanceMessage(json_str)
        balances = message.to_domain_model()

        assert len(balances) == 2

        # Find BTC
        btc_balance = next((b for b in balances if b.currency == "btc"), None)
        assert btc_balance is not None
        assert btc_balance.available == Decimal("7.75052654")
        assert btc_balance.reserved == Decimal("3.5002")
        assert btc_balance.lending == Decimal("0.1")
        assert btc_balance.lend_in_use == Decimal("0.3")
        assert btc_balance.lent == Decimal("1.2")
        assert btc_balance.debt == Decimal("0")
        assert btc_balance.tsumitate == Decimal("0.4034")

        # Find JPY
        jpy_balance = next((b for b in balances if b.currency == "jpy"), None)
        assert jpy_balance is not None
        assert jpy_balance.available == Decimal("0.8401")
        assert jpy_balance.reserved == Decimal("3000.0")
        assert jpy_balance.lending == Decimal("0")
        assert jpy_balance.lend_in_use == Decimal("0")
        assert jpy_balance.lent == Decimal("0")
        assert jpy_balance.debt == Decimal("0")
        assert jpy_balance.tsumitate == Decimal("10000.0")

    def test_balance_message_single_currency(self):
        """Test response with single currency only."""
        json_str = """{
            "success": true,
            "btc": "1.0"
        }"""

        message = BalanceMessage(json_str)
        balances = message.to_domain_model()

        assert len(balances) == 1
        assert balances[0].currency == "btc"
        assert balances[0].available == Decimal("1.0")
        # Verify default values
        assert balances[0].reserved == Decimal(0)
        assert balances[0].lending == Decimal(0)

    def test_balance_message_no_currencies(self):
        """Test when no currencies exist (success only)."""
        json_str = """{
            "success": true
        }"""

        message = BalanceMessage(json_str)
        balances = message.to_domain_model()

        assert isinstance(balances, list)
        assert len(balances) == 0

    def test_balance_message_precision_with_numeric_values(self):
        """Test that precision is preserved even when API returns numeric values.

        Verifies that precision is maintained by parse_float=Decimal
        even if API specification changes from string to numeric values.
        """
        # 30-digit high-precision number (cannot be represented as float)
        json_str = """{
            "success": true,
            "btc": 0.123456789012345678901234567890,
            "btc_reserved": 0.987654321098765432109876543210
        }"""

        message = BalanceMessage(json_str)
        balances = message.to_domain_model()

        assert len(balances) == 1
        btc_balance = balances[0]

        # Verify precision is preserved as Decimal type
        # (float would round to ~17 digits)
        assert btc_balance.available == Decimal("0.123456789012345678901234567890")
        assert btc_balance.reserved == Decimal("0.987654321098765432109876543210")

        # Verify type
        assert isinstance(btc_balance.available, Decimal)
        assert isinstance(btc_balance.reserved, Decimal)

    def test_balance_message_has_metadata(self):
        """Test that Balance Message has metadata."""
        json_str = """{
            "success": true,
            "btc": "7.75052654",
            "btc_reserved": "3.5002"
        }"""

        message = BalanceMessage(json_str)

        # Verify metadata
        assert message.metadata is not None
        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success is True
        assert message.metadata.json_str == '{"success": true}'

    def test_balance_message_metadata_false(self):
        """Test when success=false."""
        json_str = '{"success": false}'

        message = BalanceMessage(json_str)

        assert message.metadata is not None
        assert message.metadata.success is False

    def test_balance_message_metadata_integration(self):
        """Integration test for metadata and domain model."""
        json_str = """{
            "success": true,
            "btc": "1.5",
            "jpy": "10000"
        }"""

        message = BalanceMessage(json_str)

        # Verify metadata
        assert message.metadata is not None
        assert message.metadata.success is True

        # Verify domain model
        balances = message.to_domain_model()
        assert len(balances) == 2
        assert balances[0].currency == "btc"
        assert balances[1].currency == "jpy"

    def test_balance_message_payload_excludes_success(self):
        """Test that BalancePayload does not contain success field."""
        json_str = """{
            "success": true,
            "jpy": "1000.0",
            "btc": "2.5"
        }"""

        message = BalanceMessage(json_str)

        # Verify payload content_str does not contain success
        payload_content = message.payload.content_str
        assert "success" not in payload_content

        # Verify metadata is correctly extracted
        assert message.metadata is not None
        assert message.metadata.success is True

        # Verify domain model conversion works correctly
        balances = message.to_domain_model()
        assert len(balances) == 2

    def test_balance_message_payload_structure(self):
        """Test that Payload contains only pure payload."""
        import json

        json_str = """{
            "success": true,
            "jpy": "1000.0",
            "btc": "2.5",
            "jpy_reserved": "100.0"
        }"""

        message = BalanceMessage(json_str)
        payload_data = json.loads(message.payload.content_str)

        # Verify success key does not exist
        assert "success" not in payload_data

        # Verify all payload keys exist
        assert "jpy" in payload_data
        assert "btc" in payload_data
        assert "jpy_reserved" in payload_data

        # Verify values are correct
        assert payload_data["jpy"] == "1000.0"
        assert payload_data["btc"] == "2.5"
