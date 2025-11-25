"""Module providing common Decimal precision preservation test patterns.

This module provides patterns commonly used in JSON-to-model conversion Decimal
precision tests, reducing test code duplication and providing helpers for consistency.
"""

import json
from decimal import Decimal
from typing import Any, Dict, Type, TypeVar

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

# Type variable for model types
T = TypeVar("T")


class DecimalPrecisionTestMixin:
    """Mixin providing common patterns for Decimal precision preservation tests."""

    def assert_decimal_precision_preserved(
        self,
        model_class: Type[T],
        json_data: Dict[str, Any],
        decimal_field_mappings: Dict[str, str],
    ) -> T:
        """Test that Decimal precision is preserved in JSON-to-model conversion.

        :param model_class: Model class to test
        :param json_data: JSON data (as dictionary)
        :param decimal_field_mappings: Dict of {field_name: expected_string_value}
        :return: Converted model instance
        """
        json_str = json.dumps(json_data)
        instance = DecimalJsonParser.parse(json_str, model_class)

        for field_name, expected_str_value in decimal_field_mappings.items():
            actual_value = getattr(instance, field_name)

            # Verify it's Decimal type
            assert isinstance(actual_value, Decimal), (
                f"Field '{field_name}' should be Decimal, got {type(actual_value)}"
            )

            # Verify precision is preserved
            assert str(actual_value) == expected_str_value, (
                f"Field '{field_name}' precision not preserved. Expected: {expected_str_value}, Got: {str(actual_value)}"
            )

        return instance

    def assert_float_vs_decimal_precision_difference(
        self, high_precision_value: str
    ) -> None:
        """Common test to verify precision difference between float and Decimal.

        :param high_precision_value: High-precision numeric string
        """
        # When processed with float (precision is lost)
        float_value = float(high_precision_value)
        decimal_from_float = Decimal(str(float_value))

        # When processed directly with Decimal (precision is preserved)
        decimal_direct = Decimal(high_precision_value)

        # Verify precision differs
        assert str(decimal_from_float) != high_precision_value, (
            "Float should lose precision"
        )
        assert str(decimal_direct) == high_precision_value, (
            "Decimal should preserve precision"
        )


class DecimalPrecisionTestPatterns:
    """Class providing common test data and patterns for Decimal precision preservation tests."""

    # High-precision test data
    HIGH_PRECISION_30_DIGITS = "1.123456789012345678901234567890"
    HIGH_PRECISION_SMALL = "0.000001234567890123456789012345"
    HIGH_PRECISION_LARGE_PRICE = "9876543.210987654321098765432109"
    VERY_SMALL_NUMBER = "0.000000000000000000000000000001"
    VERY_LARGE_NUMBER = "999999999999999999999999999999.123456789"

    @classmethod
    def create_balance_test_data(cls) -> Dict[str, Any]:
        """Create high-precision test data for Balance."""
        return {
            "currency_code": "BTC",
            "amount": cls.HIGH_PRECISION_30_DIGITS,
            "available": "0.987654321098765432109876543210",
        }

    @classmethod
    def create_execution_test_data(cls) -> Dict[str, Any]:
        """Create high-precision test data for Execution."""
        return {
            "id": 123456789,
            "side": "BUY",
            "price": cls.HIGH_PRECISION_LARGE_PRICE,
            "size": cls.HIGH_PRECISION_SMALL,
            "exec_date": "2024-01-01T00:00:00.000",
            "buy_child_order_acceptance_id": "JRF20240101-000001",
            "sell_child_order_acceptance_id": "JRF20240101-000002",
        }

    @classmethod
    def create_child_order_test_data(cls) -> Dict[str, Any]:
        """Create high-precision test data for ChildOrder."""
        return {
            "id": 123456789,
            "child_order_id": "JOR20250101-000000-000000",
            "product_code": "BTC_JPY",
            "side": "BUY",
            "child_order_type": "LIMIT",
            "price": cls.HIGH_PRECISION_LARGE_PRICE,
            "average_price": "9876543.098765432109876543210987",
            "size": "0.000001111111111111111111111111",
            "child_order_state": "ACTIVE",
            "expire_date": "2024-12-31T23:59:59",
            "child_order_date": "2024-01-01T00:00:00",
            "child_order_acceptance_id": "JRF20240101-000000",
            "outstanding_size": "0.000000555555555555555555555555",
            "cancel_size": "0.000000222222222222222222222222",
            "executed_size": "0.000000333333333333333333333333",
            "total_commission": "12.345678901234567890123456789",
            "time_in_force": "GTC",
        }

    @classmethod
    def create_very_small_numbers_test_data(cls) -> Dict[str, Any]:
        """Create test data for very small numbers."""
        return {
            "currency_code": "BTC",
            "amount": cls.VERY_SMALL_NUMBER,
            "available": cls.VERY_SMALL_NUMBER,
        }

    @classmethod
    def create_very_large_numbers_test_data(cls) -> Dict[str, Any]:
        """Create test data for very large numbers."""
        return {
            "currency_code": "JPY",
            "amount": cls.VERY_LARGE_NUMBER,
            "available": "888888888888888888888888888888.987654321",
        }


