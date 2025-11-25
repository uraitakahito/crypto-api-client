"""Tests for TimeInForce Enum constructor"""

import pytest

from crypto_api_client.bitflyer.native_domain_models.time_in_force import TimeInForce


class TestTimeInForceConstructor:
    """Test constructor and validation of TimeInForce Enum."""

    @pytest.mark.parametrize(
        ("input_value", "expected"),
        [
            ("GTC", TimeInForce.GTC),
            ("IOC", TimeInForce.IOC),
            ("FOK", TimeInForce.FOK),
            ("gtc", TimeInForce.GTC),  # lowercase
            ("iOc", TimeInForce.IOC),  # mixed case
        ],
    )
    def test_constructor_valid_cases(
        self, input_value: str, expected: TimeInForce
    ) -> None:
        """Test that TimeInForce Enum can be correctly created from various valid input values."""
        # Assumes caller uses .upper()
        time_in_force = TimeInForce(input_value.upper())
        assert time_in_force == expected

    @pytest.mark.parametrize(
        ("input_value", "error_message"),
        [
            ("INVALID", "'INVALID' is not a valid TimeInForce"),
            ("GOOD_TILL_CANCEL", "'GOOD_TILL_CANCEL' is not a valid TimeInForce"),
            ("", "'' is not a valid TimeInForce"),
        ],
    )
    def test_constructor_invalid_cases(
        self, input_value: str, error_message: str
    ) -> None:
        """Test that ValueError is raised for invalid input values."""
        with pytest.raises(ValueError, match=error_message):
            TimeInForce(input_value)

    def test_constructor_with_none_raises_error(self) -> None:
        """Test that ValueError is raised when None is input."""
        with pytest.raises(ValueError, match="None is not a valid TimeInForce"):
            TimeInForce(None)  # type: ignore

    def test_enum_members_are_correct(self) -> None:
        """Verify that Enum members are correctly defined."""
        assert TimeInForce.GTC.value == "GTC"
        assert TimeInForce.IOC.value == "IOC"
        assert TimeInForce.FOK.value == "FOK"
        assert len(TimeInForce) == 3
