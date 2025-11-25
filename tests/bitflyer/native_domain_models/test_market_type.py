"""Tests for MarketType Enum constructor"""

import pytest

from crypto_api_client.bitflyer.native_domain_models.market_type import MarketType


class TestMarketTypeConstructor:
    """Test constructor and validation of MarketType Enum."""

    @pytest.mark.parametrize(
        ("input_value", "expected"),
        [
            ("Spot", MarketType.Spot),
            ("FX", MarketType.FX),
        ],
    )
    def test_constructor_valid_cases(
        self, input_value: str, expected: MarketType
    ) -> None:
        """Test that MarketType Enum can be correctly created from valid input values."""
        market_type = MarketType(input_value)
        assert market_type == expected

    @pytest.mark.parametrize(
        ("input_value", "error_message"),
        [
            ("INVALID", "'INVALID' is not a valid MarketType"),
            ("spot", "'spot' is not a valid MarketType"),  # lowercase is invalid
            ("fx", "'fx' is not a valid MarketType"),  # lowercase is invalid
            ("", "'' is not a valid MarketType"),
        ],
    )
    def test_constructor_invalid_cases(
        self, input_value: str, error_message: str
    ) -> None:
        """Test that ValueError is raised for invalid input values."""
        with pytest.raises(ValueError, match=error_message):
            MarketType(input_value)

    def test_constructor_with_none_raises_error(self) -> None:
        """Test that ValueError is raised when None is input."""
        with pytest.raises(ValueError, match="None is not a valid MarketType"):
            MarketType(None)  # type: ignore

    def test_enum_members_are_correct(self) -> None:
        """Verify that Enum members are correctly defined."""
        assert MarketType.Spot.value == "Spot"
        assert MarketType.FX.value == "FX"
        assert len(MarketType) == 2
