"""Timestamp field assertion."""

from datetime import datetime, timezone
from typing import Any, Union

from .base_assertion import Assertion


class TimestampAssertion(Assertion):
    """Assert timestamp field properties."""

    def __init__(
        self,
        field_path: str,
        expected: Union[datetime, str | None] = None,
        format: str | None = None,
        timezone_aware: bool = True,
    ):
        """Initialize timestamp assertion.

        Args:
            field_path: Dot-separated path to field
            expected: Expected timestamp value (optional)
            format: Expected format (e.g., "ISO8601", "RFC3339")
            timezone_aware: Whether timestamp should have timezone info
        """
        self.field_path = field_path
        self.expected = expected
        self.format = format
        self.timezone_aware = timezone_aware

    def validate(self, response: Any) -> None:
        """Validate timestamp field.

        Args:
            response: Response object to validate

        Raises:
            AssertionError: If validation fails
        """
        # Get field value
        value = self.get_field_value(response, self.field_path)

        # Check type
        if not isinstance(value, datetime):
            raise AssertionError(
                f"Expected {self.field_path} to be datetime, "
                f"but got {type(value).__name__}: {value}"
            )

        # Check timezone awareness
        if self.timezone_aware:
            if value.tzinfo is None:
                raise AssertionError(
                    f"Expected {self.field_path} to be timezone-aware, "
                    f"but got naive datetime: {value}"
                )
            # Check if it's UTC
            if value.tzinfo != timezone.utc:
                # Try to get UTC offset
                utc_offset = value.utcoffset()
                if utc_offset is None or utc_offset.total_seconds() != 0:
                    raise AssertionError(
                        f"Expected {self.field_path} to be in UTC, "
                        f"but got timezone: {value.tzinfo}"
                    )
        else:
            if value.tzinfo is not None:
                raise AssertionError(
                    f"Expected {self.field_path} to be timezone-naive, "
                    f"but got aware datetime: {value}"
                )

        # Check format if specified
        if self.format:
            if self.format.upper() == "ISO8601":
                # Check if it can be formatted as ISO8601
                try:
                    iso_str = value.isoformat()
                    # Basic validation - should contain 'T' and timezone info
                    if "T" not in iso_str:
                        raise AssertionError(
                            f"Timestamp {self.field_path} not in ISO8601 format"
                        )
                except Exception as e:
                    raise AssertionError(
                        f"Failed to format {self.field_path} as ISO8601: {e}"
                    )

        # Check value if specified
        if self.expected is not None:
            if isinstance(self.expected, str):
                # Parse expected string to datetime
                expected_dt = datetime.fromisoformat(
                    self.expected.replace("Z", "+00:00")
                )
            else:
                expected_dt = self.expected

            if value != expected_dt:
                raise AssertionError(
                    f"Expected {self.field_path} to be {expected_dt}, but got {value}"
                )
