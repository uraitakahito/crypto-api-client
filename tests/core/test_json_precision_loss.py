"""Tests for JSON numeric precision loss (TDD: Red Phase)."""

from decimal import Decimal

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser


class TestJsonPrecisionLoss:
    """Tests for JSON numeric precision loss."""

    def test_high_precision_float_loss(self) -> None:
        """Verify precision loss for high-precision decimals."""
        # JSON containing high-precision number
        json_str = '{"best_bid": 0.12345678901234567890}'

        # Confirm that precision is preserved in current implementation
        result = DecimalJsonParser.parse(json_str, dict)  # type: ignore

        # Expected: original value should be preserved
        expected = "0.12345678901234567890"
        actual = str(result["best_bid"])  # type: ignore

        # This test should pass (precision preserved with Decimal)
        assert actual == expected, f"Precision loss: {expected} -> {actual}"

    def test_small_decimal_precision(self) -> None:
        """Verify precision loss for very small values."""
        json_str = '{"amount": 0.000000000000000001}'

        result = DecimalJsonParser.parse(json_str, dict)  # type: ignore

        # Decimal may display in exponential notation, but value is preserved
        assert isinstance(result["amount"], Decimal)  # type: ignore
        # Compare as numeric value
        assert result["amount"] == Decimal("0.000000000000000001")  # type: ignore
        # Confirm precision is preserved (string representation may be 1E-18)
        assert result["amount"] == Decimal("1E-18")  # type: ignore

    def test_large_number_precision(self) -> None:
        """Verify precision loss for large numbers."""
        json_str = '{"total": 999999999999999999.123456789}'

        result = DecimalJsonParser.parse(json_str, dict)  # type: ignore

        expected = "999999999999999999.123456789"
        actual = str(result["total"])  # type: ignore

        assert actual == expected, f"Large number precision loss: {expected} -> {actual}"
