"""Field value assertion."""

from enum import Enum
from typing import Any

from .base_assertion import Assertion


class FieldValueAssertion(Assertion):
    """Assert that a field has a specific value."""

    def __init__(self, field_path: str, expected_value: Any):
        """Initialize field value assertion.

        Args:
            field_path: Dot-separated path to field
            expected_value: Expected value of field
        """
        self.field_path = field_path
        self.expected_value = expected_value

    def validate(self, response: Any) -> None:
        """Validate field value.

        Args:
            response: Response object to validate

        Raises:
            AssertionError: If validation fails
        """
        try:
            value = self.get_field_value(response, self.field_path)
        except AssertionError:
            # Re-raise with clearer message
            raise AssertionError(
                f"Required field '{self.field_path}' not found in response"
            )

        # Handle Enum comparison by comparing string values
        actual_value = value.value if isinstance(value, Enum) else value
        expected_value = (
            self.expected_value.value
            if isinstance(self.expected_value, Enum)
            else self.expected_value
        )

        if actual_value != expected_value:
            raise AssertionError(
                f"Expected {self.field_path} to be '{expected_value}', "
                f"but got '{actual_value}'"
            )
