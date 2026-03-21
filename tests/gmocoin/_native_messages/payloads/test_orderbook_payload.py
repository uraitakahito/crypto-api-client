"""Tests for GMO Coin OrderBookPayload"""

import json

from crypto_api_client.gmocoin._native_messages.orderbook_payload import (
    OrderBookPayload,
)


class TestOrderBookPayload:
    """Tests for OrderBookPayload"""

    def test_content_str_extracts_object(self) -> None:
        """Verify content_str extracts object from 'data': {...}"""
        json_str = '"data": {"asks": [{"price": "100", "size": "0.1"}], "bids": [], "symbol": "BTC"}'

        payload = OrderBookPayload(json_str)
        content = payload.content_str

        parsed = json.loads(content)
        assert isinstance(parsed, dict)
        assert "asks" in parsed
        assert "bids" in parsed
        assert "symbol" in parsed

    def test_content_str_excludes_data_key(self) -> None:
        """Verify that 'data' wrapper key is excluded from content"""
        json_str = '"data": {"symbol": "BTC", "asks": [], "bids": []}'

        payload = OrderBookPayload(json_str)
        content = payload.content_str

        # Content should start with { not with "data"
        assert content.strip().startswith("{")
        assert '"data"' not in content

    def test_content_str_is_valid_json(self) -> None:
        """Verify content_str returns valid parseable JSON"""
        json_str = '"data": {"asks": [{"price": "455659", "size": "0.1"}], "bids": [{"price": "455650", "size": "0.2"}], "symbol": "BTC"}'

        payload = OrderBookPayload(json_str)
        parsed = json.loads(payload.content_str)

        assert parsed["asks"][0]["price"] == "455659"
        assert parsed["bids"][0]["size"] == "0.2"

    def test_raw_json_preserves_original(self) -> None:
        """Verify raw_json returns original string"""
        json_str = '"data": {"asks": [], "bids": [], "symbol": "BTC"}'

        payload = OrderBookPayload(json_str)

        assert payload.raw_json == json_str
