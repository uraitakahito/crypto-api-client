"""Tests to verify precision of each API response model (TDD: Red Phase)"""

from crypto_api_client.bitflyer.native_domain_models.balance import Balance
from crypto_api_client.bitflyer.native_domain_models.public_execution import (
    PublicExecution,
)
from crypto_api_client.core.decimal_json_parser import DecimalJsonParser


class TestApiResponsePrecision:
    """Verify precision of each API response model"""

    def test_execution_payload_precision(self) -> None:
        """Verify precision of execution data"""
        json_str = """{
            "id": 12345,
            "side": "BUY",
            "price": 0.00000001,
            "size": 999999999.123456789012345678,
            "exec_date": "2025-01-15T10:00:00.000Z",
            "buy_child_order_acceptance_id": "ABC123",
            "sell_child_order_acceptance_id": "DEF456",
            "commission": 0.000000000000000001
        }"""

        # Parse with current implementation
        execution = DecimalJsonParser.parse(json_str, PublicExecution)

        # Verify precision is maintained in Execution model
        # Decimal expresses very small values in scientific notation
        assert str(execution.price) == "1E-8"  # Scientific notation of 0.00000001
        assert str(execution.size) == "999999999.123456789012345678"

    def test_balance_payload_precision(self) -> None:
        """Verify precision of balance data"""
        json_str = """{
            "currency_code": "BTC",
            "amount": 123.456789012345678901234567890,
            "available": 100.123456789012345678901234567890
        }"""

        balance = DecimalJsonParser.parse(json_str, Balance)

        # Precision is maintained through Decimal parsing in Balance model
        assert str(balance.amount) == "123.456789012345678901234567890"
        assert str(balance.available) == "100.123456789012345678901234567890"

    def test_extreme_precision_values(self) -> None:
        """Test values with extreme precision"""
        # Precision of 50 decimal places
        json_str = """{
            "value": 0.12345678901234567890123456789012345678901234567890
        }"""

        result = DecimalJsonParser.parse(json_str, dict)  # type: ignore[arg-type]

        # Verify precision that cannot be represented by Python float is maintained
        expected_str = "0.12345678901234567890123456789012345678901234567890"
        actual_str = str(result["value"])  # type: ignore[index]

        assert actual_str == expected_str, (
            f"Extreme precision was lost: {expected_str} → {actual_str}"
        )
