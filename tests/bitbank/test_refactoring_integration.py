"""bitbank refactoring integration tests

This test confirms that URL construction works correctly after action name refactoring.
"""

import pytest
from yarl import URL

from crypto_api_client.bitbank.bitbank_api_client_factory import (
    BitbankApiClientFactory,
)


class TestBitbankRefactoringIntegration:
    """Integration tests for action name refactoring"""

    @pytest.fixture
    def factory(self):
        """Factory instance for testing"""
        return BitbankApiClientFactory()

    def test_factory_config_has_all_new_keys(self, factory):
        """Verify all new configuration keys exist"""
        config = factory.get_default_config()

        # spot/status endpoint
        assert "relative_spot_resource_identifier_path" in config
        assert "status_action_name" in config

        # user/assets endpoint
        assert "relative_user_resource_identifier_path" in config
        assert "assets_action_name" in config

        # user/spot/order endpoint
        assert "relative_user_spot_resource_identifier_path" in config
        assert "order_action_name" in config

    def test_factory_config_does_not_have_old_keys(self, factory):
        """Verify old configuration keys have been removed"""
        config = factory.get_default_config()

        # Removed old keys
        assert "spot_status_action_name" not in config
        assert "resource_identifier_path" not in config  # Generic name removed

    def test_spot_status_path_construction(self, factory):
        """Verify spot/status endpoint path construction is correct"""
        config = factory.get_default_config()

        resource_path = config["relative_spot_resource_identifier_path"].joinpath(
            config["status_action_name"].path
        )

        assert resource_path.path == "spot/status"

    def test_assets_path_construction(self, factory):
        """Verify user/assets endpoint path construction is correct"""
        config = factory.get_default_config()

        resource_path = config["relative_user_resource_identifier_path"].joinpath(
            config["assets_action_name"].path
        )

        assert resource_path.path == "user/assets"

    def test_create_order_path_construction(self, factory):
        """Verify user/spot/order endpoint path construction is correct"""
        config = factory.get_default_config()

        resource_path = config["relative_user_spot_resource_identifier_path"].joinpath(
            config["order_action_name"].path
        )

        assert resource_path.path == "user/spot/order"

    def test_config_values_are_url_types(self, factory):
        """Verify all configuration values are URL types"""
        config = factory.get_default_config()

        assert isinstance(config["relative_spot_resource_identifier_path"], URL)
        assert isinstance(config["status_action_name"], URL)
        assert isinstance(config["relative_user_resource_identifier_path"], URL)
        assert isinstance(config["assets_action_name"], URL)
        assert isinstance(config["relative_user_spot_resource_identifier_path"], URL)
        assert isinstance(config["order_action_name"], URL)

    def test_resource_identifier_path_values(self, factory):
        """Verify resource identifier path values are correct"""
        config = factory.get_default_config()

        assert config["relative_spot_resource_identifier_path"].path == "spot"
        assert config["relative_user_resource_identifier_path"].path == "user"
        assert config["relative_user_spot_resource_identifier_path"].path == "user/spot"

    def test_action_name_values(self, factory):
        """Verify action name values are correct"""
        config = factory.get_default_config()

        assert config["status_action_name"].path == "status"
        assert config["assets_action_name"].path == "assets"
        assert config["order_action_name"].path == "order"

    def test_full_url_construction_spot_status(self, factory):
        """Verify full URL construction for spot/status"""
        config = factory.get_default_config()

        base_url = config["private_base_url"]
        relative_stub_path = config["private_relative_stub_path"]
        resource_path = config["relative_spot_resource_identifier_path"].joinpath(
            config["status_action_name"].path
        )

        # Same logic as EndpointRequestBuilder for URL construction
        # Add leading slash to relative stub path to make stub path
        stub_path = URL("/") / relative_stub_path.path
        full_path = stub_path / resource_path.path
        full_url = base_url.with_path(full_path.path)

        expected_url = "https://api.bitbank.cc/v1/spot/status"
        assert str(full_url) == expected_url

    def test_full_url_construction_assets(self, factory):
        """Verify full URL construction for user/assets"""
        config = factory.get_default_config()

        base_url = config["private_base_url"]
        relative_stub_path = config["private_relative_stub_path"]
        resource_path = config["relative_user_resource_identifier_path"].joinpath(
            config["assets_action_name"].path
        )

        # Add leading slash to relative stub path to make stub path
        stub_path = URL("/") / relative_stub_path.path
        full_path = stub_path / resource_path.path
        full_url = base_url.with_path(full_path.path)

        expected_url = "https://api.bitbank.cc/v1/user/assets"
        assert str(full_url) == expected_url

    def test_full_url_construction_create_order(self, factory):
        """Verify full URL construction for user/spot/order"""
        config = factory.get_default_config()

        base_url = config["private_base_url"]
        relative_stub_path = config["private_relative_stub_path"]
        resource_path = config["relative_user_spot_resource_identifier_path"].joinpath(
            config["order_action_name"].path
        )

        # Add leading slash to relative stub path to make stub path
        stub_path = URL("/") / relative_stub_path.path
        full_path = stub_path / resource_path.path
        full_url = base_url.with_path(full_path.path)

        expected_url = "https://api.bitbank.cc/v1/user/spot/order"
        assert str(full_url) == expected_url
