"""Tests for GMO Coin TickerPayload"""

import json

import pytest

from crypto_api_client.gmocoin._native_messages.ticker_payload import TickerPayload


class TestTickerPayload:
    """Tests for TickerPayload"""

    def test_content_str_extracts_array(self) -> None:
        """Verify content_str extracts array from 'data': [...]"""
        json_str = '"data": [{"ask": "100", "bid": "99", "symbol": "BTC"}]'

        payload = TickerPayload(json_str)
        content = payload.content_str

        parsed = json.loads(content)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["ask"] == "100"

    def test_content_str_extracts_multiple_elements(self) -> None:
        """Verify extraction with multiple elements in array"""
        json_str = '"data": [{"symbol": "BTC"}, {"symbol": "ETH"}]'

        payload = TickerPayload(json_str)
        content = payload.content_str

        parsed = json.loads(content)
        assert len(parsed) == 2

    def test_content_str_extracts_empty_array(self) -> None:
        """Verify extraction of empty array"""
        json_str = '"data": []'

        payload = TickerPayload(json_str)
        content = payload.content_str

        parsed = json.loads(content)
        assert parsed == []

    def test_content_str_handles_nested_objects(self) -> None:
        """Verify extraction with nested objects inside array"""
        json_str = '"data": [{"nested": {"key": "value"}, "arr": [1, 2]}]'

        payload = TickerPayload(json_str)
        content = payload.content_str

        parsed = json.loads(content)
        assert parsed[0]["nested"]["key"] == "value"
        assert parsed[0]["arr"] == [1, 2]

    def test_content_str_no_bracket_raises_error(self) -> None:
        """Verify ValueError when no [ or { found"""
        payload = TickerPayload("no brackets here")

        with pytest.raises(ValueError, match="Opening character"):
            payload.content_str

    def test_content_str_unclosed_bracket_raises_error(self) -> None:
        """Verify ValueError when closing bracket not found"""
        payload = TickerPayload('"data": [{"unclosed": true')

        with pytest.raises(ValueError, match="Closing character"):
            payload.content_str

    def test_raw_json_preserves_original(self) -> None:
        """Verify raw_json returns original string"""
        json_str = '"data": [{"ask": "100"}]'

        payload = TickerPayload(json_str)

        assert payload.raw_json == json_str
