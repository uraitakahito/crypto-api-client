"""Validation Test Data Factory

Factory classes for generating test validation data.
Systematically generates test data for happy path, error cases, and edge cases.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Union

from .base import BaseTestDataBuilder, TestDataConfig


class ValidationDataConfig(TestDataConfig):
    """Extended configuration for validation testing"""

    # Edge case settings
    generate_edge_cases: bool = True
    max_string_length: int = 10000
    max_decimal_precision: int = 30

    # Boundary value settings
    min_price: Union[str, Decimal] = "0.00000001"
    max_price: Union[str, Decimal] = "999999999999.99999999"
    min_size: Union[str, Decimal] = "0.00000001"
    max_size: Union[str, Decimal] = "999999999.99999999"


class EdgeCaseDataBuilder(BaseTestDataBuilder):
    """Data builder specialized for edge cases"""

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {}

    def empty_strings(self) -> "EdgeCaseDataBuilder":
        """Edge cases for empty strings"""
        self._data = {"values": ["", "   ", "\t", "\n"]}
        return self

    def integer_values(self) -> "EdgeCaseDataBuilder":
        """Edge cases for integer values"""
        self._data = {"values": [0, 123, -456, 999999999999999999]}
        return self

    def unsupported_types(self) -> "EdgeCaseDataBuilder":
        """Edge cases for unsupported types"""
        self._data = {"values": [[], {}, object(), complex(1, 2)]}
        return self

    def boundary_values(self, data_type: str) -> "EdgeCaseDataBuilder":
        """Generate boundary value data"""
        # config is always ValidationDataConfig at this point
        self.config = ValidationDataConfig()

        if data_type == "decimal_precision":
            self._data = {
                "min_precision": "0.00000001",
                "max_precision": "999999999999.99999999999999999999999999999999",
                "zero": "0.0",
                "very_small": "0.000000000000000000000000000001",
                "very_large": "999999999999999999999999999999.999999999",
            }
        elif data_type == "string_length":
            self._data = {
                "empty": "",
                "single_char": "a",
                "normal": "BTC_JPY",
                "max_length": "A" * self.config.max_string_length,
                "over_max": "B" * (self.config.max_string_length + 1),
            }
        elif data_type == "timestamp":
            now = datetime.now()
            self._data = {
                "past": (now - timedelta(days=365)).isoformat(),
                "now": now.isoformat(),
                "future": (now + timedelta(days=365)).isoformat(),
                "epoch": "1970-01-01T00:00:00.000000",
                "far_future": "2099-12-31T23:59:59.999999",
            }

        return self

    def invalid_values(self, data_type: str) -> "EdgeCaseDataBuilder":
        """Generate invalid value data"""
        if data_type == "product_code":
            self._data = {
                "empty": "",
                "null": None,
                "invalid_format": "INVALID_PAIR",
                "non_existent": "XXX_YYY",
                "special_chars": "BTC@JPY",
                "spaces": "BTC JPY",
                "lowercase": "btc_jpy",
                "numbers": "123_456",
            }
        elif data_type == "numeric":
            self._data = {
                "negative": "-1.0",
                "zero": "0",
                "string": "not_a_number",
                "null": None,
                "infinity": "inf",
                "nan": "nan",
                "empty_string": "",
                "special_chars": "12.34@",
            }
        elif data_type == "boolean":
            self._data = {
                "string_true": "true",
                "string_false": "false",
                "number_zero": 0,
                "number_one": 1,
                "null": None,
                "empty_string": "",
            }

        return self

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class ErrorScenarioBuilder(BaseTestDataBuilder):
    """Builder specialized for error scenarios"""

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {
            "scenario_type": "validation_error",
            "expected_error": "ValidationError",
            "test_data": {},
            "error_message_pattern": "",
        }

    def invalid_decimal_strings(self) -> "ErrorScenarioBuilder":
        """Error cases for invalid Decimal strings"""
        self._data = {
            "values": ["abc", "12.34.56", "12a34", "not_a_number", "12.34.56.78"]
        }
        return self

    def negative_decimals(self) -> "ErrorScenarioBuilder":
        """Error cases for negative Decimal values"""
        self._data = {"values": ["-1", "-0.01", -123.45, Decimal("-999.99")]}
        return self

    def max_digits_exceeded(self, max_digits: int) -> "ErrorScenarioBuilder":
        """Error cases for exceeding maximum digit count"""
        self._data = {"values": ["123456", "123.456", "1234567890"]}
        return self

    def validation_error(
        self,
        field_name: str,
        invalid_value: Any,
        expected_pattern: str = "Input should be",
    ) -> "ErrorScenarioBuilder":
        """Validation error scenario"""
        return (
            self._set_field("scenario_type", "validation_error")
            ._set_field("expected_error", "ValidationError")
            ._set_field("test_data", {field_name: invalid_value})
            ._set_field("error_message_pattern", expected_pattern)
        )

    def api_error(
        self, error_code: str, error_message: str, http_status: int = 400
    ) -> "ErrorScenarioBuilder":
        """API error scenario"""
        return (
            self._set_field("scenario_type", "api_error")
            ._set_field("expected_error", "APIError")
            ._set_field(
                "test_data",
                {
                    "error_code": error_code,
                    "error_message": error_message,
                    "http_status": http_status,
                },
            )
        )

    def timeout_error(self, timeout_seconds: float = 30.0) -> "ErrorScenarioBuilder":
        """Timeout error scenario"""
        return (
            self._set_field("scenario_type", "timeout_error")
            ._set_field("expected_error", "TimeoutError")
            ._set_field("test_data", {"timeout": timeout_seconds})
        )

    def network_error(
        self, error_type: str = "connection_error"
    ) -> "ErrorScenarioBuilder":
        """Network error scenario"""
        return (
            self._set_field("scenario_type", "network_error")
            ._set_field("expected_error", "NetworkError")
            ._set_field("test_data", {"error_type": error_type})
        )

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class TestScenarioBuilder(BaseTestDataBuilder):
    """Integrated test scenario builder"""

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {
            "scenario_id": str(uuid.uuid4()),
            "description": "",
            "test_type": "functional",
            "expected_result": "success",
            "test_data": {},
            "assertions": [],
        }

    def valid_positive_decimals(self) -> "TestScenarioBuilder":
        """Test cases for valid positive Decimal values"""
        self._data = {"values": ["0", "123.45", 0, 999.99]}
        return self

    def max_digits_valid(self, max_digits: int) -> "TestScenarioBuilder":
        """Valid values within maximum digit count"""
        self._data = {"values": ["123.45", "12345", "0.1234", "99999"]}
        return self

    def valid_product_codes(self) -> "TestScenarioBuilder":
        """List of valid product codes"""
        self._data = {
            "values": ["BTC_JPY", "ETH_JPY", "XRP_JPY", "MONA_JPY", "XLM_JPY"]
        }
        return self

    def decimal_performance_values(self) -> "TestScenarioBuilder":
        """Values for Decimal performance testing"""
        self._data = {
            "values": ["123.456789", 123.456, Decimal("789.012345"), 0, "0.000000001"]
        }
        return self

    def bitflyer_enum_names(self) -> "TestScenarioBuilder":
        """List of expected bitFlyer Enum names"""
        self._data = {
            "values": [
                "ProductCode",
                "Currency",
                "Side",
                "ChildOrderType",
                "ChildOrderState",
                "MarketType",
                "HealthStatusType",
                "TimeInForce",
            ]
        }
        return self

    def crypto_decimal_names(self) -> "TestScenarioBuilder":
        """List of cryptocurrency Decimal validator names"""
        self._data = {"values": ["CryptoPrice", "CryptoAmount"]}
        return self

    def with_scenario_id(self, scenario_id: str) -> "TestScenarioBuilder":
        """Set scenario ID"""
        return self._set_field("scenario_id", scenario_id)

    def with_description(self, description: str) -> "TestScenarioBuilder":
        """Set scenario description"""
        return self._set_field("description", description)

    def with_test_type(self, test_type: str) -> "TestScenarioBuilder":
        """Set test type"""
        return self._set_field("test_type", test_type)

    def with_expected_result(self, expected_result: str) -> "TestScenarioBuilder":
        """Set expected result"""
        return self._set_field("expected_result", expected_result)

    def with_test_data(self, test_data: Dict[str, Any]) -> "TestScenarioBuilder":
        """Set test data"""
        return self._set_field("test_data", test_data)

    def add_assertion(self, assertion: str) -> "TestScenarioBuilder":
        """Add an assertion"""
        assertions = self._get_field("assertions", [])
        assertions.append(assertion)
        return self._set_field("assertions", assertions)

    def functional_test(
        self, description: str, test_data: Dict[str, Any]
    ) -> "TestScenarioBuilder":
        """Functional test scenario"""
        return (
            self.with_description(description)
            .with_test_type("functional")
            .with_expected_result("success")
            .with_test_data(test_data)
        )

    def error_test(
        self, description: str, test_data: Dict[str, Any], expected_error: str
    ) -> "TestScenarioBuilder":
        """Error test scenario"""
        return (
            self.with_description(description)
            .with_test_type("error")
            .with_expected_result("error")
            .with_test_data(test_data)
            .add_assertion(f"raises {expected_error}")
        )

    def performance_test(
        self, description: str, test_data: Dict[str, Any], max_time: float
    ) -> "TestScenarioBuilder":
        """Performance test scenario"""
        return (
            self.with_description(description)
            .with_test_type("performance")
            .with_expected_result("success")
            .with_test_data(test_data)
            .add_assertion(f"execution_time < {max_time}")
        )

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class ValidationTestCaseBuilder(BaseTestDataBuilder):
    """Builder specialized for validation test cases"""

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {"test_cases": []}

    def add_positive_test(
        self, description: str, factory_method: str, test_data: Dict[str, Any]
    ) -> "ValidationTestCaseBuilder":
        """Add a happy path test case"""
        test_case = {
            "type": "positive",
            "description": description,
            "factory_method": factory_method,
            "test_data": test_data,
            "expected_result": "success",
        }

        test_cases = self._get_field("test_cases", [])
        test_cases.append(test_case)
        return self._set_field("test_cases", test_cases)

    def add_negative_test(
        self,
        description: str,
        factory_method: str,
        test_data: Dict[str, Any],
        expected_error: str,
    ) -> "ValidationTestCaseBuilder":
        """Add an error case test case"""
        test_case = {
            "type": "negative",
            "description": description,
            "factory_method": factory_method,
            "test_data": test_data,
            "expected_result": "error",
            "expected_error": expected_error,
        }

        test_cases = self._get_field("test_cases", [])
        test_cases.append(test_case)
        return self._set_field("test_cases", test_cases)

    def bitflyer_ticker_validation_suite(self) -> "ValidationTestCaseBuilder":
        """bitFlyer ticker validation suite"""
        # Happy path test cases
        self.add_positive_test(
            "Valid BTC_JPY ticker",
            "BitFlyerDataFactory.ticker",
            {"product_code": "BTC_JPY"},
        )

        self.add_positive_test(
            "ETH_JPY ticker",
            "BitFlyerDataFactory.ticker",
            {"product_code": "ETH_JPY"},
        )

        # Error case test cases
        self.add_negative_test(
            "Invalid product code",
            "BitFlyerDataFactory.ticker",
            {"product_code": "INVALID_PAIR"},
            "ValidationError",
        )

        self.add_negative_test(
            "None product code",
            "BitFlyerDataFactory.ticker",
            {"product_code": None},
            "ValidationError",
        )

        return self

    def bitbank_asset_validation_suite(self) -> "ValidationTestCaseBuilder":
        """bitbank asset validation suite"""
        # Happy path
        self.add_positive_test(
            "Valid JPY asset",
            "BitbankDataFactory.asset",
            {"asset": "jpy", "onhand_amount": "100000.0"},
        )

        # Error case
        self.add_negative_test(
            "Invalid asset symbol",
            "BitbankDataFactory.asset",
            {"asset": "invalid_symbol"},
            "ValidationError",
        )

        return self

    def websocket_validation_suite(self) -> "ValidationTestCaseBuilder":
        """WebSocket validation suite"""
        # Happy path
        self.add_positive_test(
            "Valid ticker event",
            "WebSocketDataFactory.ticker_event",
            {"product_code": "BTC_JPY"},
        )

        # Error case
        self.add_negative_test(
            "Invalid timestamp format",
            "WebSocketDataFactory.ticker_event",
            {"timestamp": "invalid-timestamp"},
            "ValidationError",
        )

        return self

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class ValidationDataFactory:
    """Factory class for validation test data

    Provides entry points for generating happy path, error case, and edge case test data.
    """

    @staticmethod
    def edge_case(config: ValidationDataConfig | None = None) -> EdgeCaseDataBuilder:
        """Get edge case builder"""
        return EdgeCaseDataBuilder(config or ValidationDataConfig())

    @staticmethod
    def error_scenario(
        config: ValidationDataConfig | None = None,
    ) -> ErrorScenarioBuilder:
        """Get error scenario builder"""
        return ErrorScenarioBuilder(config or ValidationDataConfig())

    @staticmethod
    def test_scenario(
        config: ValidationDataConfig | None = None,
    ) -> TestScenarioBuilder:
        """Get test scenario builder"""
        return TestScenarioBuilder(config or ValidationDataConfig())

    @staticmethod
    def test_case_suite(
        config: ValidationDataConfig | None = None,
    ) -> ValidationTestCaseBuilder:
        """Get test case suite builder"""
        return ValidationTestCaseBuilder(config or ValidationDataConfig())

    # Special methods for Enhanced Validators
    @staticmethod
    def enum_conversion_cases():
        """Builder for Enum conversion test cases"""
        return _EnumConversionCasesBuilder()

    @staticmethod
    def decimal_conversion_cases():
        """Builder for Decimal conversion test cases"""
        return _DecimalConversionCasesBuilder()

    # Convenience methods
    @staticmethod
    def generate_boundary_decimal_values() -> Dict[str, Any]:
        """Generate boundary value Decimals"""
        return (
            ValidationDataFactory.edge_case()
            .boundary_values("decimal_precision")
            .build()
        )

    @staticmethod
    def generate_invalid_product_codes() -> Dict[str, Any]:
        """Generate invalid product codes"""
        return ValidationDataFactory.edge_case().invalid_values("product_code").build()

    @staticmethod
    def generate_invalid_numeric_values() -> Dict[str, Any]:
        """Generate invalid numeric values"""
        return ValidationDataFactory.edge_case().invalid_values("numeric").build()

    @staticmethod
    def create_bitflyer_validation_errors() -> List[Dict[str, Any]]:
        """Generate bitFlyer validation error cases"""
        scenarios: List[Dict[str, Any]] = []

        # Product code errors
        invalid_codes = ValidationDataFactory.generate_invalid_product_codes()
        for code_type, invalid_code in invalid_codes.items():
            scenario = (
                ValidationDataFactory.error_scenario()
                .validation_error("product_code", invalid_code, "Input should be")
                .build()
            )
            scenario["description"] = f"product code {code_type} error"
            scenarios.append(scenario)

        # Numeric errors
        invalid_numbers = ValidationDataFactory.generate_invalid_numeric_values()
        for num_type, invalid_num in invalid_numbers.items():
            scenario = (
                ValidationDataFactory.error_scenario()
                .validation_error("ltp", invalid_num, "Input should be")
                .build()
            )
            scenario["description"] = f"LTP {num_type} error"
            scenarios.append(scenario)

        return scenarios

    @staticmethod
    def create_comprehensive_test_suite() -> Dict[str, Any]:
        """Generate comprehensive test suite"""
        return (
            ValidationDataFactory.test_case_suite()
            .bitflyer_ticker_validation_suite()
            .bitbank_asset_validation_suite()
            .websocket_validation_suite()
            .build()
        )


class _EnumConversionCasesBuilder:
    """Test case builder specialized for Enum conversion"""

    def __init__(self):
        self._data = []

    # Commented out due to removal of currency-related functionality
    # def for_product_code(self):
    #     """Conversion test cases for Exchange pair (bitFlyer)"""
    #     from crypto_api_client.core.currency_pair import CurrencyPairConverter
    #     from crypto_api_client.core.exchange_types import Exchange
    #     from crypto_api_client.currency.currency_registry import CurrencyRegistry
    #
    #     btc = CurrencyRegistry.get_currency_for_exchange("BTC", Exchange.BITFLYER)
    #     jpy = CurrencyRegistry.get_currency_for_exchange("JPY", Exchange.BITFLYER)
    #     eth = CurrencyRegistry.get_currency_for_exchange("ETH", Exchange.BITFLYER)
    #
    #     if not btc or not jpy or not eth:
    #         raise ValueError("Currency not found")
    #
    #     btc_jpy_unified = CurrencyPairConverter.create_unified(btc, jpy)
    #     btc_jpy_pair = CurrencyPairConverter.to_exchange_pair(
    #         btc_jpy_unified, Exchange.BITFLYER
    #     )
    #     eth_jpy_unified = CurrencyPairConverter.create_unified(eth, jpy)
    #     eth_jpy_pair = CurrencyPairConverter.to_exchange_pair(
    #         eth_jpy_unified, Exchange.BITFLYER
    #     )
    #
    #     self._data = [
    #         ("btc_jpy", btc_jpy_pair),
    #         ("BTC_JPY", btc_jpy_pair),
    #         ("Btc_Jpy", btc_jpy_pair),
    #         ("eth_jpy", eth_jpy_pair),
    #     ]
    #     return self

    def for_side(self):
        """Conversion test cases for Side"""
        from crypto_api_client.bitflyer.native_domain_models.side import Side

        self._data = [
            ("buy", Side.BUY),
            ("SELL", Side.SELL),
            ("Buy", Side.BUY),
            ("sell", Side.SELL),
        ]
        return self

    def build(self):
        """Return test cases"""
        return self._data


class _DecimalConversionCasesBuilder:
    """Test case builder specialized for Decimal conversion"""

    def __init__(self):
        self._data = []

    def comprehensive(self):
        """Comprehensive Decimal conversion test cases"""
        self._data = [
            ("123.45", Decimal("123.45")),
            ("0.000000000000000001", Decimal("0.000000000000000001")),
            (
                "999999999999999999999.999999999999999999",
                Decimal("999999999999999999999.999999999999999999"),
            ),
            ("0", Decimal("0")),
            ("-123.45", Decimal("-123.45")),
        ]
        return self

    def float_precision(self):
        """Decimal conversion test cases that preserve float precision"""
        self._data = [
            (123.45, Decimal("123.45")),
            (0.1, Decimal("0.1")),
            (99.99, Decimal("99.99")),
        ]
        return self

    def edge_cases(self):
        """Edge cases for Decimal"""
        self._data = [
            ("0.0", Decimal("0.0")),
            ("0.00000001", Decimal("0.00000001")),
            ("999999999999.99999999", Decimal("999999999999.99999999")),
        ]
        return self

    def build(self):
        """Return test cases"""
        return self._data
