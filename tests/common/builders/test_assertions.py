"""Tests for assertion classes."""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

import pytest

from tests.common.builders.assertions import (
    DecimalAssertion,
    EnumAssertion,
    FieldExistsAssertion,
    TimestampAssertion,
)


class SampleEnum(Enum):
    """Sample enum for testing."""

    BUY = "BUY"
    SELL = "SELL"


class SampleResponse:
    """Sample response class for testing."""

    def __init__(self):
        self.price = Decimal("12345.678")
        self.side = SampleEnum.BUY
        self.timestamp = datetime.now(timezone.utc)
        self.nested = {"data": {"value": Decimal("999.99")}}
        self.optional_field = None


class TestDecimalAssertion:
    """Test DecimalAssertion."""

    def test_exact_match(self) -> None:
        """Test exact decimal match."""
        response = SampleResponse()
        assertion = DecimalAssertion("price", Decimal("12345.678"))

        # Should not raise
        assertion.validate(response)

    def test_value_mismatch(self) -> None:
        """Test decimal value mismatch."""
        response = SampleResponse()
        assertion = DecimalAssertion("price", Decimal("12345.679"))

        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "Expected price to be 12345.679" in str(exc_info.value)
        assert "but got 12345.678" in str(exc_info.value)

    def test_precision_check(self) -> None:
        """Test decimal precision validation."""
        response = SampleResponse()
        response.price = Decimal("12345.12345678")  # 8 decimal places

        # Should pass with precision >= 8
        assertion = DecimalAssertion("price", response.price, precision=8)
        assertion.validate(response)

        # Should fail with precision < 8
        assertion = DecimalAssertion("price", response.price, precision=4)
        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "precision <= 4" in str(exc_info.value)
        assert "but got 8" in str(exc_info.value)

    def test_tolerance(self) -> None:
        """Test decimal tolerance."""
        response = SampleResponse()
        response.price = Decimal("100.00")

        # Within tolerance
        assertion = DecimalAssertion(
            "price", Decimal("100.05"), tolerance=Decimal("0.1")
        )
        assertion.validate(response)

        # Outside tolerance
        assertion = DecimalAssertion(
            "price", Decimal("100.15"), tolerance=Decimal("0.1")
        )
        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "±0.1" in str(exc_info.value)

    def test_nested_field(self) -> None:
        """Test nested field access."""
        response = SampleResponse()
        assertion = DecimalAssertion("nested.data.value", Decimal("999.99"))

        assertion.validate(response)

    def test_wrong_type(self) -> None:
        """Test non-decimal field."""
        response = SampleResponse()
        response.price = "12345.678"  # type: ignore[assignment] # String instead of Decimal

        assertion = DecimalAssertion("price", Decimal("12345.678"))

        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "Expected price to be Decimal" in str(exc_info.value)
        assert "but got str" in str(exc_info.value)


class TestEnumAssertion:
    """Test EnumAssertion."""

    def test_enum_match(self) -> None:
        """Test enum value match."""
        response = SampleResponse()

        # Test with enum value
        assertion = EnumAssertion("side", SampleEnum, SampleEnum.BUY)
        assertion.validate(response)

        # Test with string value
        assertion = EnumAssertion("side", SampleEnum, "BUY")
        assertion.validate(response)

    def test_enum_mismatch(self) -> None:
        """Test enum value mismatch."""
        response = SampleResponse()
        assertion = EnumAssertion("side", SampleEnum, SampleEnum.SELL)

        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "Expected side to be SELL" in str(exc_info.value)
        assert "but got BUY" in str(exc_info.value)

    def test_invalid_enum_value(self) -> None:
        """Test invalid enum value."""
        response = SampleResponse()
        response.side = "INVALID"  # type: ignore[assignment]

        assertion = EnumAssertion("side", SampleEnum, "BUY")

        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "valid SampleEnum" in str(exc_info.value)
        assert "invalid value: INVALID" in str(exc_info.value)


class TestFieldExistsAssertion:
    """Test FieldExistsAssertion."""

    def test_field_exists(self) -> None:
        """Test existing field."""
        response = SampleResponse()
        assertion = FieldExistsAssertion("price")

        assertion.validate(response)

    def test_field_not_exists(self) -> None:
        """Test non-existing field."""
        response = SampleResponse()
        assertion = FieldExistsAssertion("non_existent")

        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "Required field 'non_existent' not found" in str(exc_info.value)

    def test_type_check(self) -> None:
        """Test field type validation."""
        response = SampleResponse()

        # Correct type
        assertion = FieldExistsAssertion("price", expected_type=Decimal)
        assertion.validate(response)

        # Wrong type
        assertion = FieldExistsAssertion("price", expected_type=str)
        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "Expected price to be str" in str(exc_info.value)
        assert "but got Decimal" in str(exc_info.value)

    def test_none_handling(self) -> None:
        """Test None value handling."""
        response = SampleResponse()

        # None not allowed (default)
        assertion = FieldExistsAssertion("optional_field")
        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "is None but null values not allowed" in str(exc_info.value)

        # None allowed
        assertion = FieldExistsAssertion("optional_field", allow_none=True)
        assertion.validate(response)


class TestTimestampAssertion:
    """Test TimestampAssertion."""

    def test_datetime_type(self) -> None:
        """Test datetime type validation."""
        response = SampleResponse()
        assertion = TimestampAssertion("timestamp")

        assertion.validate(response)

    def test_timezone_aware(self) -> None:
        """Test timezone awareness check."""
        response = SampleResponse()

        # UTC timezone (should pass)
        assertion = TimestampAssertion("timestamp", timezone_aware=True)
        assertion.validate(response)

        # Naive datetime
        response.timestamp = datetime.now()  # No timezone
        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "Expected timestamp to be timezone-aware" in str(exc_info.value)

    def test_iso8601_format(self) -> None:
        """Test ISO8601 format validation."""
        response = SampleResponse()
        assertion = TimestampAssertion("timestamp", format="ISO8601")

        # Should be able to format as ISO8601
        assertion.validate(response)

    def test_value_match(self) -> None:
        """Test timestamp value matching."""
        response = SampleResponse()
        expected_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        response.timestamp = expected_time

        # Test with datetime object
        assertion = TimestampAssertion("timestamp", expected=expected_time)
        assertion.validate(response)

        # Test with string
        assertion = TimestampAssertion(
            "timestamp", expected="2024-01-01T12:00:00+00:00"
        )
        assertion.validate(response)

    def test_value_mismatch(self) -> None:
        """Test timestamp value mismatch."""
        response = SampleResponse()
        response.timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        assertion = TimestampAssertion(
            "timestamp", expected=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
        )

        with pytest.raises(AssertionError) as exc_info:
            assertion.validate(response)

        assert "Expected timestamp to be" in str(exc_info.value)
        assert "2024-01-01 13:00:00" in str(exc_info.value)
