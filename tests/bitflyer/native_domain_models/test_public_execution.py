"""Tests for PublicExecution model

Tests side field validation including empty string processing during itayose execution
"""

import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from crypto_api_client.bitflyer.native_domain_models import PublicExecution, Side


class TestPublicExecution:
    """Test class for PublicExecution model"""

    def test_side_buy(self):
        """BUY side execution is processed correctly"""
        data = {
            "id": 123456789,
            "side": "BUY",
            "price": 16500000.0,
            "size": 0.01,
            "exec_date": "2025-09-28T12:00:00.000",
            "buy_child_order_acceptance_id": "JRF20250928-120000-000001",
            "sell_child_order_acceptance_id": "JRF20250928-120000-000002",
        }
        execution = PublicExecution.model_validate(data)
        assert execution.side == Side.BUY
        assert execution.id == 123456789
        assert execution.price == Decimal("16500000.0")

    def test_side_sell(self):
        """SELL side execution is processed correctly"""
        data = {
            "id": 123456790,
            "side": "SELL",
            "price": 16500100.0,
            "size": 0.02,
            "exec_date": "2025-09-28T12:00:01.000",
            "buy_child_order_acceptance_id": "JRF20250928-120001-000003",
            "sell_child_order_acceptance_id": "JRF20250928-120001-000004",
        }
        execution = PublicExecution.model_validate(data)
        assert execution.side == Side.SELL
        assert execution.price == Decimal("16500100.0")
        assert execution.size == Decimal("0.02")

    def test_side_empty_string(self):
        """Empty string is converted to None (itayose execution)"""
        data = {
            "id": 123456791,
            "side": "",  # API response during itayose execution
            "price": 16477300.0,
            "size": 0.001,
            "exec_date": "2025-09-28T19:12:00.633",
            "buy_child_order_acceptance_id": "JRF20250928-191136-020706",
            "sell_child_order_acceptance_id": "JRF20250928-191157-011172",
        }
        execution = PublicExecution.model_validate(data)
        assert execution.side is None
        assert execution.price == Decimal("16477300.0")

    def test_side_none(self):
        """None is processed correctly"""
        data = {
            "id": 123456792,
            "side": None,
            "price": 16500200.0,
            "size": 0.03,
            "exec_date": "2025-09-28T12:00:02.000",
            "buy_child_order_acceptance_id": "JRF20250928-120002-000005",
            "sell_child_order_acceptance_id": "JRF20250928-120002-000006",
        }
        execution = PublicExecution.model_validate(data)
        assert execution.side is None

    def test_side_field_missing(self):
        """When side field is missing, defaults to None"""
        data = {
            "id": 123456793,
            # "side" field intentionally omitted
            "price": 16500300.0,
            "size": 0.04,
            "exec_date": "2025-09-28T12:00:03.000",
            "buy_child_order_acceptance_id": "JRF20250928-120003-000007",
            "sell_child_order_acceptance_id": "JRF20250928-120003-000008",
        }
        execution = PublicExecution.model_validate(data)
        assert execution.side is None

    def test_invalid_side_value(self):
        """ValidationError is raised for invalid value"""
        data = {
            "id": 123456794,
            "side": "INVALID",
            "price": 16500400.0,
            "size": 0.05,
            "exec_date": "2025-09-28T12:00:04.000",
            "buy_child_order_acceptance_id": "JRF20250928-120004-000009",
            "sell_child_order_acceptance_id": "JRF20250928-120004-000010",
        }
        with pytest.raises(ValidationError) as exc_info:
            PublicExecution.model_validate(data)

        # Verify error message
        error = exc_info.value.errors()[0]
        assert error["loc"] == ("side",)
        assert "Input should be 'BUY' or 'SELL'" in error["msg"]

    def test_parse_actual_api_response(self):
        """Parse actual API response format"""
        # Example of actual API response
        data = {
            "id": 2622084310,
            "side": "BUY",
            "price": 16508699.0,
            "size": 0.01,
            "exec_date": "2025-09-28T19:27:57.177",
            "buy_child_order_acceptance_id": "JRF20250928-192757-546175",
            "sell_child_order_acceptance_id": "JRF20250928-192750-019464",
        }
        execution = PublicExecution.model_validate(data)
        assert execution.id == 2622084310
        assert execution.side == Side.BUY
        assert execution.price == Decimal("16508699.0")
        assert execution.size == Decimal("0.01")
        assert isinstance(execution.exec_date, datetime.datetime)

    def test_parse_itayose_executions(self):
        """Parse list of itayose executions"""
        # Itayose execution data (same time, same price, empty side string)
        itayose_data = [
            {
                "id": 2622084179,
                "side": "",
                "price": 16477300.0,
                "size": 0.001,
                "exec_date": "2025-09-28T19:12:00.633",
                "buy_child_order_acceptance_id": "JRF20250928-191136-020706",
                "sell_child_order_acceptance_id": "JRF20250928-191157-011172",
            },
            {
                "id": 2622084178,
                "side": "",
                "price": 16477300.0,
                "size": 0.02075121,
                "exec_date": "2025-09-28T19:12:00.633",
                "buy_child_order_acceptance_id": "JRF20250928-191136-020706",
                "sell_child_order_acceptance_id": "JRF20250928-191133-010185",
            },
            {
                "id": 2622084177,
                "side": "",
                "price": 16477300.0,
                "size": 0.01,
                "exec_date": "2025-09-28T19:12:00.633",
                "buy_child_order_acceptance_id": "JRF20250928-185950-536600",
                "sell_child_order_acceptance_id": "JRF20250928-191133-010185",
            },
        ]

        executions = [PublicExecution.model_validate(data) for data in itayose_data]

        # All itayose executions have None side
        assert all(execution.side is None for execution in executions)
        # All have same price
        assert all(execution.price == Decimal("16477300.0") for execution in executions)
        # All have same time
        first_exec_date = executions[0].exec_date
        assert all(execution.exec_date == first_exec_date for execution in executions)

    def test_with_timezone(self):
        """Test timezone conversion"""
        from zoneinfo import ZoneInfo

        data = {
            "id": 123456795,
            "side": "BUY",
            "price": 16500500.0,
            "size": 0.06,
            "exec_date": "2025-09-28T12:00:00.000",
            "buy_child_order_acceptance_id": "JRF20250928-120000-000011",
            "sell_child_order_acceptance_id": "JRF20250928-120000-000012",
        }
        execution = PublicExecution.model_validate(data)

        # Convert to Tokyo time
        tokyo_execution = execution.with_timezone(ZoneInfo("Asia/Tokyo"))
        assert tokyo_execution.exec_date.tzinfo is not None
        assert tokyo_execution.side == Side.BUY
        assert tokyo_execution.price == execution.price

    def test_decimal_precision(self):
        """Decimal type precision is preserved"""
        data = {
            "id": 123456796,
            "side": "SELL",
            "price": 16500600.123456789,  # high precision price
            "size": 0.00000001,  # very small size
            "exec_date": "2025-09-28T12:00:00.000",
            "buy_child_order_acceptance_id": "JRF20250928-120000-000013",
            "sell_child_order_acceptance_id": "JRF20250928-120000-000014",
        }
        execution = PublicExecution.model_validate(data)
        # Precision is limited in conversion from float to Decimal
        # Actual API returns as JSON string, so it's properly processed with DecimalJsonParser
        assert str(execution.price).startswith("16500600.123")
        assert execution.size == Decimal("1E-8")
