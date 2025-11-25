"""Common Request test patterns module.

This module provides common patterns used in Request class tests,
reducing test code duplication and providing helpers for consistency.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type

import pytest
from pydantic import ValidationError


class RequestTestPattern:
    """Class providing common patterns for Request tests."""

    @staticmethod
    def test_invalid_product_code_type(
        request_class: Type[object],
        valid_params: Dict[str, Any],
        expected_match: str = "Input should be",
    ) -> None:
        """Generate test for invalid product_code type.

        :param request_class: Request class to test
        :param valid_params: Valid parameters (product_code will be overwritten with invalid value)
        :param expected_match: Expected error message pattern
        :return: test function
        """

        def test_invalid_product_code_type() -> None:
            """Test that ValidationError is raised for invalid type."""
            invalid_params = valid_params.copy()
            invalid_params["product_code"] = "INVALID_JPY"

            with pytest.raises(ValidationError, match=expected_match):
                request_class(**invalid_params)  # type: ignore[arg-type]

        return test_invalid_product_code_type  # type: ignore[return-value]

    @staticmethod
    def test_to_query_params(
        request_class: Type[object],
        test_params: Dict[str, Any],
        expected_params: Dict[str, str],
    ) -> None:
        """Generate test for to_query_params method.

        :param request_class: Request class to test
        :param test_params: Parameters for creating request
        :param expected_params: Expected query parameters
        :return: test function
        """

        def test_to_query_params() -> None:
            """Test to_query_params method."""
            request = request_class(**test_params)
            params = request.to_query_params()  # type: ignore[attr-defined]
            assert params == expected_params

        return test_to_query_params  # type: ignore[return-value]


class BaseRequestTest(ABC):
    """Base class for Request tests."""

    @property
    @abstractmethod
    def request_class(self) -> Type[object]:
        """Request class to test."""
        pass

    @property
    @abstractmethod
    def valid_params(self) -> Dict[str, Any]:
        """Valid parameters."""
        pass

    def get_invalid_product_code_test(self, expected_match: str = "Input should be"):
        """Get test for invalid product_code type."""
        return RequestTestPattern.test_invalid_product_code_type(
            self.request_class, self.valid_params, expected_match
        )

    def get_to_query_params_test(
        self,
        test_params: Dict[str, Any | None] | None = None,
        expected_params: Dict[str, str | None] | None = None,
    ):
        """Get test for to_query_params method."""
        if test_params is None:
            test_params = self.valid_params
        if expected_params is None:
            # Generate default expected values
            request = self.request_class(**test_params)
            expected_params = request.to_query_params()  # type: ignore[attr-defined]

        return RequestTestPattern.test_to_query_params(
            self.request_class,
            test_params,
            expected_params or {},  # type: ignore[arg-type]
        )


class BitflyerRequestTestMixin:
    """Mixin providing common test methods specific to bitFlyer Request."""

    def test_invalid_product_code_type_standard(self) -> None:
        """Standard test for invalid product_code type (for bitFlyer)."""
        # Supports Pydantic's enum validation error message pattern
        test_func = self.get_invalid_product_code_test("Input should be")  # type: ignore[attr-defined]
        test_func()

    def test_to_query_params_standard(self) -> None:
        """Standard test for to_query_params."""
        test_func = self.get_to_query_params_test()  # type: ignore[attr-defined]
        test_func()
