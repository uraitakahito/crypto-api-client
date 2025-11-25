"""Enum field assertion."""

from enum import Enum
from typing import Any, Type, Union

from .base_assertion import Assertion


class EnumAssertion(Assertion):
    """Assert enum field value."""

    def __init__(
        self, field_path: str, enum_class: Type[Enum], expected: Union[str, Enum]
    ):
        """Initialize enum assertion.

        Args:
            field_path: Dot-separated path to field
            enum_class: Enum class type
            expected: Expected enum value or string
        """
        self.field_path = field_path
        self.enum_class = enum_class

        # Convert string to enum if needed
        if isinstance(expected, str):
            try:
                self.expected = enum_class(expected)
            except ValueError:
                # Try by name if value doesn't work
                self.expected = enum_class[expected]
        else:
            self.expected = expected

    def validate(self, response: Any) -> None:
        """Validate enum field.

        Args:
            response: Response object to validate

        Raises:
            AssertionError: If validation fails
        """
        # Get field value
        value = self.get_field_value(response, self.field_path)

        # Check if it's the enum class
        if not isinstance(value, self.enum_class):
            # If it's a string, try to convert
            if isinstance(value, str):
                try:
                    value = self.enum_class(value)
                except ValueError:
                    try:
                        value = self.enum_class[value]
                    except KeyError:
                        raise AssertionError(
                            f"Expected {self.field_path} to be valid {self.enum_class.__name__}, "
                            f"but got invalid value: {value}"
                        )
            else:
                raise AssertionError(
                    f"Expected {self.field_path} to be {self.enum_class.__name__}, "
                    f"but got {type(value).__name__}: {value}"
                )

        # Check value
        if value != self.expected:
            raise AssertionError(
                f"Expected {self.field_path} to be {self.expected.value}, "
                f"but got {value.value}"
            )
