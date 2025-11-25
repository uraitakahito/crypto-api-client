"""Common data factory for shared test data across all exchanges."""

from decimal import Decimal
from typing import Any

from .base_factory import BaseTestDataFactory


class CommonDataFactory(BaseTestDataFactory):
    """Factory for common test data used across all exchanges."""

    # Product codes / Currency pairs
    BTC_JPY = "BTC_JPY"
    ETH_JPY = "ETH_JPY"
    FX_BTC_JPY = "FX_BTC_JPY"
    ETH_BTC = "ETH_BTC"

    # Common test values
    DEFAULT_TIMESTAMP = "2025-02-27T13:50:43.957"
    DEFAULT_TICK_ID = 243332856
    DEFAULT_TICK_ID_STR = "243332856"

    # Price data
    DEFAULT_BEST_BID = Decimal("12860000.0")
    DEFAULT_BEST_ASK = Decimal("12870464.0")
    DEFAULT_LTP = Decimal("12872459.0")
    DEFAULT_BEST_BID_SIZE = Decimal("0.1385912")
    DEFAULT_BEST_ASK_SIZE = Decimal("0.0106")
    DEFAULT_TOTAL_BID_DEPTH = Decimal("123.24202636")
    DEFAULT_TOTAL_ASK_DEPTH = Decimal("279.49970104")
    DEFAULT_VOLUME = Decimal("5691.9186518")
    DEFAULT_VOLUME_BY_PRODUCT = Decimal("2042.29972298")

    # Order data
    DEFAULT_ORDER_SIZE = Decimal("0.001")
    DEFAULT_ORDER_PRICE = Decimal("1000000")

    # Execution data
    DEFAULT_EXECUTION_ID_1 = 39287
    DEFAULT_EXECUTION_ID_2 = 39288
    DEFAULT_EXECUTION_PRICE_1 = Decimal("31690")
    DEFAULT_EXECUTION_PRICE_2 = Decimal("31700")
    DEFAULT_EXECUTION_SIZE_1 = Decimal("27.04")
    DEFAULT_EXECUTION_SIZE_2 = Decimal("0.01")

    def create_product_code(self) -> str:
        """Create a default product code."""
        return self.BTC_JPY

    def create_ticker_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create common ticker data structure."""
        return {
            "product_code": kwargs.get("product_code", self.BTC_JPY),
            "state": kwargs.get("state", "RUNNING"),
            "timestamp": kwargs.get("timestamp", self.DEFAULT_TIMESTAMP),
            "tick_id": kwargs.get("tick_id", self.DEFAULT_TICK_ID),
            "best_bid": kwargs.get("best_bid", float(self.DEFAULT_BEST_BID)),
            "best_ask": kwargs.get("best_ask", float(self.DEFAULT_BEST_ASK)),
            "best_bid_size": kwargs.get(
                "best_bid_size", float(self.DEFAULT_BEST_BID_SIZE)
            ),
            "best_ask_size": kwargs.get(
                "best_ask_size", float(self.DEFAULT_BEST_ASK_SIZE)
            ),
            "total_bid_depth": kwargs.get(
                "total_bid_depth", float(self.DEFAULT_TOTAL_BID_DEPTH)
            ),
            "total_ask_depth": kwargs.get(
                "total_ask_depth", float(self.DEFAULT_TOTAL_ASK_DEPTH)
            ),
            "market_bid_size": kwargs.get("market_bid_size", 0.0),
            "market_ask_size": kwargs.get("market_ask_size", 0.0),
            "ltp": kwargs.get("ltp", float(self.DEFAULT_LTP)),
            "volume": kwargs.get("volume", float(self.DEFAULT_VOLUME)),
            "volume_by_product": kwargs.get(
                "volume_by_product", float(self.DEFAULT_VOLUME_BY_PRODUCT)
            ),
        }

    def create_execution_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create common execution data structure."""
        return {
            "id": kwargs.get("id", self.DEFAULT_EXECUTION_ID_1),
            "side": kwargs.get("side", "BUY"),
            "price": kwargs.get("price", float(self.DEFAULT_EXECUTION_PRICE_1)),
            "size": kwargs.get("size", float(self.DEFAULT_EXECUTION_SIZE_1)),
            "exec_date": kwargs.get("exec_date", "2015-07-08T02:43:34.823"),
            "buy_child_order_acceptance_id": kwargs.get(
                "buy_child_order_acceptance_id", "JRF20150707-200203-452209"
            ),
            "sell_child_order_acceptance_id": kwargs.get(
                "sell_child_order_acceptance_id", "JRF20150708-024334-060234"
            ),
        }

    def create_config_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create API configuration data."""
        return {
            "api_key": kwargs.get("api_key", self.DEFAULT_API_KEY),
            "api_secret": kwargs.get("api_secret", self.DEFAULT_API_SECRET),
            "timeout": kwargs.get("timeout", 30),
            "retry_config": kwargs.get(
                "retry_config",
                {
                    "max_retries": 3,
                    "retry_delay": 1,
                },
            ),
        }

    def create_error_response_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create error response data structure."""
        return {
            "status": kwargs.get("status", -1),
            "error": {
                "code": kwargs.get("error_code", "ERR001"),
                "message": kwargs.get("error_message", "Invalid parameter"),
            },
        }

    def create_http_error_mapping(self) -> dict[int, dict[str, Any]]:
        """Create HTTP error status code mapping."""
        return {
            400: {"status_code": 400, "text": "Bad Request"},
            401: {"status_code": 401, "text": "Unauthorized"},
            403: {"status_code": 403, "text": "Forbidden"},
            404: {"status_code": 404, "text": "Not Found"},
            429: {"status_code": 429, "text": "Too Many Requests"},
            500: {"status_code": 500, "text": "Internal Server Error"},
        }

    def create_balance_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create generic balance/asset response structure."""
        return {
            "status": kwargs.get("status", 0),
            "data": {
                "assets": kwargs.get(
                    "assets",
                    [
                        {
                            "asset": "jpy",
                            "free_amount": "10000.0",
                            "amount_precision": 4,
                            "onhand_amount": "10000.0",
                            "locked_amount": "0.0",
                        },
                        {
                            "asset": "btc",
                            "free_amount": "0.5",
                            "amount_precision": 8,
                            "onhand_amount": "0.5",
                            "locked_amount": "0.0",
                        },
                    ],
                ),
            },
        }

    def create_order_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create generic order response structure."""
        return {
            "order_id": kwargs.get("order_id", "123456"),
            "pair": kwargs.get("pair", "btc_jpy"),
            "side": kwargs.get("side", "buy"),
            "type": kwargs.get("type", "limit"),
            "start_amount": kwargs.get("start_amount", "0.01"),
            "remaining_amount": kwargs.get("remaining_amount", "0.01"),
            "executed_amount": kwargs.get("executed_amount", "0.0"),
            "price": kwargs.get("price", "5000000"),
            "average_price": kwargs.get("average_price", "0"),
            "ordered_at": kwargs.get("ordered_at", 1234567890000),
            "status": kwargs.get("status", "UNFILLED"),
        }

    def create_sample_ticker_response(self, **kwargs: Any) -> dict[str, Any]:
        """Generic ticker response structure (fixture replacement)."""
        return {
            "status": kwargs.get("status", 0),
            "data": {
                "sell": kwargs.get("sell", "1000000"),
                "buy": kwargs.get("buy", "999000"),
                "high": kwargs.get("high", "1010000"),
                "low": kwargs.get("low", "990000"),
                "last": kwargs.get("last", "999500"),
                "vol": kwargs.get("vol", "1234.5678"),
                "timestamp": kwargs.get("timestamp", 1234567890),
            },
        }

    def create_sample_execution_data(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Generic execution/trade history structure (fixture replacement)."""
        executions = kwargs.get(
            "executions",
            [
                {
                    "id": 1,
                    "price": "5000000",
                    "size": "0.001",
                    "side": "BUY",
                    "exec_date": "2024-01-01T00:00:00",
                    "buy_child_order_acceptance_id": "JRF20240101-000001",
                    "sell_child_order_acceptance_id": "JRF20240101-000002",
                },
                {
                    "id": 2,
                    "price": "5001000",
                    "size": "0.002",
                    "side": "SELL",
                    "exec_date": "2024-01-01T00:01:00",
                    "buy_child_order_acceptance_id": "JRF20240101-000003",
                    "sell_child_order_acceptance_id": "JRF20240101-000004",
                },
            ],
        )
        return executions
