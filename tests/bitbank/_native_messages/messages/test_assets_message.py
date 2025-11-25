"""Tests for AssetsMessage."""

from decimal import Decimal

import pytest

from crypto_api_client.bitbank._native_messages.assets_message import AssetsMessage
from crypto_api_client.bitbank._native_messages.message_metadata import (
    MessageMetadata,
)
from crypto_api_client.bitbank.native_domain_models import Asset


class TestAssetsMessage:
    """Tests for AssetsMessage class."""

    @pytest.fixture
    def valid_assets_json(self) -> str:
        """Valid assets message JSON string."""
        return """{
            "success": 1,
            "data": {
                "assets": [
                    {
                        "asset": "jpy",
                        "amount_precision": 4,
                        "onhand_amount": "100000.0000",
                        "locked_amount": "0.0000",
                        "free_amount": "100000.0000",
                        "stop_deposit": false,
                        "stop_withdrawal": false,
                        "withdrawal_fee": {
                            "threshold": "30000.0000",
                            "under": "550.0000",
                            "over": "770.0000"
                        }
                    },
                    {
                        "asset": "btc",
                        "amount_precision": 8,
                        "onhand_amount": "10.12345678",
                        "locked_amount": "0.50000000",
                        "free_amount": "9.62345678",
                        "stop_deposit": false,
                        "stop_withdrawal": false,
                        "withdrawal_fee": null
                    }
                ]
            }
        }"""

    @pytest.fixture
    def empty_assets_json(self) -> str:
        """Empty assets message JSON string."""
        return """{
            "success": 1,
            "data": {
                "assets": []
            }
        }"""

    def test_init_with_valid_json(self, valid_assets_json: str) -> None:
        """Test initialization with valid JSON."""
        message = AssetsMessage(valid_assets_json)

        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success == 1
        assert message.metadata.json_str == '{"success": 1}'
        assert message.payload is not None

    def test_init_with_empty_assets(self, empty_assets_json: str) -> None:
        """Test initialization with empty assets."""
        message = AssetsMessage(empty_assets_json)

        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success == 1
        assert message.metadata.json_str == '{"success": 1}'
        assert message.payload is not None

    def test_to_domain_model(self, valid_assets_json: str) -> None:
        """Test conversion to domain model."""
        message = AssetsMessage(valid_assets_json)

        assets = message.to_domain_model()
        assert isinstance(assets, list)
        assert len(assets) == 2

        # JPY asset
        jpy_asset = assets[0]
        assert isinstance(jpy_asset, Asset)
        # Currency symbol validation removed with CurrencyRegistry removal
        assert jpy_asset.asset == "jpy"
        assert jpy_asset.amount_precision == 4
        assert jpy_asset.onhand_amount == Decimal("100000.0000")
        assert jpy_asset.locked_amount == Decimal("0.0000")
        assert jpy_asset.free_amount == Decimal("100000.0000")
        assert jpy_asset.stop_deposit is False
        assert jpy_asset.stop_withdrawal is False
        assert jpy_asset.withdrawal_fee is not None
        assert jpy_asset.withdrawal_fee.threshold == Decimal("30000.0000")
        assert jpy_asset.withdrawal_fee.under == Decimal("550.0000")
        assert jpy_asset.withdrawal_fee.over == Decimal("770.0000")

        # BTC asset
        btc_asset = assets[1]
        assert isinstance(btc_asset, Asset)
        # Currency symbol validation removed with CurrencyRegistry removal
        assert btc_asset.asset == "btc"
        assert btc_asset.amount_precision == 8
        assert btc_asset.onhand_amount == Decimal("10.12345678")
        assert btc_asset.locked_amount == Decimal("0.50000000")
        assert btc_asset.free_amount == Decimal("9.62345678")
        assert btc_asset.stop_deposit is False
        assert btc_asset.stop_withdrawal is False
        assert btc_asset.withdrawal_fee is None

    def test_to_domain_model_empty_assets(self, empty_assets_json: str) -> None:
        """Test domain model conversion with empty assets."""
        message = AssetsMessage(empty_assets_json)

        assets = message.to_domain_model()
        assert isinstance(assets, list)
        assert len(assets) == 0

    def test_init_missing_success_field(self) -> None:
        """Test error when success field is missing."""
        json_str = """{
            "data": {
                "assets": []
            }
        }"""

        message = AssetsMessage(json_str)
        with pytest.raises(
            ValueError,
            match="metadata \\('success' field\\) not found",
        ):
            _ = message.metadata

    def test_init_missing_data_field(self) -> None:
        """Test error when data field is missing."""
        json_str = """{
            "success": 1
        }"""

        message = AssetsMessage(json_str)
        with pytest.raises(ValueError, match="Field 'data' not found"):
            _ = message.payload

    def test_extract_brace_content_with_nested_braces(self) -> None:
        """Test JSON processing with nested braces."""
        json_str = """{
            "success": 1,
            "data": {
                "assets": [
                    {
                        "asset": "test",
                        "nested": {
                            "inner": {
                                "value": 123
                            }
                        }
                    }
                ]
            }
        }"""

        message = AssetsMessage(json_str)
        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success == 1
        assert '"nested": {' in message.payload.content_str

    def test_extract_brace_content_with_whitespace(self) -> None:
        """Test JSON processing with whitespace."""
        json_str = """{
            "success"  :  1,
            "data"   :   {
                "assets": []
            }
        }"""

        message = AssetsMessage(json_str)
        # Parses correctly even with whitespace
        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.success == 1

    def test_invalid_json_structure(self) -> None:
        """Test error with invalid JSON structure."""
        # Data brace is not closed
        json_str = """{
            "success": 1,
            "data": {"""  # Missing closing brace for data

        # _extract_brace_content fails
        message = AssetsMessage(json_str)
        with pytest.raises(ValueError, match="Closing brace not found"):
            _ = message.payload
