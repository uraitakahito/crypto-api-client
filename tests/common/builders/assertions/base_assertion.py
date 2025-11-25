"""Base assertion interface."""

from abc import ABC, abstractmethod
from typing import Any


class Assertion(ABC):
    """Base class for all assertions.

    Assertions validate specific properties of API responses.
    """

    @abstractmethod
    def validate(self, response: Any) -> None:
        """Validate the response.

        Args:
            response: API response object to validate

        Raises:
            AssertionError: If validation fails
        """
        pass

    def get_field_value(self, obj: Any, field_path: str) -> Any:
        """Get value from object using dot-separated field path.

        Args:
            obj: Object to extract value from
            field_path: Dot-separated path (e.g., "data.ticker.price")

        Returns:
            Field value

        Raises:
            AssertionError: If field not found
        """
        value: Any = obj
        parts = field_path.split(".")

        for part in parts:
            if hasattr(value, part):  # pyright: ignore[reportUnknownArgumentType]
                value = getattr(value, part, None)  # pyright: ignore[reportUnknownArgumentType]
            elif isinstance(value, dict) and part in value:
                value = value[part]  # type: ignore[index]
            else:
                raise AssertionError(
                    f"Field '{field_path}' not found in response. Failed at '{part}'"
                )

        return value  # pyright: ignore[reportUnknownVariableType]
