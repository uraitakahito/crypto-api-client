"""Base classes for Test Data Factory Pattern

This module provides base classes and configuration for test data factories.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, TypeVar, Union

T = TypeVar("T", bound="BaseTestDataBuilder")


@dataclass
class TestDataConfig:
    """Class for managing test data generation configuration"""

    __test__ = False  # Exclude from pytest collection

    # Default settings
    default_timestamp: str = "2025-01-10T13:50:43.957"
    default_product_code: str = "BTC_JPY"

    # Precision settings
    decimal_precision: int = 30
    price_precision: int = 2

    # API compliance settings
    use_api_spec_validation: bool = True


class BaseTestDataBuilder(ABC):
    """Base class for test data builders

    Each exchange's Factory inherits from this class.
    Builder Pattern enables data construction through method chaining.
    """

    def __init__(self, config: TestDataConfig | None = None):
        self.config = config or TestDataConfig()
        self._data: Dict[str, Any] = {}
        self._initialize_defaults()

    @abstractmethod
    def _initialize_defaults(self) -> None:
        """Initialize default values (implemented in subclasses)"""
        pass

    @abstractmethod
    def build(self) -> Dict[str, Any]:
        """Build and return data (implemented in subclasses)"""
        pass

    def to_json(self) -> str:
        """Return constructed data as JSON string"""
        data = self.build()
        return json.dumps(data, default=self._json_serializer)

    def _json_serializer(self, obj: Any) -> Any:
        """Custom handler for JSON serialization"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def _set_field(self: T, field_name: str, value: Any) -> T:
        """Helper method to set field value"""
        self._data[field_name] = value
        return self

    def _get_field(self, field_name: str, default: Any = None) -> Any:
        """Helper method to get field value"""
        return self._data.get(field_name, default)


class BaseDataValidator:
    """Base class for data validation"""

    @staticmethod
    def validate_product_code(product_code: str, allowed_codes: list[str]) -> bool:
        """Validate product code"""
        return product_code in allowed_codes

    @staticmethod
    def validate_decimal_precision(
        value: Union[str, float, Decimal], max_precision: int = 30
    ) -> bool:
        """Validate Decimal precision"""
        try:
            decimal_value = Decimal(str(value))
            # Check number of decimal places
            _, _, exponent = decimal_value.as_tuple()
            # Return False if exponent is not int (special values)
            if not isinstance(exponent, int):
                return False
            if exponent < -max_precision:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_timestamp_format(timestamp: str) -> bool:
        """Validate timestamp format"""
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return True
        except ValueError:
            return False
