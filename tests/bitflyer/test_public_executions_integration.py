"""Integration tests for PublicExecutions

Tests message to domain model conversion and processing via DecimalJsonParser
"""

from decimal import Decimal

from crypto_api_client.bitflyer._native_messages import (
    PublicExecution,
    PublicExecutionsMessage,
)
from crypto_api_client.bitflyer.native_domain_models import Side
from crypto_api_client.core.decimal_json_parser import DecimalJsonParser


class TestPublicExecutionsIntegration:
    """Integration test class for PublicExecutions"""

    def test_message_to_domain_model_conversion(self):
        """Message to domain model conversion"""
        # JSON string mocking API response
        json_response = """[
            {
                "id": 2622084310,
                "side": "BUY",
                "price": 16508699.0,
                "size": 0.01,
                "exec_date": "2025-09-28T19:27:57.177",
                "buy_child_order_acceptance_id": "JRF20250928-192757-546175",
                "sell_child_order_acceptance_id": "JRF20250928-192750-019464"
            },
            {
                "id": 2622084179,
                "side": "",
                "price": 16477300.0,
                "size": 0.001,
                "exec_date": "2025-09-28T19:12:00.633",
                "buy_child_order_acceptance_id": "JRF20250928-191136-020706",
                "sell_child_order_acceptance_id": "JRF20250928-191157-011172"
            }
        ]"""

        # Convert to domain model via message
        message = PublicExecutionsMessage(json_response)
        executions = message.to_domain_model()

        assert len(executions) == 2

        # Normal execution
        assert executions[0].id == 2622084310
        assert executions[0].side == Side.BUY
        assert executions[0].price == Decimal("16508699.0")

        # Itayose execution (empty string converted to None)
        assert executions[1].id == 2622084179
        assert executions[1].side is None
        assert executions[1].price == Decimal("16477300.0")

    def test_decimal_parser_with_empty_side(self):
        """Empty string processing via DecimalJsonParser"""
        # Data including itayose execution
        json_str = """[
            {
                "id": 2622084179,
                "side": "",
                "price": 16477300.123456,
                "size": 0.00000001,
                "exec_date": "2025-09-28T19:12:00.633",
                "buy_child_order_acceptance_id": "JRF20250928-191136-020706",
                "sell_child_order_acceptance_id": "JRF20250928-191157-011172"
            }
        ]"""

        # Parse with DecimalJsonParser
        executions = DecimalJsonParser.parse(json_str, list[PublicExecution])

        assert len(executions) == 1
        execution = executions[0]

        # Empty string converted to None
        assert execution.side is None
        # Decimal precision preserved
        assert execution.price == Decimal("16477300.123456")
        assert execution.size == Decimal("0.00000001")

    def test_mixed_executions_list(self):
        """List with mixed normal and itayose executions"""
        # Mixed data (based on actual API response)
        json_str = """[
            {
                "id": 2622084310,
                "side": "BUY",
                "price": 16508699.0,
                "size": 0.01,
                "exec_date": "2025-09-28T19:27:57.177",
                "buy_child_order_acceptance_id": "JRF20250928-192757-546175",
                "sell_child_order_acceptance_id": "JRF20250928-192750-019464"
            },
            {
                "id": 2622084309,
                "side": "SELL",
                "price": 16508786.0,
                "size": 0.02,
                "exec_date": "2025-09-28T19:27:47.630",
                "buy_child_order_acceptance_id": "JRF20250928-192747-546075",
                "sell_child_order_acceptance_id": "JRF20250928-192745-019426"
            },
            {
                "id": 2622084179,
                "side": "",
                "price": 16477300.0,
                "size": 0.001,
                "exec_date": "2025-09-28T19:12:00.633",
                "buy_child_order_acceptance_id": "JRF20250928-191136-020706",
                "sell_child_order_acceptance_id": "JRF20250928-191157-011172"
            },
            {
                "id": 2622084178,
                "side": "",
                "price": 16477300.0,
                "size": 0.02075121,
                "exec_date": "2025-09-28T19:12:00.633",
                "buy_child_order_acceptance_id": "JRF20250928-191136-020706",
                "sell_child_order_acceptance_id": "JRF20250928-191133-010185"
            },
            {
                "id": 2622084177,
                "side": "BUY",
                "price": 16508800.0,
                "size": 0.005,
                "exec_date": "2025-09-28T19:27:26.277",
                "buy_child_order_acceptance_id": "JRF20250928-192726-006197",
                "sell_child_order_acceptance_id": "JRF20250928-192700-024188"
            }
        ]"""

        # Convert via message
        message = PublicExecutionsMessage(json_str)
        executions = message.to_domain_model()

        assert len(executions) == 5

        # Normal executions
        buy_executions = [e for e in executions if e.side == Side.BUY]
        sell_executions = [e for e in executions if e.side == Side.SELL]
        itayose_executions = [e for e in executions if e.side is None]

        assert len(buy_executions) == 2
        assert len(sell_executions) == 1
        assert len(itayose_executions) == 2

        # Itayose executions have same price
        assert all(e.price == Decimal("16477300.0") for e in itayose_executions)

    def test_empty_list(self):
        """Empty list processing"""
        json_str = "[]"
        message = PublicExecutionsMessage(json_str)
        executions = message.to_domain_model()
        assert executions == []

    def test_single_itayose_execution(self):
        """Single itayose execution processing"""
        json_str = """[
            {
                "id": 2622084179,
                "side": "",
                "price": 16477300.0,
                "size": 0.001,
                "exec_date": "2025-09-28T19:12:00.633",
                "buy_child_order_acceptance_id": "JRF20250928-191136-020706",
                "sell_child_order_acceptance_id": "JRF20250928-191157-011172"
            }
        ]"""

        executions = DecimalJsonParser.parse(json_str, list[PublicExecution])
        assert len(executions) == 1
        assert executions[0].side is None
        assert executions[0].id == 2622084179

    def test_payload_json_integrity(self):
        """Payload JSON string is correctly preserved"""
        original_json = """[{"id":123,"side":"","price":100.0,"size":0.1,"exec_date":"2025-01-01T00:00:00","buy_child_order_acceptance_id":"A","sell_child_order_acceptance_id":"B"}]"""

        message = PublicExecutionsMessage(original_json)
        # JSON string is preserved internally
        assert message.payload.content_str == original_json

        # Correctly processed after conversion
        executions = message.to_domain_model()
        assert len(executions) == 1
        assert executions[0].side is None