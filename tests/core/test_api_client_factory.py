"""Tests for API client factory base class."""

from typing import Any
from unittest.mock import Mock

import httpx
import pytest
from pydantic import SecretStr

from crypto_api_client._base import ApiClient
from crypto_api_client.core.api_client_factory import ApiClientFactoryBase


class MockApiClient(ApiClient):
    """Mock API client for testing."""

    pass


class ConcreteApiClientFactory(ApiClientFactoryBase[MockApiClient]):
    """Concrete factory implementation for testing."""

    def __init__(self):
        self.create_called = False
        self._api_config = {"test": "config"}

    def get_default_config(self) -> dict[str, Any]:
        """Get default API configuration."""
        return self._api_config

    def create(
        self,
        *,
        api_key: SecretStr | str | None,
        api_secret: SecretStr | str | None,
        http_client: httpx.AsyncClient,
        callbacks: Any,
        request_config: dict[str, Any],
    ) -> MockApiClient:
        """Create API client."""
        self.create_called = True
        return Mock(spec=MockApiClient)


class TestApiClientFactoryBase:
    """Tests for ApiClientFactoryBase."""

    def test_abstract_methods_defined(self):
        """Verify abstract methods are defined."""
        # Abstract base class cannot be instantiated directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ApiClientFactoryBase()  # type: ignore[abstract]

    def test_concrete_factory_implementation(self):
        """Verify concrete factory can be implemented correctly."""
        factory = ConcreteApiClientFactory()
        assert factory is not None
        assert not factory.create_called

    async def test_create_method_called(self):
        """Verify create method is called correctly."""
        factory = ConcreteApiClientFactory()

        async with httpx.AsyncClient() as http_client:
            client = factory.create(
                api_key=SecretStr("test_key"),
                api_secret=SecretStr("test_secret"),
                http_client=http_client,
                callbacks=None,
                request_config={"timeout": 30.0},
            )

            assert factory.create_called
            assert client is not None

    def test_generic_type_hint(self):
        """Verify generic type hints are defined correctly."""
        # Verify type hints exist
        assert hasattr(ApiClientFactoryBase, "__orig_bases__")

        # Verify ConcreteApiClientFactory can be instantiated correctly
        # (Indirectly confirms type checker works properly)
        _ = ConcreteApiClientFactory()
        # Type information is erased at runtime, so full verification only through static type checking
