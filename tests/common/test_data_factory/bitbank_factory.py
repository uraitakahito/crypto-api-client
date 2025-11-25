"""bitbank Test Data Factory

Factory classes for generating bitbank exchange test data.
Generates test data compliant with official API specifications.

API References:
- Public API: https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-api_JP.md
- Private API: https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api_JP.md
"""

import time
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Union

from .base import BaseDataValidator, BaseTestDataBuilder, TestDataConfig


class BitbankDataValidator(BaseDataValidator):
    """bitbank-specific data validation"""

    VALID_SYMBOLS = [
        "jpy",
        "btc",
        "eth",
        "xrp",
        "ltc",
        "bcc",
        "mona",
        "xlm",
        "qtum",
        "bat",
        "omg",
        "xym",
    ]
    VALID_PAIRS = [
        "btc_jpy",
        "eth_jpy",
        "xrp_jpy",
        "ltc_jpy",
        "bcc_jpy",
        "mona_jpy",
        "xlm_jpy",
        "qtum_jpy",
        "bat_jpy",
        "omg_jpy",
        "xym_jpy",
        "eth_btc",
        "ltc_btc",
        "xrp_btc",
        "bcc_btc",
        "mona_btc",
        "xlm_btc",
        "qtum_btc",
        "bat_btc",
        "omg_btc",
        "xym_btc",
    ]
    VALID_SIDE_VALUES = ["buy", "sell"]
    VALID_ORDER_TYPES = ["limit", "market"]

    # Common test timestamps (in milliseconds)
    COMMON_TIMESTAMPS = {
        "2025_01_01": Decimal(1735689600000),  # 2025-01-01 00:00:00 UTC
        "2024_01_01": Decimal(1704067200000),  # 2024-01-01 00:00:00 UTC
        "2023_01_01": Decimal(1672531200000),  # 2023-01-01 00:00:00 UTC
    }

    @classmethod
    def validate_bitbank_symbol(cls, symbol: str) -> bool:
        """Validate bitbank-specific symbol"""
        return symbol.lower() in cls.VALID_SYMBOLS

    @classmethod
    def validate_bitbank_pair(cls, pair: str) -> bool:
        """Validate bitbank-specific currency pair"""
        return pair.lower() in cls.VALID_PAIRS

    @classmethod
    def validate_unix_timestamp_ms(cls, timestamp: Union[int, float]) -> bool:
        """Validate Unix timestamp in milliseconds"""
        try:
            # Check if timestamp is within valid range (2020-2030)
            min_timestamp = 1577836800000  # 2020-01-01 00:00:00 UTC (ms)
            max_timestamp = 1893456000000  # 2030-01-01 00:00:00 UTC (ms)
            return min_timestamp <= int(timestamp) <= max_timestamp
        except (ValueError, TypeError):
            return False


