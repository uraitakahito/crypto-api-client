"""Tests for bitFlyer API client factory"""

import httpx
import pytest
from pydantic import SecretStr
from yarl import URL

from crypto_api_client.bitflyer.bitflyer_api_client_factory import (
    BitFlyerApiClientFactory,
)


class TestBitFlyerApiClientFactory:
    """Tests for BitFlyerApiClientFactory"""

    @pytest.fixture
    def factory(self):
        """Factory instance for testing"""
        return BitFlyerApiClientFactory()

    def test_factory_initialization(self, factory):
        """Verify that the factory is correctly initialized"""
        assert factory is not None
        assert factory._api_config is not None
        assert factory._api_config["base_url"] == URL("https://api.bitflyer.jp")
        assert factory._api_config["relative_stub_path"] == URL("v1")

    async def test_create_with_credentials(self, factory):
        """Create client with credentials"""
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

    async def test_create_with_dummy_credentials(self, factory):
        """Create client with dummy credentials (Public API only)"""
        async with httpx.AsyncClient() as http_client:
            client = factory.create(
                api_key=SecretStr("dummy_api_key"),
                api_secret=SecretStr("dummy_api_secret"),
                http_client=http_client,
                callbacks=None,
                request_config={"timeout": 30.0},
            )

            # Verify dummy values are set
            assert client._api_key == SecretStr("dummy_api_key")
            assert client._api_secret == SecretStr("dummy_api_secret")

    async def test_create_with_secretstr_credentials(self, factory):
        """Create client with SecretStr type credentials"""
        async with httpx.AsyncClient() as http_client:
            api_key = SecretStr("plain_api_key")
            api_secret = SecretStr("plain_api_secret")
            client = factory.create(
                api_key=api_key,
                api_secret=api_secret,
                http_client=http_client,
                callbacks=None,
                request_config={"timeout": 30.0},
            )

            # Verify SecretStr type
            assert isinstance(client._api_key, SecretStr)
            assert isinstance(client._api_secret, SecretStr)
            assert client._api_key.get_secret_value() == "plain_api_key"
            assert client._api_secret.get_secret_value() == "plain_api_secret"

    async def test_create_with_callbacks(self, factory):
        """Create client with callbacks"""
        async with httpx.AsyncClient() as http_client:
            from crypto_api_client.callbacks import AbstractRequestCallback

            # Create actual callback class
            class TestCallback(AbstractRequestCallback):
                async def before_request(self, url, headers, data):
                    pass

                async def after_request(self, response_data):
                    pass

            test_callback = TestCallback()
            callbacks = (test_callback,)

            client = factory.create(
                api_key=SecretStr("dummy_api_key"),
                api_secret=SecretStr("dummy_api_secret"),
                http_client=http_client,
                callbacks=callbacks,
                request_config={"timeout": 30.0},
            )

            # Verify callbacks are correctly processed
            assert "before_request" in client._callbacks
            assert "after_request" in client._callbacks

    async def test_create_preserves_http_client(self, factory):
        """Verify HTTP client is correctly passed"""
        async with httpx.AsyncClient() as http_client:
            client = factory.create(
                api_key=SecretStr("dummy_api_key"),
                api_secret=SecretStr("dummy_api_secret"),
                http_client=http_client,
                callbacks=None,
                request_config={"timeout": 30.0},
            )

            # Verify the same HTTP client instance is used
            assert client._http_client is http_client

    def test_api_config_contains_all_required_paths(self, factory):
        """Verify all required API paths are included in configuration"""
        config = factory._api_config

        # Public API paths
        assert "relative_board_identifier_path" in config
        assert "relative_executions_identifier_path" in config
        assert "relative_gethealth_identifier_path" in config
        assert "relative_markets_identifier_path" in config
        assert "relative_ticker_identifier_path" in config

        # Private API paths
        assert "relative_resource_identifier_path" in config
        assert "getbalance_action_name" in config
        assert "getchildorders_action_name" in config
        assert "gettradingcommission_action_name" in config
        assert "sendchildorder_action_name" in config
        assert "cancelchildorder_action_name" in config

    def test_get_default_config(self, factory):
        """Verify default configuration can be retrieved correctly"""
        config = factory.get_default_config()

        assert config["base_url"] == URL("https://api.bitflyer.jp")
        assert config["relative_stub_path"] == URL("v1")
        assert "relative_ticker_identifier_path" in config
        assert "sendchildorder_action_name" in config

    def test_config_immutability(self, factory):
        """Verify configuration is immutable (different dict instances returned)"""
        config1 = factory.get_default_config()
        config2 = factory.get_default_config()

        # Different dict instances are returned
        assert config1 is not config2
        # Content is the same
        assert config1 == config2
