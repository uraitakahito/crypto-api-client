"""Tests for Side Enum constructor"""

import pytest

from crypto_api_client.bitflyer.native_domain_models.side import Side


class TestSideConstructor:
    """Test constructor and validation of Side Enum."""

    def test_constructor_valid_input_success(self) -> None:
        """Test that Side can be created with valid values"""
        assert Side("BUY") == Side.BUY
        assert Side("SELL") == Side.SELL

    def test_constructor_invalid_input_error(self) -> None:
        """Test that error is raised with invalid values"""
        with pytest.raises(ValueError):
            Side("INVALID")
        with pytest.raises(ValueError):
            Side("buy")  # lowercase is invalid

    def test_constructor_none_input_error(self) -> None:
        """Test that error is raised with None"""
        with pytest.raises((TypeError, ValueError)):
            Side(None)  # type: ignore

    def test_enum_members_are_correct(self) -> None:
        """Test that Enum members are correct"""
        assert Side.BUY.value == "BUY"
        assert Side.SELL.value == "SELL"
        assert set(member.value for member in Side) == {"BUY", "SELL"}