class BitbankTickerBuilder(BaseTestDataBuilder):
    """Builder specialized for bitbank ticker data

    Generates ticker data compliant with official API specifications.
    Reference: https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-api_JP.md#ticker
    """

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        # Current time as millisecond timestamp
        current_timestamp = int(time.time() * 1000)

        self._data = {
            "success": 1,
            "data": {
                "sell": "15350001",
                "buy": "15350000",
                "open": "15572550",
                "high": "15836477",
                "low": "15271389",
                "last": "15350001",
                "vol": "273.5234",
                "timestamp": current_timestamp,
            },
        }

    def with_success_status(self, success: int) -> "BitbankTickerBuilder":
        """Set success status (normally 1, 0 for error testing)"""
        return self._set_field("success", success)

    def with_prices(
        self,
        sell: Union[str, int, float, Decimal],
        buy: Union[str, int, float, Decimal],
        last: Union[str, int, float, Decimal],
        high: Union[str, int, float, Decimal | None] = None,
        low: Union[str, int, float, Decimal | None] = None,
        open_price: Union[str, int, float, Decimal | None] = None,
    ) -> "BitbankTickerBuilder":
        """Set price information in bulk"""
        data = self._get_field("data", {})
        data.update(
            {
                "sell": str(sell),
                "buy": str(buy),
                "last": str(last),
            }
        )

        if high is not None:
            data["high"] = str(high)
        if low is not None:
            data["low"] = str(low)
        if open_price is not None:
            data["open"] = str(open_price)

        return self._set_field("data", data)

    def with_volume(self, volume: Union[str, float, Decimal]) -> "BitbankTickerBuilder":
        """Set volume"""
        data = self._get_field("data", {})
        data["vol"] = str(volume)
        return self._set_field("data", data)

    def with_timestamp(
        self, timestamp: Union[int, float, datetime]
    ) -> "BitbankTickerBuilder":
        """Set timestamp"""
        if isinstance(timestamp, datetime):
            # Convert datetime to millisecond Unix timestamp
            timestamp_ms = int(timestamp.timestamp() * 1000)
        else:
            timestamp_ms = int(timestamp)

        if self.config.use_api_spec_validation:
            if not BitbankDataValidator.validate_unix_timestamp_ms(timestamp_ms):
                raise ValueError(f"Invalid timestamp: {timestamp_ms}")

        data = self._get_field("data", {})
        data["timestamp"] = timestamp_ms
        return self._set_field("data", data)

    def minimal(self) -> "BitbankTickerBuilder":
        """Set only minimal fields"""
        minimal_data = {
            "success": 1,
            "data": {
                "sell": "1000000",
                "buy": "999999",
                "open": "1000000",
                "high": "1000000",
                "low": "999999",
                "last": "1000000",
                "vol": "1.0",
                "timestamp": 1640995200000,  # 2022-01-01 00:00:00 UTC
            },
        }
        self._data.update(minimal_data)
        return self

    def error_response(self, error_code: str = "20003") -> "BitbankTickerBuilder":
        """Generate error response"""
        error_data = {"success": 0, "data": {"code": error_code}}
        self._data.update(error_data)
        return self

    def btc_jpy_preset(self, price_level: str = "standard") -> "BitbankTickerBuilder":
        """BTC/JPY preset"""
        price_configs = {
            "low": ("5000000", "4999999", "5000000", "5100000", "4900000"),
            "standard": ("15350001", "15350000", "15350001", "15836477", "15271389"),
            "high": ("20000000", "19999999", "20000000", "20500000", "19500000"),
        }

        if price_level not in price_configs:
            raise ValueError(f"Invalid price_level: {price_level}")

        sell, buy, last, high, low = price_configs[price_level]
        return self.with_prices(sell=sell, buy=buy, last=last, high=high, low=low)

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class BitbankAssetBuilder(BaseTestDataBuilder):
    """Builder specialized for bitbank asset data

    Reference: https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api_JP.md#assets
    """

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {
            "success": 1,
            "data": {
                "assets": [
                    {
                        "asset": "jpy",
                        "amount_precision": 4,
                        "onhand_amount": "100000.0000",
                        "locked_amount": "0.0000",
                        "free_amount": "100000.0000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": {
                            "threshold": "30000.0000",
                            "under": "550.0000",
                            "over": "770.0000",
                        },
                    }
                ]
            },
        }

    def with_asset(
        self,
        asset: str,
        amount_precision: int = 8,
        onhand_amount: Union[str, float, Decimal] = "0.0",
        locked_amount: Union[str, float, Decimal] = "0.0",
        free_amount: Union[str, float, Decimal | None] = None,
        stop_deposit: bool = False,
        stop_withdrawal: bool = False,
    ) -> "BitbankAssetBuilder":
        """Set a single asset"""

        if self.config.use_api_spec_validation:
            if not BitbankDataValidator.validate_bitbank_symbol(asset):
                raise ValueError(f"Invalid asset symbol: {asset}")

        # If free_amount is not specified, calculate as onhand_amount - locked_amount
        if free_amount is None:
            onhand_decimal = Decimal(str(onhand_amount))
            locked_decimal = Decimal(str(locked_amount))
            free_amount = str(onhand_decimal - locked_decimal)

        # Format according to amount_precision
        format_str = f"{{:.{amount_precision}f}}"

        asset_data = {
            "asset": asset.lower(),
            "amount_precision": amount_precision,
            "onhand_amount": format_str.format(Decimal(str(onhand_amount))),
            "locked_amount": format_str.format(Decimal(str(locked_amount))),
            "free_amount": format_str.format(Decimal(str(free_amount))),
            "stop_deposit": stop_deposit,
            "stop_withdrawal": stop_withdrawal,
        }

        # Fee settings (only for fiat currency)
        if asset.lower() == "jpy":
            asset_data["withdrawal_fee"] = {  # type: ignore[assignment]
                "threshold": "30000.0000",
                "under": "550.0000",
                "over": "770.0000",
            }

        # Add to existing assets list
        data = self._get_field("data", {"assets": []})
        data["assets"] = [asset_data]  # Replace for single asset

        return self._set_field("data", data)

    def add_asset(self, **kwargs: Any) -> "BitbankAssetBuilder":
        """Add an asset to existing assets list"""
        # First set as single asset, then add to list
        temp_builder = BitbankAssetBuilder(self.config)
        temp_builder.with_asset(**kwargs)
        new_asset = temp_builder.build()["data"]["assets"][0]

        # Add to existing assets list
        data = self._get_field("data", {"assets": []})
        data["assets"].append(new_asset)

        return self._set_field("data", data)

    def jpy(
        self,
        onhand_amount: Union[str, float, Decimal] = "100000.0",
        locked_amount: Union[str, float, Decimal] = "0.0",
    ) -> "BitbankAssetBuilder":
        """JPY asset (convenience method)"""
        return self.with_asset(
            asset="jpy",
            amount_precision=4,
            onhand_amount=onhand_amount,
            locked_amount=locked_amount,
        )

    def btc(
        self,
        onhand_amount: Union[str, float, Decimal] = "0.50000000",
        locked_amount: Union[str, float, Decimal] = "0.10000000",
    ) -> "BitbankAssetBuilder":
        """BTC asset (convenience method)"""
        return self.with_asset(
            asset="btc",
            amount_precision=8,
            onhand_amount=onhand_amount,
            locked_amount=locked_amount,
        )

    def jpy_preset(
        self, amount: Union[str, float, Decimal] = "100000.0"
    ) -> "BitbankAssetBuilder":
        """JPY asset preset"""
        return self.with_asset(
            asset="jpy",
            amount_precision=4,
            onhand_amount=amount,
            locked_amount="0.0",
            free_amount=amount,
        )

    def btc_preset(
        self, amount: Union[str, float, Decimal] = "0.12345678"
    ) -> "BitbankAssetBuilder":
        """BTC asset preset"""
        return self.with_asset(
            asset="btc",
            amount_precision=8,
            onhand_amount=amount,
            locked_amount="0.0",
            free_amount=amount,
        )

    def multi_asset_preset(self) -> "BitbankAssetBuilder":
        """Multiple assets preset"""
        return (
            self.jpy_preset("500000.0")
            .add_asset(asset="btc", amount_precision=8, onhand_amount="1.23456789")
            .add_asset(asset="eth", amount_precision=8, onhand_amount="10.12345678")
        )

    def error_response(self, error_code: str = "20003") -> "BitbankAssetBuilder":
        """Generate error response"""
        error_data = {"success": 0, "data": {"code": error_code}}
        self._data.update(error_data)
        return self

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class BitbankErrorResponseBuilder(BaseTestDataBuilder):
    """Builder specialized for bitbank error responses"""

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {"success": 0, "data": {"code": "20003"}}

    def with_error_code(self, error_code: str) -> "BitbankErrorResponseBuilder":
        """Set error code"""
        data = self._get_field("data", {})
        data["code"] = error_code
        return self._set_field("data", data)

    def with_code(self, error_code: Union[str, int]) -> "BitbankErrorResponseBuilder":
        """Set error code (convenience method)"""
        return self.with_error_code(str(error_code))

    def with_message(self, message: str) -> "BitbankErrorResponseBuilder":
        """Set error message"""
        data = self._get_field("data", {})
        data["message"] = message
        return self._set_field("data", data)

    def rate_limit_error(self) -> "BitbankErrorResponseBuilder":
        """Rate limit error"""
        return self.with_error_code("20014")

    def invalid_parameter_error(self) -> "BitbankErrorResponseBuilder":
        """Invalid parameter error"""
        return self.with_error_code("20003")

    def unauthorized_error(self) -> "BitbankErrorResponseBuilder":
        """Authentication error"""
        return self.with_error_code("20004")

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class BitbankSuccessResponseBuilder(BaseTestDataBuilder):
    """Builder specialized for bitbank success responses"""

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {"success": 1, "data": {}}

    def with_data(self, data: Dict[str, Any]) -> "BitbankSuccessResponseBuilder":
        """Set data field"""
        return self._set_field("data", data)

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class BitbankAssetOnlyBuilder(BaseTestDataBuilder):
    """Builder specialized for bitbank single asset data (without response structure)"""

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {
            "asset": "jpy",
            "amount_precision": 4,
            "onhand_amount": "100000.0000",
            "locked_amount": "0.0000",
            "free_amount": "100000.0000",
            "stop_deposit": False,
            "stop_withdrawal": False,
            "withdrawal_fee": {
                "threshold": "30000.0000",
                "under": "550.0000",
                "over": "770.0000",
            },
        }

    def jpy(
        self,
        onhand_amount: Union[str, float, Decimal] = "100000.0",
        locked_amount: Union[str, float, Decimal] = "0.0",
    ) -> "BitbankAssetOnlyBuilder":
        """JPY asset (convenience method)"""
        free_amount = str(Decimal(str(onhand_amount)) - Decimal(str(locked_amount)))
        format_str = f"{{:.{4}f}}"

        self._data.update(
            {
                "asset": "jpy",
                "amount_precision": 4,
                "onhand_amount": format_str.format(Decimal(str(onhand_amount))),
                "locked_amount": format_str.format(Decimal(str(locked_amount))),
                "free_amount": format_str.format(Decimal(str(free_amount))),
                "stop_deposit": False,
                "stop_withdrawal": False,
                "withdrawal_fee": {
                    "threshold": "30000.0000",
                    "under": "550.0000",
                    "over": "770.0000",
                },
            }
        )
        return self

    def btc(
        self,
        onhand_amount: Union[str, float, Decimal] = "0.50000000",
        locked_amount: Union[str, float, Decimal] = "0.10000000",
    ) -> "BitbankAssetOnlyBuilder":
        """BTC asset (convenience method)"""
        free_amount = str(Decimal(str(onhand_amount)) - Decimal(str(locked_amount)))
        format_str = f"{{:.{8}f}}"

        self._data.update(
            {
                "asset": "btc",
                "amount_precision": 8,
                "onhand_amount": format_str.format(Decimal(str(onhand_amount))),
                "locked_amount": format_str.format(Decimal(str(locked_amount))),
                "free_amount": format_str.format(Decimal(str(free_amount))),
                "stop_deposit": False,
                "stop_withdrawal": False,
            }
        )
        # BTC does not have withdrawal_fee
        if "withdrawal_fee" in self._data:
            del self._data["withdrawal_fee"]
        return self

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class BitbankDataFactory:
    """Factory class for bitbank test data

    Provides entry points for various builders.
    """

    @staticmethod
    def ticker(config: TestDataConfig | None = None) -> BitbankTickerBuilder:
        """Get ticker builder"""
        return BitbankTickerBuilder(config)

    @staticmethod
    def asset(config: TestDataConfig | None = None) -> BitbankAssetBuilder:
        """Get asset builder"""
        return BitbankAssetBuilder(config)

    @staticmethod
    def error(config: TestDataConfig | None = None) -> BitbankErrorResponseBuilder:
        """Get error response builder"""
        return BitbankErrorResponseBuilder(config)

    @staticmethod
    def success_response(
        config: TestDataConfig | None = None,
    ) -> "BitbankSuccessResponseBuilder":
        """Get success response builder"""
        return BitbankSuccessResponseBuilder(config)

    @staticmethod
    def error_response(
        config: TestDataConfig | None = None,
    ) -> BitbankErrorResponseBuilder:
        """Get error response builder (convenience method)"""
        return BitbankErrorResponseBuilder(config)

    @staticmethod
    def asset_only(
        config: TestDataConfig | None = None,
    ) -> "BitbankAssetOnlyBuilder":
        """Get single asset builder (without response structure)"""
        return BitbankAssetOnlyBuilder(config)

    @staticmethod
    def common_timestamp(key: str = "2025_01_01") -> Decimal:
        """Get common test timestamp"""
        return BitbankDataValidator.COMMON_TIMESTAMPS.get(
            key, BitbankDataValidator.COMMON_TIMESTAMPS["2025_01_01"]
        )

    @staticmethod
    def datetime_test_data(timestamp_key: str = "2025_01_01") -> Dict[str, Any]:
        """Generate test data for datetime_converter"""
        return {
            "timestamp": BitbankDataFactory.common_timestamp(timestamp_key),
            "sell": "1000.123",
            "buy": "999.456789",
        }
