"""Common fixtures for the entire project.

This file defines common fixtures used throughout the project.
Provides test data generation using the Factory Pattern.
"""

from typing import Any, Callable

import pytest
import redis
from yarl import URL

from tests.common.test_data_factory.bitbank_factory import BitbankDataFactory
from tests.common.test_data_factory.bitflyer_factory import BitFlyerDataFactory

# Factory Pattern imports
from tests.common.test_data_factory.common_factory import CommonDataFactory
from tests.common.test_data_factory.signature_factory import (
    BitbankSignatureBuilder,
    BitFlyerSignatureBuilder,
)
from tests.common.test_data_factory.validation_factory import ValidationDataFactory
from tests.redis_test_factory import create_test_redis_client


# Factory fixtures
@pytest.fixture
def common_factory() -> CommonDataFactory:
    """Common data factory."""
    return CommonDataFactory()


@pytest.fixture
def bitflyer_factory() -> BitFlyerDataFactory:
    """bitFlyer data factory."""
    return BitFlyerDataFactory()


@pytest.fixture
def bitbank_factory() -> BitbankDataFactory:
    """bitbank data factory."""
    return BitbankDataFactory()


@pytest.fixture
def validation_factory() -> ValidationDataFactory:
    """Validation data factory."""
    return ValidationDataFactory()


@pytest.fixture
def bitflyer_signature_builder() -> BitFlyerSignatureBuilder:
    """Builder for bitFlyer signature."""
    return BitFlyerSignatureBuilder()


@pytest.fixture
def bitbank_signature_builder() -> BitbankSignatureBuilder:
    """Builder for bitbank signature."""
    return BitbankSignatureBuilder()


# Common fixtures
@pytest.fixture(scope="session")
def long_input_data() -> dict[str, Any]:
    """Cache long input data at session scope.

    Shared across the session to reduce the cost of generating large datasets.
    """
    return {
        "secret": "a" * 1000,
        "message": "b" * 10000,
        "expected_length": 11000,  # Total character count
    }


@pytest.fixture
def signature_test_params() -> dict[str, tuple[str, str]]:
    """Standard parameter set for signature testing.

    Provides commonly used parameters for signature testing.
    """
    return {
        "empty": ("", ""),
        "normal": ("secret", "message"),
        "special": ("secret-key", "test-message"),
        "spaces": ("secret key", "test message"),
    }


@pytest.fixture
def sample_api_credentials(common_factory: CommonDataFactory) -> dict[str, str]:
    """API credentials for testing.

    Provides dummy values for testing, not actual API keys.
    """
    return common_factory.create_api_credentials()


@pytest.fixture
def sample_timestamps() -> dict[str, str | int]:
    """Sample timestamps in each exchange format."""
    return {
        "bitflyer": "2025-01-01 00:00:00.000000",
        "bitbank": "1751156562472",
        "iso": "2025-01-01T00:00:00.000000Z",
        "unix": 1751156562,
    }


@pytest.fixture
def url_builder() -> Callable[[str, str, dict[str, Any] | None], URL]:
    """Helper factory for URL construction."""

    def _build_url(
        base: str, path: str = "", params: dict[str, Any] | None = None
    ) -> URL:
        """Build URL.

        :param base: Base URL
        :param path: Path part
        :param params: Query parameters
        :return: Constructed URL
        """
        url = URL(base)
        if path:
            url = url / path
        if params:
            url = url % params
        return url

    return _build_url


# Redis client fixture
@pytest.fixture
def redis_client(request: Any) -> redis.Redis:  # type: ignore
    """Provide Redis client based on test marker.

    Markers:
    - @pytest.mark.unit: Uses AsyncMock (default)
    - @pytest.mark.integration: Uses fakeredis

    Why use a hybrid approach:
    - Unit tests require fast execution and complete control over error cases
    - Integration tests require verification of actual Redis behavior
    - Build a robust test suite by leveraging the benefits of both
    """
    use_fake = request.node.get_closest_marker("integration") is not None
    return create_test_redis_client(use_fake=use_fake)  # type: ignore[return-value]


# Common configuration for parameterized tests
def pytest_configure(config: Any) -> None:
    """Customize pytest configuration."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
