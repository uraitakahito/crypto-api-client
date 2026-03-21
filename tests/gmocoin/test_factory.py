"""Tests for GMO Coin API client factory"""

import httpx
from pydantic import SecretStr
from yarl import URL

from crypto_api_client.gmocoin.gmocoin_api_client_factory import (
    GmoCoinApiClientFactory,
)


class TestGmoCoinApiClientFactory:
    """Tests for GmoCoinApiClientFactory"""

    def test_factory_initialization(self) -> None:
        """Verify that the factory is correctly initialized"""
        factory = GmoCoinApiClientFactory()

        assert factory is not None
        assert factory._api_config is not None

    def test_default_config_base_url(self) -> None:
        """Verify base URL in default configuration"""
        factory = GmoCoinApiClientFactory()

        assert factory._api_config["base_url"] == URL("https://api.coin.z.com")

    def test_default_config_stub_path(self) -> None:
        """Verify stub path in default configuration"""
        factory = GmoCoinApiClientFactory()

        assert factory._api_config["relative_stub_path"] == URL("public/v1")

    def test_default_config_contains_all_paths(self) -> None:
        """Verify all required API paths are in configuration"""
        factory = GmoCoinApiClientFactory()
        config = factory._api_config

        assert "relative_orderbook_identifier_path" in config
        assert config["relative_orderbook_identifier_path"] == URL("orderbooks")
        assert "relative_ticker_identifier_path" in config
        assert config["relative_ticker_identifier_path"] == URL("ticker")

    def test_get_default_config(self) -> None:
        """Verify default configuration can be retrieved"""
        factory = GmoCoinApiClientFactory()
        config = factory.get_default_config()

        assert config["base_url"] == URL("https://api.coin.z.com")
        assert config["relative_stub_path"] == URL("public/v1")

    def test_config_immutability(self) -> None:
        """Verify get_default_config returns different dict instances"""
        factory = GmoCoinApiClientFactory()
        config1 = factory.get_default_config()
        config2 = factory.get_default_config()

        assert config1 is not config2
        assert config1 == config2

    async def test_create_with_credentials(self) -> None:
        """Create client with credentials"""
        factory = GmoCoinApiClientFactory()

        async with httpx.AsyncClient() as http_client:
            api_key = SecretStr("test_api_key")
            api_secret = SecretStr("test_api_secret")

            client = factory.create(
                api_key=api_key,
                api_secret=api_secret,
                http_client=http_client,
                callbacks=None,
                request_config={"timeout": 30.0},
            )

            assert client._api_key == api_key
            assert client._api_secret == api_secret

    async def test_create_preserves_http_client(self) -> None:
        """Verify HTTP client is correctly passed"""
        factory = GmoCoinApiClientFactory()

        async with httpx.AsyncClient() as http_client:
            client = factory.create(
                api_key=SecretStr("dummy_api_key"),
                api_secret=SecretStr("dummy_api_secret"),
                http_client=http_client,
                callbacks=None,
                request_config={"timeout": 30.0},
            )

            assert client._http_client is http_client
