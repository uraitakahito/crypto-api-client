"""Tests for BoardStateType"""

import pytest

from crypto_api_client.bitflyer.native_domain_models.board_state_type import (
    BoardStateType,
)


class TestBoardStateType:
    """Tests for BoardStateType enum"""

    def test_all_values(self) -> None:
        """Verify all values are defined"""
        assert BoardStateType.RUNNING.value == "RUNNING"
        assert BoardStateType.CLOSED.value == "CLOSED"
        assert BoardStateType.STARTING.value == "STARTING"
        assert BoardStateType.PREOPEN.value == "PREOPEN"
        assert BoardStateType.CIRCUIT_BREAK.value == "CIRCUIT BREAK"

    def test_from_string(self) -> None:
        """Conversion from string to enum"""
        assert BoardStateType("RUNNING") == BoardStateType.RUNNING
        assert BoardStateType("CLOSED") == BoardStateType.CLOSED
        assert BoardStateType("CIRCUIT BREAK") == BoardStateType.CIRCUIT_BREAK

    def test_invalid_value(self) -> None:
        """Invalid value case"""
        with pytest.raises(ValueError):
            BoardStateType("INVALID")
