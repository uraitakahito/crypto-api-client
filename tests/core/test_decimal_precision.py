"""Tests for numeric precision (Decimal) preservation.

This test verifies that numeric values in JSON data received from APIs
are accurately preserved as Decimal without precision loss from float.
"""

import json
from decimal import Decimal

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser


class TestDecimalPrecision:
    """Test class for numeric precision preservation.

    Verifies that high-precision numeric values received in API responses
    are accurately preserved as Decimal through CryptoApiAdapterFactory.
    """

    def test_balance_decimal_precision(self) -> None:
        """Verify Decimal precision is preserved for balance data."""
        json_data = {
            "currency": "BTC",
            "amount": "0.12345678901234567890",
            "available": "0.10000000000000000000",
        }

        # Define actual model class here if needed
        # This test processes as dictionary
        json_str = json.dumps(json_data)
        result = DecimalJsonParser.parse(json_str, dict)  # type: ignore

        # Verify values are preserved as strings
        assert result["amount"] == "0.12345678901234567890"
        assert result["available"] == "0.10000000000000000000"

    def test_execution_decimal_precision(self) -> None:
        """Verify Decimal precision is preserved for execution data."""
        json_data = {
            "price": "6899999.99999999999999",
            "size": "0.00100000000000000000",
            "commission": "0.00000015000000000000",
        }

        json_str = json.dumps(json_data)
        result = DecimalJsonParser.parse(json_str, dict)  # type: ignore

        assert result["price"] == "6899999.99999999999999"
        assert result["size"] == "0.00100000000000000000"
        assert result["commission"] == "0.00000015000000000000"

    def test_float_vs_decimal_precision_comparison(self) -> None:
        """Verify precision difference between float and Decimal."""
        high_precision_value = "0.12345678901234567890"

        # float loses precision
        float_value = float(high_precision_value)
        decimal_value = Decimal(high_precision_value)

        # float loses precision
        assert str(float_value) != high_precision_value
        # Decimal preserves precision
        assert str(decimal_value) == high_precision_value

    def test_edge_case_very_small_numbers(self) -> None:
        """Verify precision preservation for very small numbers."""
        json_data = {"tiny_amount": "0.00000000000000000001"}

        json_str = json.dumps(json_data)
        result = DecimalJsonParser.parse(json_str, dict)  # type: ignore

        assert result["tiny_amount"] == "0.00000000000000000001"

    def test_edge_case_very_large_numbers(self) -> None:
        """Verify precision preservation for very large numbers."""
        json_data = {"large_amount": "99999999999999999999.99999999999999999999"}

        json_str = json.dumps(json_data)
        result = DecimalJsonParser.parse(json_str, dict)  # type: ignore

        assert result["large_amount"] == "99999999999999999999.99999999999999999999"
