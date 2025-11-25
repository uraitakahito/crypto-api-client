"""Tests for BoardStateMessage"""

import pytest

from crypto_api_client.bitflyer._native_messages.board_state_message import (
    BoardStateMessage,
)
from crypto_api_client.bitflyer.native_domain_models.board_state import BoardState
from crypto_api_client.bitflyer.native_domain_models.board_state_type import (
    BoardStateType,
)
from crypto_api_client.bitflyer.native_domain_models.health_status_type import (
    HealthStatusType,
)


class TestBoardStateMessage:
    """Tests for BoardStateMessage class"""

    @pytest.fixture
    def valid_board_state_json(self) -> str:
        """Valid board state JSON data"""
        return """{
            "health": "NORMAL",
            "state": "RUNNING"
        }"""

    @pytest.fixture
    def circuit_break_json(self) -> str:
        """JSON data for circuit break state"""
        return """{
            "health": "STOP",
            "state": "CIRCUIT BREAK"
        }"""

    def test_init_with_valid_json(self, valid_board_state_json: str) -> None:
        """Test initialization with valid JSON"""
        message = BoardStateMessage(valid_board_state_json)

        assert message.metadata is None
        assert message.payload is not None
        assert message.payload.content_str == valid_board_state_json

    def test_to_domain_model(self, valid_board_state_json: str) -> None:
        """Test conversion to domain model"""
        message = BoardStateMessage(valid_board_state_json)

        board_state = message.to_domain_model()
        assert isinstance(board_state, BoardState)
        assert board_state.health == HealthStatusType.NORMAL
        assert board_state.state == BoardStateType.RUNNING

    def test_to_domain_model_circuit_break(self, circuit_break_json: str) -> None:
        """Test domain model conversion during circuit break"""
        message = BoardStateMessage(circuit_break_json)

        board_state = message.to_domain_model()
        assert board_state.health == HealthStatusType.STOP
        assert board_state.state == BoardStateType.CIRCUIT_BREAK

    def test_to_domain_model_consistency(self, valid_board_state_json: str) -> None:
        """Test consistency of to_domain_model method"""
        message = BoardStateMessage(valid_board_state_json)

        board_state_1 = message.to_domain_model()
        board_state_2 = message.to_domain_model()

        assert board_state_1.health == board_state_2.health
        assert board_state_1.state == board_state_2.state
