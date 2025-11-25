"""Minimal factory smoke tests

Lightweight tests to verify that each factory method executes without exceptions.
"""

from .bitbank_factory import BitbankDataFactory
from .bitflyer_factory import BitFlyerDataFactory
from .validation_factory import ValidationDataFactory


class TestFactorySmokeTests:
    """Minimal tests to verify basic factory operations"""

    def test_bitflyer_factory_basic_operations(self) -> None:
        """Verify that BitFlyerDataFactory basic methods work"""
        # Ticker
        ticker_data = BitFlyerDataFactory.ticker().build()
        assert isinstance(ticker_data, dict)
        assert "product_code" in ticker_data

        # Execution
        execution_data = BitFlyerDataFactory.execution().build()
        assert isinstance(execution_data, dict)

        # Balance
        balance_data = BitFlyerDataFactory.balance().build()
        assert isinstance(balance_data, dict)

    def test_bitbank_factory_basic_operations(self) -> None:
        """Verify that BitbankDataFactory basic methods work"""
        # Ticker
        ticker_data = BitbankDataFactory.ticker().build()
        assert isinstance(ticker_data, dict)
        assert "success" in ticker_data
        assert "data" in ticker_data

        # Asset
        asset_data = BitbankDataFactory.asset().build()
        assert isinstance(asset_data, dict)

    def test_validation_factory_basic_operations(self) -> None:
        """Verify that ValidationDataFactory basic methods work"""
        # Test scenario
        scenario = ValidationDataFactory.test_scenario()

        # Enum names
        enum_data = scenario.bitflyer_enum_names().build()
        assert isinstance(enum_data, dict)
        assert "values" in enum_data

        # Product codes
        product_codes = scenario.valid_product_codes().build()
        assert isinstance(product_codes, dict)
        assert "values" in product_codes

    def test_factory_chaining_works(self) -> None:
        """Verify that factory method chaining works correctly"""
        # BitFlyer ticker with custom values
        ticker = (
            BitFlyerDataFactory.ticker()
            .with_product_code("ETH_JPY")
            .with_prices(ltp="250000", bid="249000", ask="251000")
            .build()
        )
        assert ticker["product_code"] == "ETH_JPY"
        assert str(ticker["ltp"]) == "250000"

        # Bitbank ticker with timestamp
        from datetime import datetime

        now = datetime.now()
        bitbank_ticker = BitbankDataFactory.ticker().with_timestamp(now).build()
        assert isinstance(bitbank_ticker["data"]["timestamp"], int)
