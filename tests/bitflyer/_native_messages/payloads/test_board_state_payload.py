"""Tests for BoardStatePayload"""

from crypto_api_client.bitflyer._native_messages.board_state_payload import (
    BoardStatePayload,
)


class TestBoardStatePayload:
    """Tests for BoardStatePayload class"""

    def test_content_str_returns_original_json(self) -> None:
        """Verify that content_str returns the original JSON string"""
        json_str = '{"health":"NORMAL","state":"RUNNING"}'
        payload = BoardStatePayload(json_str)

        assert payload.content_str == json_str

    def test_preserves_formatting(self) -> None:
        """Verify that formatting is preserved"""
        json_str = """{
            "health": "BUSY",
            "state": "RUNNING"
        }"""
        payload = BoardStatePayload(json_str)

        assert payload.content_str == json_str
