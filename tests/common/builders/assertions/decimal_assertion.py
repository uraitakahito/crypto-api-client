"""Decimal field assertion."""

from decimal import Decimal
from typing import Any

from .base_assertion import Assertion


class DecimalAssertion(Assertion):
    """Assert decimal field value and precision."""

    def __init__(
        self,
        field_path: str,
        expected: str | Decimal,
        precision: int | None = None,
        tolerance: str | Decimal | None = None,
    ):
        """Initialize decimal assertion.

        Args:
            field_path: Dot-separated path to field
            expected: Expected decimal value (as string or Decimal)
            precision: Maximum decimal places (optional)
            tolerance: Allowed difference from expected (optional)
        """
        self.field_path = field_path
        self.expected = Decimal(expected) if isinstance(expected, str) else expected
        self.precision = precision
        self.tolerance = Decimal(tolerance) if isinstance(tolerance, str) else tolerance

    def validate(self, response: Any) -> None:
        """Validate decimal field.

        Args:
            response: Response object to validate

        Raises:
            AssertionError: If validation fails
        """
        # Get field value
        value = self.get_field_value(response, self.field_path)

        # Check type
        if not isinstance(value, Decimal):
            raise AssertionError(
                f"Expected {self.field_path} to be Decimal, "
                f"but got {type(value).__name__}: {value}"
            )

        # Check precision if specified
        if self.precision is not None:
            # Get actual precision (number of decimal places)
            _, _, exponent = value.as_tuple()
            actual_precision = max(0, -int(exponent)) if int(exponent) < 0 else 0

            if actual_precision > self.precision:
                raise AssertionError(
                    f"Expected {self.field_path} to have precision <= {self.precision}, "
                    f"but got {actual_precision} (value: {value})"
                )

        # Check value
        if self.tolerance is not None:
            diff = abs(value - self.expected)
            if diff > self.tolerance:
                raise AssertionError(
                    f"Expected {self.field_path} to be {self.expected} "
                    f"(±{self.tolerance}), but got {value} (diff: {diff})"
                )
        else:
            if value != self.expected:
                raise AssertionError(
                    f"Expected {self.field_path} to be {self.expected}, but got {value}"
                )
