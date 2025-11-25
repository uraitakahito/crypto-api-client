"""Test Data Factory Package

This package provides Factory Pattern to streamline test data generation and reduce duplication.

Usage:
    from tests.common.test_data_factory import BitFlyerDataFactory, BitbankDataFactory

    # Generate bitFlyer ticker data
    ticker_data = BitFlyerDataFactory.ticker().with_product_code("BTC_JPY").build()

    # Generate bitbank asset data
    asset_data = BitbankDataFactory.asset().jpy_preset("100000.0").build()

    # Generate validation error cases
    error_cases = ValidationDataFactory.create_bitflyer_validation_errors()
"""

from .base import BaseTestDataBuilder, TestDataConfig
from .bitbank_factory import BitbankDataFactory
from .bitflyer_factory import BitFlyerDataFactory
from .validation_factory import ValidationDataConfig, ValidationDataFactory

__all__ = [
    # Base classes
    "BaseTestDataBuilder",
    "TestDataConfig",
    # Exchange-specific Factories
    "BitFlyerDataFactory",
    "BitbankDataFactory",
    # Validation Factory
    "ValidationDataFactory",
    "ValidationDataConfig",
]
