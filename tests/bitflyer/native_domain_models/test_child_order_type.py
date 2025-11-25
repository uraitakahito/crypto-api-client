"""Tests for ChildOrderType Enum constructor"""

import pytest

from crypto_api_client.bitflyer.native_domain_models.child_order_type import (
    ChildOrderType,
)


class TestChildOrderTypeConstructor:
    """Test constructor and validation of ChildOrderType Enum."""

    def test_constructor_valid_input_success(self) -> None:
        """Test that ChildOrderType can be created with valid values"""
        assert ChildOrderType("LIMIT") == ChildOrderType.LIMIT
        assert ChildOrderType("MARKET") == ChildOrderType.MARKET

    def test_constructor_invalid_input_error(self) -> None:
        """Test that error is raised with invalid values"""
        with pytest.raises(ValueError):
            ChildOrderType("INVALID")
        with pytest.raises(ValueError):
            ChildOrderType("limit")  # lowercase is invalid

    def test_constructor_none_input_error(self) -> None:
        """Test that error is raised with None"""
        with pytest.raises((TypeError, ValueError)):
            ChildOrderType(None)  # type: ignore

    def test_enum_members_are_correct(self) -> None:
        """Test that Enum members are correct"""
        assert ChildOrderType.LIMIT.value == "LIMIT"
        assert ChildOrderType.MARKET.value == "MARKET"
        members = set(member.value for member in ChildOrderType)
        assert "LIMIT" in members
        assert "MARKET" in members
