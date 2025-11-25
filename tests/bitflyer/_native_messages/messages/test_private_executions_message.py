"""Tests for PrivateExecutionsMessage"""

from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from crypto_api_client.bitflyer._native_messages.private_executions_message import (
    PrivateExecutionsMessage,
)
from crypto_api_client.bitflyer.native_domain_models.private_execution import (
    PrivateExecution,
)
from crypto_api_client.bitflyer.native_domain_models.side import Side


class TestPrivateExecutionsMessage:
    """Tests for PrivateExecutionsMessage class"""

    @pytest.fixture
    def valid_private_executions_json(self) -> str:
        """Valid private executions JSON data (array)"""
        return """[
            {
                "id": 100001,
                "side": "BUY",
                "price": 15900000,
                "size": 0.001,
                "exec_date": "2025-01-01T10:00:00Z",
                "commission": 0.0000015,
                "child_order_id": "JOR20250101-100000-123456",
                "child_order_acceptance_id": "JRF20250101-100000-123456"
            },
            {
                "id": 100002,
                "side": "SELL",
                "price": 16000000,
                "size": 0.002,
                "exec_date": "2025-01-01T11:00:00Z",
                "commission": 0.0000030,
                "child_order_id": "JOR20250101-110000-234567",
                "child_order_acceptance_id": "JRF20250101-110000-234567"
            }
        ]"""

    def test_init_with_valid_json(self, valid_private_executions_json: str) -> None:
        """Test initialization with valid JSON"""
        message = PrivateExecutionsMessage(valid_private_executions_json)

        # Access payload property and verify
        assert message.payload.content_str == valid_private_executions_json

    def test_to_domain_model(self, valid_private_executions_json: str) -> None:
        """Test conversion to domain model"""
        message = PrivateExecutionsMessage(valid_private_executions_json)

        executions = message.to_domain_model()
        assert isinstance(executions, list)
        assert len(executions) == 2

        # Verify first execution
        exec1 = executions[0]
        assert isinstance(exec1, PrivateExecution)
        assert exec1.id == 100001
        assert exec1.side == Side.BUY
        assert exec1.price == Decimal("15900000")
        assert exec1.size == Decimal("0.001")
        assert exec1.commission == Decimal("0.0000015")
        assert exec1.child_order_id == "JOR20250101-100000-123456"
        assert exec1.child_order_acceptance_id == "JRF20250101-100000-123456"
        assert isinstance(exec1.exec_date, datetime)
        assert exec1.exec_date.tzinfo == ZoneInfo("UTC")

        # Verify second execution (sell)
        exec2 = executions[1]
        assert exec2.id == 100002
        assert exec2.side == Side.SELL
        assert exec2.price == Decimal("16000000")
        assert exec2.size == Decimal("0.002")
        assert exec2.commission == Decimal("0.0000030")

    def test_empty_executions(self) -> None:
        """Test conversion with empty execution list"""
        message = PrivateExecutionsMessage("[]")

        executions = message.to_domain_model()
        assert isinstance(executions, list)
        assert len(executions) == 0

    def test_with_timezone(self, valid_private_executions_json: str) -> None:
        """Test timezone conversion"""
        message = PrivateExecutionsMessage(valid_private_executions_json)
        executions = message.to_domain_model()

        # Convert to Tokyo time
        jst = ZoneInfo("Asia/Tokyo")
        exec_jst = executions[0].with_timezone(jst)

        # Verify timezone has changed
        assert exec_jst.exec_date.tzinfo == jst
        # Verify original instance is unchanged (immutable)
        assert executions[0].exec_date.tzinfo == ZoneInfo("UTC")

    def test_itayose_private_execution_without_side(self) -> None:
        """Test when itayose execution (without side field) is returned in Private API"""
        itayose_json = """[
            {
                "id": 2621689708,
                "price": 16531800.0,
                "size": 0.01872934,
                "exec_date": "2025-09-23T19:12:00.237",
                "commission": 0.0000028,
                "child_order_id": "JOR20250923-191108-040197",
                "child_order_acceptance_id": "JRF20250923-191108-040197"
            }
        ]"""

        message = PrivateExecutionsMessage(itayose_json)
        executions = message.to_domain_model()

        assert len(executions) == 1
        execution = executions[0]
        assert execution.id == 2621689708
        assert execution.side is None  # None for itayose
        assert execution.price == Decimal("16531800.0")
        assert execution.size == Decimal("0.01872934")
        assert execution.commission == Decimal("0.0000028")

    def test_mixed_private_executions_with_and_without_side(self) -> None:
        """Test when normal and itayose executions are mixed in Private API"""
        mixed_json = """[
            {
                "id": 100001,
                "side": "BUY",
                "price": 15900000,
                "size": 0.001,
                "exec_date": "2025-01-01T10:00:00Z",
                "commission": 0.0000015,
                "child_order_id": "JOR20250101-100000-123456",
                "child_order_acceptance_id": "JRF20250101-100000-123456"
            },
            {
                "id": 2621689708,
                "price": 16531800.0,
                "size": 0.01872934,
                "exec_date": "2025-09-23T19:12:00.237",
                "commission": 0.0000028,
                "child_order_id": "JOR20250923-191108-040197",
                "child_order_acceptance_id": "JRF20250923-191108-040197"
            }
        ]"""

        message = PrivateExecutionsMessage(mixed_json)
        executions = message.to_domain_model()

        assert len(executions) == 2

        # Normal execution
        assert executions[0].id == 100001
        assert executions[0].side == Side.BUY

        # Itayose execution
        assert executions[1].id == 2621689708
        assert executions[1].side is None

    def test_private_execution_str_with_no_side(self) -> None:
        """Test string representation of itayose execution (empty side)"""
        itayose_json = """[
            {
                "id": 2621689708,
                "price": 16531800.0,
                "size": 0.01872934,
                "exec_date": "2025-09-23T19:12:00.237",
                "commission": 0.0000028,
                "child_order_id": "JOR20250923-191108-040197",
                "child_order_acceptance_id": "JRF20250923-191108-040197"
            }
        ]"""

        message = PrivateExecutionsMessage(itayose_json)
        execution = message.to_domain_model()[0]

        # Verify side part is blank (7 spaces) in string representation
        str_repr = str(execution)
        assert " |         | " in str_repr  # side part is 7 blank spaces
        assert "2621689708" in str_repr  # ID
        assert "16531800" in str_repr  # price
