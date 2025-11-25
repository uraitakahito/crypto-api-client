"""Tests for HealthStatusType Enum constructor"""

import pytest

from crypto_api_client.bitflyer.native_domain_models.health_status_type import (
    HealthStatusType,
)


class TestHealthStatusTypeConstructor:
    """Test constructor and validation of HealthStatusType Enum."""

    @pytest.mark.parametrize(
        ("input_value", "expected"),
        [
            ("NORMAL", HealthStatusType.NORMAL),
            ("BUSY", HealthStatusType.BUSY),
            ("VERY BUSY", HealthStatusType.VERY_BUSY),
            ("SUPER BUSY", HealthStatusType.SUPER_BUSY),
            ("NO ORDER", HealthStatusType.NO_ORDER),
            ("STOP", HealthStatusType.STOP),
        ],
    )
    def test_constructor_valid_cases(
        self, input_value: str, expected: HealthStatusType
    ) -> None:
        """Test that HealthStatusType Enum can be correctly created from valid input values."""
        health_status = HealthStatusType(input_value)
        assert health_status == expected

    @pytest.mark.parametrize(
        ("input_value", "error_message"),
        [
            ("INVALID", "'INVALID' is not a valid HealthStatusType"),
            ("normal", "'normal' is not a valid HealthStatusType"),  # lowercase is invalid
            ("", "'' is not a valid HealthStatusType"),
        ],
    )
    def test_constructor_invalid_cases(
        self, input_value: str, error_message: str
    ) -> None:
        """Test that ValueError is raised for invalid input values."""
        with pytest.raises(ValueError, match=error_message):
            HealthStatusType(input_value)

    def test_constructor_with_none_raises_error(self) -> None:
        """Test that ValueError is raised when None is input."""
        with pytest.raises(ValueError, match="None is not a valid HealthStatusType"):
            HealthStatusType(None)  # type: ignore

    def test_enum_members_are_correct(self) -> None:
        """Verify that Enum members are correctly defined."""
        assert HealthStatusType.NORMAL.value == "NORMAL"
        assert HealthStatusType.BUSY.value == "BUSY"
        assert HealthStatusType.VERY_BUSY.value == "VERY BUSY"
        assert HealthStatusType.SUPER_BUSY.value == "SUPER BUSY"
        assert HealthStatusType.NO_ORDER.value == "NO ORDER"
        assert HealthStatusType.STOP.value == "STOP"
        assert len(HealthStatusType) == 6
