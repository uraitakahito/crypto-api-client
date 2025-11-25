"""Tests for MarketsPayload"""

import pytest

from crypto_api_client.bitflyer._native_messages.markets_payload import MarketsPayload


class TestMarketsPayload:
    """Tests for MarketsPayload class"""

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
            },
            {
                "product_code": "BTCJPY_MAT1WK",
                "market_type": "Futures",
                "alias": "BTCJPY_Mat1Week"
            },
            {
                "product_code": "BTCJPY_MAT2WK",
                "market_type": "Futures",
                "alias": "BTCJPY_Mat2Week"
            }
        ]"""

    def test_init_with_valid_json(self, valid_markets_json: str) -> None:
        """Test initialization with valid JSON"""
        payload = MarketsPayload(valid_markets_json)

        assert payload.content_str == valid_markets_json

    def test_init_with_empty_array(self) -> None:
        """Test initialization with empty array"""
        json_str = "[]"
        payload = MarketsPayload(json_str)

        assert payload.content_str == json_str

    def test_init_with_single_market(self) -> None:
        """Test initialization with single market"""
        json_str = """[
            {
                "product_code": "BTC_JPY",
                "market_type": "Spot",
                "alias": null
            }
        ]"""
        payload = MarketsPayload(json_str)

        assert payload.content_str == json_str

    def test_init_with_futures_market(self) -> None:
        """Test initialization with futures market"""
        json_str = """[
            {
                "product_code": "BTCJPY_MAT3M",
                "market_type": "Futures",
                "alias": "BTCJPY_Mat3Month"
            }
        ]"""
        payload = MarketsPayload(json_str)

        assert payload.content_str == json_str
