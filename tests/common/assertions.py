"""Common assertion helpers for testing.

This module provides convenient assertion functions for working with
Result[Ok, Err] types and common data validation patterns in tests,
making test code more readable and reducing boilerplate.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

import pytest
from pydantic import ValidationError

# Result type assertion functions were removed due to API change to exception-based
# Use standard pytest.raises or assert statements instead


# Common assertion patterns for data validation


def assert_enum_validation(
    actual: Any, expected_enum: Enum, expected_value: str | None = None
) -> None:
    """Assert that an Enum value is correctly validated.

    :param actual: The actual enum value
    :param expected_enum: The expected enum instance
    :param expected_value: Optional expected string value
    :raises AssertionError: If enum validation fails
    """
    assert actual == expected_enum, f"Expected {expected_enum}, got {actual}"
    assert isinstance(actual, type(expected_enum)), (
        f"Expected {type(expected_enum).__name__}, got {type(actual).__name__}"
    )

    if expected_value:
        assert actual.value == expected_value, (
            f"Expected value '{expected_value}', got '{actual.value}'"
        )


def assert_decimal_precision(actual: Any, expected_str: str) -> None:
    """Assert that a Decimal value maintains precision.

    :param actual: The actual decimal value
    :param expected_str: The expected string representation
    :raises AssertionError: If decimal validation fails
    """
    assert isinstance(actual, Decimal), f"Expected Decimal, got {type(actual).__name__}"
    assert str(actual) == expected_str, (
        f"Expected '{expected_str}', got '{str(actual)}'"
    )


def assert_decimal_field(
    actual: Any, expected_value: str | int | float | Decimal
) -> None:
    """Assert that a field is a valid Decimal with expected value.

    :param actual: The actual field value
    :param expected_value: The expected value (converted to Decimal)
    :raises AssertionError: If decimal field validation fails
    """
    assert isinstance(actual, Decimal), f"Expected Decimal, got {type(actual).__name__}"
    expected_decimal = Decimal(str(expected_value))
    assert actual == expected_decimal, f"Expected {expected_decimal}, got {actual}"


def assert_validation_error_with_message(
    model_class: type,
    invalid_data: dict[str, Any],
    expected_message: str,
) -> ValidationError:
    """Assert that a ValidationError is raised with expected message.

    :param model_class: The Pydantic model class
    :param invalid_data: The invalid data that should cause validation error
    :param expected_message: The expected error message substring
    :return: The raised ValidationError
    :raises AssertionError: If validation error is not raised or message doesn't match
    """
    with pytest.raises(ValidationError) as exc_info:
        model_class(**invalid_data)

    error_message = str(exc_info.value)
    assert expected_message in error_message, (
        f"Expected error message to contain '{expected_message}', got '{error_message}'"
    )

    return exc_info.value


def assert_enum_validation_error(enum_class: type[Enum], invalid_value: Any) -> None:
    """Assert that an invalid enum value raises ValueError with correct message.

    :param enum_class: The enum class
    :param invalid_value: The invalid value that should cause error
    :raises AssertionError: If ValueError is not raised or message is incorrect
    """
    with pytest.raises(ValueError) as exc_info:
        enum_class(invalid_value)

    error_message = str(exc_info.value)
    # Handle special case for None value (no quotes around None)
    if invalid_value is None:
        expected_message = f"None is not a valid {enum_class.__name__}"
    else:
        expected_message = f"'{invalid_value}' is not a valid {enum_class.__name__}"

    assert expected_message in error_message, (
        f"Expected error message to contain '{expected_message}', got '{error_message}'"
    )


def assert_response_structure(
    response_data: dict[str, Any],
    expected_keys: set[str],
    optional_keys: set[str] | None = None,
) -> None:
    """Assert that API response has expected structure.

    :param response_data: The response data dictionary
    :param expected_keys: Set of required keys
    :param optional_keys: Set of optional keys
    :raises AssertionError: If response structure is invalid
    """
    assert isinstance(response_data, dict), (
        f"Expected dict, got {type(response_data).__name__}"
    )

    # Check required keys exist
    missing_keys = expected_keys - set(response_data.keys())
    assert not missing_keys, f"Missing required keys: {missing_keys}"

    # Check no unexpected keys (if optional_keys provided)
    if optional_keys is not None:
        all_expected = expected_keys | optional_keys
        unexpected_keys = set(response_data.keys()) - all_expected
        assert not unexpected_keys, f"Unexpected keys found: {unexpected_keys}"


def assert_utc_datetime(actual: Any) -> None:
    """Assert that a value is a UTC datetime.

    :param actual: The actual datetime value
    :raises AssertionError: If datetime validation fails
    """
    assert isinstance(actual, datetime), (
        f"Expected datetime, got {type(actual).__name__}"
    )
    assert actual.tzinfo is not None, "Expected timezone-aware datetime"
    # Note: We don't check for specific UTC here as it might be ZoneInfo("UTC") or timezone.utc
