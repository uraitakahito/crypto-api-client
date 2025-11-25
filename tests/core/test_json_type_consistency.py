"""Tests to verify JSON numeric type consistency (TDD: Red Phase)."""

from decimal import Decimal
from typing import Any, Type

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser


class TestJsonTypeConsistency:
    """Tests to verify JSON numeric type consistency."""

    def test_integer_decimal_consistency(self) -> None:
        """Verify type consistency between integers and decimals."""
        test_cases = [
            '{"price": 100}',  # Integer
            '{"price": 100.0}',  # With decimal point
            '{"price": 100.00001}',  # Decimal
        ]

        types: list[Type[Any]] = []
        for json_str in test_cases:
            result = DecimalJsonParser.parse(json_str, dict)  # type: ignore
            types.append(type(result["price"]))  # type: ignore

        # All should be same type (Decimal)
        assert all(t == Decimal for t in types), (
            f"Type mismatch: {[t.__name__ for t in types]}"
        )

    def test_zero_value_consistency(self) -> None:
        """Verify type consistency for zero values."""
        test_cases = [
            '{"amount": 0}',  # Integer zero
            '{"amount": 0.0}',  # Decimal zero
            '{"amount": 0.00000000}',  # Zero with many decimal places
        ]

        types: list[Type[Any]] = []
        values: list[Any] = []
        for json_str in test_cases:
            result = DecimalJsonParser.parse(json_str, dict)  # type: ignore
            types.append(type(result["amount"]))  # type: ignore
            values.append(result["amount"])  # type: ignore

        # All should be same type (Decimal)
        assert all(t == Decimal for t in types), (
            f"Zero value type mismatch: {[t.__name__ for t in types]}"
        )

        # All should be same value (0)
        assert all(v == values[0] for v in values), f"Zero value mismatch: {values}"

    def test_exponential_notation_consistency(self) -> None:
        """Verify type consistency for exponential notation."""
        test_cases = [
            '{"value": 1e2}',  # 100
            '{"value": 1.0e2}',  # 100.0
            '{"value": 1e-2}',  # 0.01
            '{"value": 1.23e-4}',  # 0.000123
        ]

        types: list[Type[Any]] = []
        for json_str in test_cases:
            result = DecimalJsonParser.parse(json_str, dict)  # type: ignore
            types.append(type(result["value"]))  # type: ignore

        # All should be same type (Decimal)
        assert all(t == Decimal for t in types), (
            f"Exponential notation type mismatch: {[t.__name__ for t in types]}"
        )

    def test_mixed_numeric_fields(self) -> None:
        """Verify type consistency for multiple numeric fields."""
        json_str = """{
            "integer_field": 42,
            "float_field": 3.14,
            "zero_int": 0,
            "zero_float": 0.0,
            "exp_notation": 1e-6,
            "large_int": 999999999999999999,
            "small_float": 0.000000000001
        }"""

        result = DecimalJsonParser.parse(json_str, dict)  # type: ignore

        # All fields should be Decimal type
        for field_name, value in result.items():  # type: ignore[assignment]
            assert isinstance(value, Decimal), (
                f"{field_name} is not Decimal type: {type(value).__name__}"
            )  # type: ignore[arg-type]
