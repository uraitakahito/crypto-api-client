"""Tests for PublicExecutionsMessage"""

from datetime import datetime
from decimal import Decimal

import pytest

from crypto_api_client.bitflyer._native_messages.public_executions_message import (
    PublicExecutionsMessage,
)
from crypto_api_client.bitflyer.native_domain_models.public_execution import (
    PublicExecution,
)
from crypto_api_client.bitflyer.native_domain_models.side import Side


class TestPublicExecutionsMessage:
    """Tests for PublicExecutionsMessage class"""

    @pytest.fixture
    def valid_executions_json(self) -> str:
        """Valid execution JSON data (array)"""
        return """[
            {
                "id": 39287,
                "side": "BUY",
                "price": 31690,
                "size": 0.01,
                "exec_date": "2015-07-07T09:57:40.397",
                "buy_child_order_acceptance_id": "JRF20150707-095739-268738",
                "sell_child_order_acceptance_id": "JRF20150707-095739-397698"
            },
            {
                "id": 39286,
                "side": "BUY",
                "price": 33170,
                "size": 0.02,
                "exec_date": "2015-07-07T09:43:34.823",
                "buy_child_order_acceptance_id": "JRF20150707-094334-349118",
                "sell_child_order_acceptance_id": "JRF20150707-094334-823512"
            },
            {
                "id": 39285,
                "side": "SELL",
                "price": 33000,
                "size": 0.005,
                "exec_date": "2015-07-07T09:40:10.123",
                "buy_child_order_acceptance_id": "JRF20150707-094010-123456",
                "sell_child_order_acceptance_id": "JRF20150707-094010-654321"
            }
        ]"""

    def test_init_with_valid_json(self, valid_executions_json: str) -> None:
        """Test initialization with valid JSON"""
        message = PublicExecutionsMessage(valid_executions_json)

        assert message.metadata is None
        assert message.payload is not None
        assert message.payload.content_str == valid_executions_json

    def test_to_domain_model(self, valid_executions_json: str) -> None:
        """Test conversion to domain model"""
        message = PublicExecutionsMessage(valid_executions_json)

        executions = message.to_domain_model()
        assert isinstance(executions, list)
        assert len(executions) == 3

        # Verify first execution
        exec1 = executions[0]
        assert isinstance(exec1, PublicExecution)
        assert exec1.id == 39287
        assert exec1.side == Side.BUY  # Enum value, not string
        assert exec1.price == Decimal("31690")
        assert exec1.size == Decimal("0.01")
        assert exec1.buy_child_order_acceptance_id == "JRF20150707-095739-268738"
        assert exec1.sell_child_order_acceptance_id == "JRF20150707-095739-397698"
        assert isinstance(exec1.exec_date, datetime)
        # Note: exec_date might not have timezone info in the parsed data
        assert isinstance(exec1.exec_date, datetime)

        # Verify third execution (sell)
        exec3 = executions[2]
        assert exec3.side == Side.SELL  # Enum value, not string
        assert exec3.price == Decimal("33000")
        assert exec3.size == Decimal("0.005")

    def test_to_executions_alias_method(self, valid_executions_json: str) -> None:
        """Test to_domain_model method (no alias method exists)"""
        message = PublicExecutionsMessage(valid_executions_json)

        executions = message.to_domain_model()
        assert len(executions) == 3
        assert executions[0].id == 39287
        assert executions[0].price == Decimal("31690")

    def test_empty_executions(self) -> None:
        """Test conversion with empty execution list"""
        message = PublicExecutionsMessage("[]")

        executions = message.to_domain_model()
        assert isinstance(executions, list)
        assert len(executions) == 0

    def test_itayose_execution_without_side(self) -> None:
        """Test conversion of itayose execution (without side field)"""
        itayose_json = """[
            {
                "id": 2621689708,
                "price": 16531800.0,
                "size": 0.01872934,
                "exec_date": "2025-09-23T19:12:00.237",
                "buy_child_order_acceptance_id": "JRF20250923-191108-040197",
                "sell_child_order_acceptance_id": "JRF20250923-191147-066739"
            }
        ]"""

        message = PublicExecutionsMessage(itayose_json)
        executions = message.to_domain_model()

        assert len(executions) == 1
        execution = executions[0]
        assert execution.id == 2621689708
        assert execution.side is None  # None for itayose
        assert execution.price == Decimal("16531800.0")
        assert execution.size == Decimal("0.01872934")

    def test_mixed_executions_with_and_without_side(self) -> None:
        """Test when normal and itayose executions are mixed"""
        mixed_json = """[
            {
                "id": 2621690106,
                "side": "BUY",
                "price": 16517002.0,
                "size": 0.00108143,
                "exec_date": "2025-09-23T19:35:34.637",
                "buy_child_order_acceptance_id": "JRF20250923-193534-063450",
                "sell_child_order_acceptance_id": "JRF20250923-193531-058308"
            },
            {
                "id": 2621689708,
                "price": 16531800.0,
                "size": 0.01872934,
                "exec_date": "2025-09-23T19:12:00.237",
                "buy_child_order_acceptance_id": "JRF20250923-191108-040197",
                "sell_child_order_acceptance_id": "JRF20250923-191147-066739"
            }
        ]"""

        message = PublicExecutionsMessage(mixed_json)
        executions = message.to_domain_model()

        assert len(executions) == 2

        # Normal execution
        assert executions[0].id == 2621690106
        assert executions[0].side == Side.BUY

        # Itayose execution
        assert executions[1].id == 2621689708
        assert executions[1].side is None
