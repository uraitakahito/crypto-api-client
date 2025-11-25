"""bitFlyer Test Data Factory

Factory classes for generating bitFlyer exchange test data.
Generates test data compliant with official API specifications.

API References:
- HTTP API: https://lightning.bitflyer.com/docs?lang=ja
- WebSocket API: https://bf-lightning-api.readme.io/docs/endpoint-json-rpc
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Union

from .base import BaseDataValidator, BaseTestDataBuilder, TestDataConfig
from .base_factory import BaseTestDataFactory


class BitFlyerDataValidator(BaseDataValidator):
    """bitFlyer-specific data validation"""

    VALID_PRODUCT_CODES = ["BTC_JPY", "ETH_JPY", "ETH_BTC", "BCH_BTC", "FX_BTC_JPY"]
    VALID_STATES = [
        "RUNNING",
        "CLOSED",
        "STARTING",
        "PREOPEN",
        "CIRCUIT_BREAK",
        "AWAITING_SQ",
        "MATURED",
    ]
    VALID_SIDES = ["BUY", "SELL"]
    VALID_ORDER_TYPES = ["MARKET", "LIMIT"]
    VALID_ORDER_STATES = ["ACTIVE", "COMPLETED", "CANCELED", "EXPIRED", "REJECTED"]

    # Common test data constants
    DEFAULT_PRODUCT_CODE = "BTC_JPY"
    DEFAULT_SIDE = "BUY"
    DEFAULT_ORDER_TYPE = "LIMIT"

    @classmethod
    def validate_bitflyer_product_code(cls, product_code: str) -> bool:
        """Validate bitFlyer-specific product code"""
        return cls.validate_product_code(product_code, cls.VALID_PRODUCT_CODES)


class BitFlyerTickerBuilder(BaseTestDataBuilder):
    """Builder specialized for bitFlyer ticker data

    Generates ticker data compliant with official API specifications.
    Reference: https://lightning.bitflyer.com/docs?lang=ja#ticker
    """

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {
            "product_code": self.config.default_product_code,
            "state": "RUNNING",
            "timestamp": self.config.default_timestamp,
            "tick_id": "243332856",
            "best_bid": Decimal("12860000.0"),
            "best_ask": Decimal("12870464.0"),
            "best_bid_size": Decimal("0.1385912"),
            "best_ask_size": Decimal("0.0106"),
            "total_bid_depth": Decimal("123.24202636"),
            "total_ask_depth": Decimal("279.49970104"),
            "market_bid_size": Decimal("0.0"),
            "market_ask_size": Decimal("0.0"),
            "ltp": Decimal("12872459.0"),
            "volume": Decimal("5691.9186518"),
            "volume_by_product": Decimal("2042.29972298"),
        }

    def with_product_code(self, code: str) -> "BitFlyerTickerBuilder":
        """Set product code"""
        if self.config.use_api_spec_validation:
            if not BitFlyerDataValidator.validate_bitflyer_product_code(code):
                raise ValueError(f"Invalid product code: {code}")
        return self._set_field("product_code", code)

    def with_state(self, state: str) -> "BitFlyerTickerBuilder":
        """Set market state"""
        if self.config.use_api_spec_validation:
            if state not in BitFlyerDataValidator.VALID_STATES:
                raise ValueError(f"Invalid state: {state}")
        return self._set_field("state", state)

    def with_prices(
        self,
        ltp: Union[str, int, float, Decimal],
        bid: Union[str, int, float, Decimal],
        ask: Union[str, int, float, Decimal],
    ) -> "BitFlyerTickerBuilder":
        """Set price information in bulk"""
        return (
            self._set_field("ltp", Decimal(str(ltp)))
            ._set_field("best_bid", Decimal(str(bid)))
            ._set_field("best_ask", Decimal(str(ask)))
        )

    def with_volume(
        self, volume: Union[str, float, Decimal]
    ) -> "BitFlyerTickerBuilder":
        """Set volume"""
        return self._set_field("volume", Decimal(str(volume)))

    def with_timestamp(
        self, timestamp: Union[str, datetime]
    ) -> "BitFlyerTickerBuilder":
        """Set timestamp"""
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.isoformat()
        else:
            timestamp_str = timestamp

        if self.config.use_api_spec_validation:
            if not BitFlyerDataValidator.validate_timestamp_format(timestamp_str):
                raise ValueError(f"Invalid timestamp format: {timestamp_str}")

        return self._set_field("timestamp", timestamp_str)

    def with_tick_id(self, tick_id: Union[str, int]) -> "BitFlyerTickerBuilder":
        """Set tick ID"""
        return self._set_field("tick_id", str(tick_id))

    def with_sizes(
        self, bid_size: Union[str, float, Decimal], ask_size: Union[str, float, Decimal]
    ) -> "BitFlyerTickerBuilder":
        """Set order book sizes"""
        return self._set_field("best_bid_size", Decimal(str(bid_size)))._set_field(
            "best_ask_size", Decimal(str(ask_size))
        )

    def with_depth(
        self,
        bid_depth: Union[str, float, Decimal],
        ask_depth: Union[str, float, Decimal],
    ) -> "BitFlyerTickerBuilder":
        """Set order book depth"""
        return self._set_field("total_bid_depth", Decimal(str(bid_depth)))._set_field(
            "total_ask_depth", Decimal(str(ask_depth))
        )

    def minimal(self) -> "BitFlyerTickerBuilder":
        """Set only minimal fields"""
        minimal_data = {
            "product_code": "BTC_JPY",
            "state": "RUNNING",
            "timestamp": "2025-01-10T00:00:00.000",
            "tick_id": "1",
            "best_bid": Decimal("1000000.0"),
            "best_ask": Decimal("1000001.0"),
            "best_bid_size": Decimal("0.01"),
            "best_ask_size": Decimal("0.01"),
            "total_bid_depth": Decimal("1.0"),
            "total_ask_depth": Decimal("1.0"),
            "market_bid_size": Decimal("0.0"),
            "market_ask_size": Decimal("0.0"),
            "ltp": Decimal("1000000.0"),
            "volume": Decimal("1.0"),
            "volume_by_product": Decimal("1.0"),
        }
        self._data.update(minimal_data)
        return self

    def invalid(self, field: str, value: Any = None) -> "BitFlyerTickerBuilder":
        """Set invalid data (for error testing)"""
        if field == "product_code":
            return self._set_field(field, value or "INVALID_CODE")
        elif field == "timestamp":
            return self._set_field(field, value or "invalid-timestamp")
        elif field == "tick_id":
            return self._set_field(field, value or None)
        else:
            return self._set_field(field, value)

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class BitFlyerBalanceBuilder(BaseTestDataBuilder):
    """Builder specialized for bitFlyer balance data

    Reference: https://lightning.bitflyer.com/docs?lang=ja#get-account-asset-balance
    """

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {
            "currency_code": "BTC",
            "amount": Decimal("0.12345678"),
            "available": Decimal("0.12345678"),
        }

    def with_currency(self, currency_code: str) -> "BitFlyerBalanceBuilder":
        """Set currency code"""
        return self._set_field("currency_code", currency_code)

    def with_amounts(
        self,
        amount: Union[str, float, Decimal],
        available: Union[str, float, Decimal | None] = None,
    ) -> "BitFlyerBalanceBuilder":
        """Set balance"""
        result = self._set_field("amount", Decimal(str(amount)))
        if available is not None:
            result = result._set_field("available", Decimal(str(available)))
        return result

    def jpy(
        self, amount: Union[str, float, Decimal] = "100000.0"
    ) -> "BitFlyerBalanceBuilder":
        """JPY balance preset"""
        return self.with_currency("JPY").with_amounts(amount, amount)

    def btc(
        self, amount: Union[str, float, Decimal] = "0.12345678"
    ) -> "BitFlyerBalanceBuilder":
        """BTC balance preset"""
        return self.with_currency("BTC").with_amounts(amount, amount)

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class BitFlyerExecutionBuilder(BaseTestDataBuilder):
    """Builder specialized for bitFlyer execution data

    Reference: https://lightning.bitflyer.com/docs?lang=ja#list-executions
    """

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {
            "id": 123456789,
            "side": "BUY",
            "price": Decimal("5000000.0"),
            "size": Decimal("0.001"),
            "exec_date": "2024-01-01T00:00:00.000",
            "buy_child_order_acceptance_id": "JRF20240101-000001",
            "sell_child_order_acceptance_id": "JRF20240101-000002",
        }

    def with_id(self, execution_id: int) -> "BitFlyerExecutionBuilder":
        """Set execution ID"""
        return self._set_field("id", execution_id)

    def with_side(self, side: str) -> "BitFlyerExecutionBuilder":
        """Set side (buy/sell)"""
        if self.config.use_api_spec_validation:
            if side not in BitFlyerDataValidator.VALID_SIDES:
                raise ValueError(f"Invalid side: {side}")
        return self._set_field("side", side)

    def with_execution(
        self, price: Union[str, float, Decimal], size: Union[str, float, Decimal]
    ) -> "BitFlyerExecutionBuilder":
        """Set execution price and size"""
        return self._set_field("price", Decimal(str(price)))._set_field(
            "size", Decimal(str(size))
        )

    def with_exec_date(
        self, exec_date: Union[str, datetime]
    ) -> "BitFlyerExecutionBuilder":
        """Set execution date"""
        if isinstance(exec_date, datetime):
            exec_date = exec_date.isoformat()
        return self._set_field("exec_date", exec_date)

    def with_order_ids(self, buy_id: str, sell_id: str) -> "BitFlyerExecutionBuilder":
        """Set order IDs"""
        return self._set_field("buy_child_order_acceptance_id", buy_id)._set_field(
            "sell_child_order_acceptance_id", sell_id
        )

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class BitFlyerChildOrderBuilder(BaseTestDataBuilder):
    """Builder specialized for bitFlyer child order data

    Reference: https://lightning.bitflyer.com/docs?lang=ja#list-orders
    """

    def _initialize_defaults(self) -> None:
        """Initialize default values"""
        self._data = {
            "id": 138398,
            "child_order_id": "JOR20250310-214142-959206",
            "product_code": "BTC_JPY",
            "side": "BUY",
            "child_order_type": "LIMIT",
            "price": 12901973.0,
            "average_price": 0.0,
            "size": 0.001,
            "child_order_state": "ACTIVE",
            "time_in_force": "GTC",
            "expire_date": "2025-04-09T14:41:42",
            "child_order_date": "2025-03-10T14:41:42",
            "child_order_acceptance_id": "JRF20250310-214142-437003",
            "outstanding_size": 0.001,
            "cancel_size": 0.0,
            "executed_size": 0.0,
            "total_commission": 0.0,
        }

    def with_product_code(self, product_code: str) -> "BitFlyerChildOrderBuilder":
        """Set product code"""
        if self.config.use_api_spec_validation:
            if not BitFlyerDataValidator.validate_bitflyer_product_code(product_code):
                raise ValueError(f"Invalid product_code: {product_code}")
        return self._set_field("product_code", product_code)

    def with_side(self, side: str) -> "BitFlyerChildOrderBuilder":
        """Set side (buy/sell)"""
        if self.config.use_api_spec_validation:
            if side not in BitFlyerDataValidator.VALID_SIDES:
                raise ValueError(f"Invalid side: {side}")
        return self._set_field("side", side)

    def with_order_type(self, order_type: str) -> "BitFlyerChildOrderBuilder":
        """Set order type"""
        if self.config.use_api_spec_validation:
            if order_type not in BitFlyerDataValidator.VALID_ORDER_TYPES:
                raise ValueError(f"Invalid order_type: {order_type}")
        return self._set_field("child_order_type", order_type)

    def with_price(
        self, price: Union[str, int, float, Decimal]
    ) -> "BitFlyerChildOrderBuilder":
        """Set price"""
        return self._set_field("price", float(price))

    def with_size(
        self, size: Union[str, float, Decimal]
    ) -> "BitFlyerChildOrderBuilder":
        """Set size"""
        return self._set_field("size", float(size))

    def with_state(self, state: str) -> "BitFlyerChildOrderBuilder":
        """Set order state"""
        if self.config.use_api_spec_validation:
            if state not in BitFlyerDataValidator.VALID_ORDER_STATES:
                raise ValueError(f"Invalid state: {state}")
        return self._set_field("child_order_state", state)

    def with_id(self, order_id: int) -> "BitFlyerChildOrderBuilder":
        """Set order ID"""
        return self._set_field("id", order_id)

    def with_child_order_id(self, child_order_id: str) -> "BitFlyerChildOrderBuilder":
        """Set child order ID"""
        return self._set_field("child_order_id", child_order_id)

    def with_time_in_force(self, time_in_force: str) -> "BitFlyerChildOrderBuilder":
        """Set time in force"""
        return self._set_field("time_in_force", time_in_force)

    def active_buy_order(self) -> "BitFlyerChildOrderBuilder":
        """Active buy order preset"""
        return self.with_side("BUY").with_state("ACTIVE").with_order_type("LIMIT")

    def completed_sell_order(self) -> "BitFlyerChildOrderBuilder":
        """Completed sell order preset"""
        return (
            self.with_side("SELL")
            .with_state("COMPLETED")
            .with_order_type("LIMIT")
            ._set_field("executed_size", self._get_field("size", 0.001))
            ._set_field("outstanding_size", 0.0)
        )

    def build(self) -> Dict[str, Any]:
        """Build the final data"""
        return self._data.copy()


class BitFlyerDataFactory(BaseTestDataFactory):
    """Factory class for bitFlyer test data

    Provides entry points for various builders.
    """

    @staticmethod
    def ticker(config: TestDataConfig | None = None) -> BitFlyerTickerBuilder:
        """Get ticker builder"""
        return BitFlyerTickerBuilder(config)

    @staticmethod
    def balance(config: TestDataConfig | None = None) -> BitFlyerBalanceBuilder:
        """Get balance builder"""
        return BitFlyerBalanceBuilder(config)

    @staticmethod
    def execution(config: TestDataConfig | None = None) -> BitFlyerExecutionBuilder:
        """Get execution builder"""
        return BitFlyerExecutionBuilder(config)

    @staticmethod
    def child_order(
        config: TestDataConfig | None = None,
    ) -> "BitFlyerChildOrderBuilder":
        """Get child order builder"""
        return BitFlyerChildOrderBuilder(config)

    @staticmethod
    def common_params(
        product_code: str | None = None, side: str | None = None
    ) -> Dict[str, str]:
        """Get common parameters (for testing)"""
        return {
            "product_code": product_code or BitFlyerDataValidator.DEFAULT_PRODUCT_CODE,
            "side": side or BitFlyerDataValidator.DEFAULT_SIDE,
        }

    def create_product_code(self) -> str:
        """Create a product code."""
        return BitFlyerDataValidator.DEFAULT_PRODUCT_CODE

    def create_ticker_request(self, **kwargs: Any) -> Any:
        """Create a ticker request object."""
        # This would typically return a BitFlyerTickerRequest object
        # For now, return a dict with product_code
        return {"product_code": kwargs.get("product_code", self.create_product_code())}

    def create_ticker_response(self, **kwargs: Any) -> Any:
        """Create a ticker response object."""
        ticker_data = self.ticker().build()
        return self.create_success_response(ticker_data)

    def create_balance_response(self, **kwargs: Any) -> Any:
        """Create a balance response object."""
        balance_data = [self.balance().build()]
        return self.create_success_response(balance_data)

    def create_order_request(self, **kwargs: Any) -> Any:
        """Create an order request object."""
        # Return basic order request data
        return {
            "product_code": kwargs.get("product_code", self.create_product_code()),
            "child_order_type": kwargs.get("child_order_type", "LIMIT"),
            "side": kwargs.get("side", BitFlyerDataValidator.DEFAULT_SIDE),
            "size": kwargs.get("size", "0.001"),
            "price": kwargs.get("price", 1000000),
        }

    def create_order_response(self, **kwargs: Any) -> Any:
        """Create an order response object."""
        order_data = {
            "child_order_acceptance_id": kwargs.get("order_id", "JRF20240101-000001")
        }
        return self.create_success_response(order_data)

    def create_execution_response(self, **kwargs: Any) -> Any:
        """Create an execution response object."""
        execution_data = [self.execution().build()]
        return self.create_success_response(execution_data)
