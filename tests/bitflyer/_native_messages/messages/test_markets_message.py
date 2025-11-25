"""Tests for MarketsMessage"""

import pytest

from crypto_api_client.bitflyer._native_messages.markets_message import (
    MarketsMessage,
)
from crypto_api_client.bitflyer.native_domain_models.market import Market
from crypto_api_client.bitflyer.native_domain_models.market_type import MarketType


class TestMarketsMessage:
    """Tests for MarketsMessage class"""

    @pytest.fixture
    def valid_markets_json(self) -> str:
        """Valid market information JSON data (array)"""
        return """[
            {
                "product_code": "BTC_JPY",
                "market_type": "Spot",
                "alias": null
            },
            {
                "product_code": "FX_BTC_JPY",
                "market_type": "FX",
                "alias": null
            },
            {
                "product_code": "ETH_JPY",
                "market_type": "Spot",
                "alias": null
            }
        ]"""

    def test_init_with_valid_json(self, valid_markets_json: str) -> None:
        """Test initialization with valid JSON"""
        message = MarketsMessage(valid_markets_json)

        assert message.metadata is None
        assert message.payload is not None
        assert message.payload.content_str == valid_markets_json

    def test_to_domain_model(self, valid_markets_json: str) -> None:
        """Test conversion to domain model"""
        message = MarketsMessage(valid_markets_json)

        markets = message.to_domain_model()
        assert isinstance(markets, list)
        assert len(markets) == 3

        # Verify spot market
        btc_jpy = markets[0]
        assert isinstance(btc_jpy, Market)
        assert str(btc_jpy.product_code) == "BTC_JPY"
        assert btc_jpy.market_type == MarketType.Spot

        # Verify FX market
        fx_btc_jpy = markets[1]
        assert str(fx_btc_jpy.product_code) == "FX_BTC_JPY"
        assert fx_btc_jpy.market_type == MarketType.FX

    def test_to_markets_alias_method(self, valid_markets_json: str) -> None:
        """Test to_domain_model method (no alias method exists)"""
        message = MarketsMessage(valid_markets_json)

        markets = message.to_domain_model()
        assert len(markets) == 3
        assert str(markets[0].product_code) == "BTC_JPY"
        assert markets[0].market_type == MarketType.Spot

    def test_empty_markets(self) -> None:
        """Test conversion with empty market list"""
        message = MarketsMessage("[]")

        markets = message.to_domain_model()
        assert isinstance(markets, list)
        assert len(markets) == 0
