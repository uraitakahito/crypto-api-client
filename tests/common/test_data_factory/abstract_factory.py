"""Abstract factory base classes for test data generation."""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Protocol, runtime_checkable

from crypto_api_client.http.http_response_data import HttpResponseData


@runtime_checkable
class TestDataFactoryProtocol(Protocol):
    """Protocol defining the interface all test data factories must implement."""

    @abstractmethod
    def create_ticker_request(self, **kwargs: Any) -> Any:
        """Create a ticker request object."""
        ...

    @abstractmethod
    def create_ticker_response(self, **kwargs: Any) -> HttpResponseData:
        """Create a ticker response object."""
        ...

    @abstractmethod
    def create_balance_response(self, **kwargs: Any) -> HttpResponseData:
        """Create a balance/assets response object."""
        ...

    @abstractmethod
    def create_order_request(self, **kwargs: Any) -> Any:
        """Create an order request object."""
        ...

    @abstractmethod
    def create_order_response(self, **kwargs: Any) -> HttpResponseData:
        """Create an order response object."""
        ...

    @abstractmethod
    def create_execution_response(self, **kwargs: Any) -> HttpResponseData:
        """Create an execution/trade history response object."""
        ...

    @abstractmethod
    def create_error_response(
        self, status_code: int, **kwargs: Any
    ) -> HttpResponseData:
        """Create an error response object with specified status code."""
        ...


class ExchangeTestDataFactory(ABC):
    """Abstract base class for exchange-specific test data factories."""

    @abstractmethod
    def create_api_credentials(self) -> dict[str, str]:
        """Create API credentials for testing."""
        ...

    @abstractmethod
    def create_product_code(self) -> str:
        """Create a product code/currency pair."""
        ...

    @abstractmethod
    def create_price(
        self, min_price: Decimal | None = None, max_price: Decimal | None = None
    ) -> Decimal:
        """Create a price value within specified range."""
        ...

    @abstractmethod
    def create_size(
        self, min_size: Decimal | None = None, max_size: Decimal | None = None
    ) -> Decimal:
        """Create a size/quantity value within specified range."""
        ...


class BitFlyerTestDataFactoryProtocol(TestDataFactoryProtocol, Protocol):
    """Protocol for bitFlyer-specific test data factory methods."""

    @abstractmethod
    def create_ticker_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create bitFlyer ticker data."""
        ...

    @abstractmethod
    def create_balance_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create bitFlyer balance data."""
        ...

    @abstractmethod
    def create_execution_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create bitFlyer execution data."""
        ...

    @abstractmethod
    def create_child_order_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create bitFlyer child order data."""
        ...


class BitbankTestDataFactoryProtocol(TestDataFactoryProtocol, Protocol):
    """Protocol for bitbank-specific test data factory methods."""

    @abstractmethod
    def create_ticker_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create bitbank ticker data."""
        ...

    @abstractmethod
    def create_asset_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create bitbank asset data."""
        ...

    @abstractmethod
    def create_order_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create bitbank order data."""
        ...

    @abstractmethod
    def create_trade_data(self, **kwargs: Any) -> dict[str, Any]:
        """Create bitbank trade data."""
        ...
