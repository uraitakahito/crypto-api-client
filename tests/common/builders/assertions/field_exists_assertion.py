"""Field existence assertion."""

from typing import Any, Type

from .base_assertion import Assertion


class FieldExistsAssertion(Assertion):
    """Assert that a field exists in response."""

    def __init__(
        self,
        field_path: str,
        expected_type: Type[Any] | None = None,
        allow_none: bool = False,
    ):
        """Initialize field existence assertion.

        Args:
            field_path: Dot-separated path to field
            expected_type: Expected type of field (optional)
            allow_none: Whether None values are allowed
        """
        self.field_path = field_path
        self.expected_type = expected_type
        self.allow_none = allow_none

    def validate(self, response: Any) -> None:
        """Validate field exists.

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

        # Check if None is allowed
        if value is None and not self.allow_none:
            raise AssertionError(
                f"Field '{self.field_path}' is None but null values not allowed"
            )

        # Check type if specified
        if self.expected_type is not None and value is not None:
            if not isinstance(value, self.expected_type):
                raise AssertionError(
                    f"Expected {self.field_path} to be {self.expected_type.__name__}, "
                    f"but got {type(value).__name__}"
                )
