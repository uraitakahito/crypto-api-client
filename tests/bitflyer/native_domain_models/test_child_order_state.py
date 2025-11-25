"""Tests for ChildOrderState Enum constructor"""

import pytest

from crypto_api_client.bitflyer.native_domain_models.child_order_state import (
    ChildOrderState,
)


class TestChildOrderStateConstructor:
    """Test constructor and validation of ChildOrderState Enum."""

    @pytest.mark.parametrize(
        ("input_value", "expected"),
        [
            ("ACTIVE", ChildOrderState.ACTIVE),
            ("COMPLETED", ChildOrderState.COMPLETED),
            ("CANCELED", ChildOrderState.CANCELED),
            ("EXPIRED", ChildOrderState.EXPIRED),
            ("REJECTED", ChildOrderState.REJECTED),
            ("active", ChildOrderState.ACTIVE),  # lowercase
            ("completed", ChildOrderState.COMPLETED),
            ("canceled", ChildOrderState.CANCELED),
            ("expired", ChildOrderState.EXPIRED),
            ("rejected", ChildOrderState.REJECTED),
        ],
    )
    def test_constructor_valid_cases(
        self, input_value: str, expected: ChildOrderState
    ) -> None:
        """Test that ChildOrderState Enum can be correctly created from various valid input values."""
        # Assumes caller uses .upper()
        order_state = ChildOrderState(input_value.upper())
        assert order_state == expected

    @pytest.mark.parametrize(
        ("input_value", "error_message"),
        [
            ("INVALID", "'INVALID' is not a valid ChildOrderState"),
            ("PENDING", "'PENDING' is not a valid ChildOrderState"),
            ("", "'' is not a valid ChildOrderState"),
        ],
    )
    def test_constructor_invalid_cases(
        self, input_value: str, error_message: str
    ) -> None:
        """Test that ValueError is raised for invalid input values."""
        with pytest.raises(ValueError, match=error_message):
            ChildOrderState(input_value)

    def test_constructor_with_none_raises_error(self) -> None:
        """Test that ValueError is raised when None is input."""
        with pytest.raises(ValueError, match="None is not a valid ChildOrderState"):
            ChildOrderState(None)  # type: ignore

    def test_enum_members_are_correct(self) -> None:
        """Verify that Enum members are correctly defined."""
        assert ChildOrderState.ACTIVE.value == "ACTIVE"
        assert ChildOrderState.COMPLETED.value == "COMPLETED"
        assert ChildOrderState.CANCELED.value == "CANCELED"
        assert ChildOrderState.EXPIRED.value == "EXPIRED"
        assert ChildOrderState.REJECTED.value == "REJECTED"
        assert len(ChildOrderState) == 5