class StandardDecimalPrecisionTests(DecimalPrecisionTestMixin):
    """Class providing standard Decimal precision preservation test cases."""

    def test_balance_decimal_precision(self) -> None:
        """Test numeric precision preservation in Balance model."""
        json_data = DecimalPrecisionTestPatterns.create_balance_test_data()
        decimal_mappings = {
            "amount": DecimalPrecisionTestPatterns.HIGH_PRECISION_30_DIGITS,
            "available": "0.987654321098765432109876543210",
        }

        from crypto_api_client.bitflyer.native_domain_models.balance import Balance

        self.assert_decimal_precision_preserved(Balance, json_data, decimal_mappings)

    def test_execution_decimal_precision(self) -> None:
        """Test numeric precision preservation in Execution model."""
        json_data = DecimalPrecisionTestPatterns.create_execution_test_data()
        decimal_mappings = {
            "price": DecimalPrecisionTestPatterns.HIGH_PRECISION_LARGE_PRICE,
            "size": DecimalPrecisionTestPatterns.HIGH_PRECISION_SMALL,
        }

        from crypto_api_client.bitflyer.native_domain_models.public_execution import (
            PublicExecution,
        )

        self.assert_decimal_precision_preserved(
            PublicExecution, json_data, decimal_mappings
        )

    def test_child_order_decimal_precision(self) -> None:
        """Test numeric precision preservation in ChildOrder model."""
        json_data = DecimalPrecisionTestPatterns.create_child_order_test_data()
        decimal_mappings = {
            "price": DecimalPrecisionTestPatterns.HIGH_PRECISION_LARGE_PRICE,
            "size": "0.000001111111111111111111111111",
            "total_commission": "12.345678901234567890123456789",
        }

        from crypto_api_client.bitflyer.native_domain_models.child_order import (
            ChildOrder,
        )

        self.assert_decimal_precision_preserved(ChildOrder, json_data, decimal_mappings)

    def test_float_vs_decimal_precision_comparison(self) -> None:
        """Test explicitly demonstrating precision difference between float and Decimal."""
        self.assert_float_vs_decimal_precision_difference(
            "0.123456789012345678901234567890"
        )

    def test_edge_case_very_small_numbers(self) -> None:
        """Test precision preservation with very small numbers."""
        import json
        from decimal import Decimal

        from crypto_api_client.bitflyer.native_domain_models.balance import Balance
        from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

        json_data = DecimalPrecisionTestPatterns.create_very_small_numbers_test_data()
        json_str = json.dumps(json_data)
        balance = DecimalJsonParser.parse(json_str, Balance)

        # Verify precision is preserved even for very small values
        # Decimal may display in scientific notation, but value is exact
        expected_decimal = Decimal(DecimalPrecisionTestPatterns.VERY_SMALL_NUMBER)
        assert balance.amount == expected_decimal
        assert balance.available == expected_decimal

        # Verify normalization
        assert f"{balance.amount:.30f}" == "0.000000000000000000000000000001"

    def test_edge_case_very_large_numbers(self) -> None:
        """Test precision preservation with very large numbers."""
        json_data = DecimalPrecisionTestPatterns.create_very_large_numbers_test_data()
        decimal_mappings = {
            "amount": DecimalPrecisionTestPatterns.VERY_LARGE_NUMBER,
            "available": "888888888888888888888888888888.987654321",
        }

        from crypto_api_client.bitflyer.native_domain_models.balance import Balance

        self.assert_decimal_precision_preserved(Balance, json_data, decimal_mappings)
