"""Factory and builders for signature testing

Provides Factory and Builder classes for test data used in signature-related tests.
"""

from dataclasses import dataclass
from typing import Any, ClassVar

from yarl import URL

from .base import BaseTestDataBuilder, TestDataConfig


@dataclass
class SignatureTestCase:
    """Signature test case."""

    secret: str
    message: str
    expected: str | None
    description: str


class SignatureDataFactory:
    """Factory for signature test data.

    Manages known signature values and test cases.
    """

    KNOWN_SIGNATURES: ClassVar[dict[str, SignatureTestCase]] = {
        "hmac_doc_example": SignatureTestCase(
            secret="1bdf1e786b748ffd9f747f1b6abd43abf1939db740541e26b9c2c0e151690923",
            message="value",
            expected="3a97c3c68815ffa3a7fcdca9a67a6d106d7fc6dde79c96c1515b2b6acf16cc48",
            description="Example from official documentation",
        ),
        "empty_secret": SignatureTestCase(
            secret="",
            message="test_message",
            expected=None,  # Computed dynamically
            description="Empty secret key",
        ),
        "empty_message": SignatureTestCase(
            secret="test_secret",
            message="",
            expected=None,  # Computed dynamically
            description="Empty message",
        ),
        "special_characters": SignatureTestCase(
            secret="SecretKey🔐",
            message="Message📝 with special chars: !@#$%^&*()",
            expected=None,  # Computed dynamically
            description="Case with special characters",
        ),
        "long_input": SignatureTestCase(
            secret="a" * 1000,
            message="b" * 10000,
            expected=None,  # Computed dynamically
            description="Long input values",
        ),
    }

    @classmethod
    def get_test_case(cls, name: str) -> SignatureTestCase:
        """Get test case by name.

        :param name: Test case name
        :return: Signature test case
        :raises KeyError: If the specified test case name does not exist
        """
        if name not in cls.KNOWN_SIGNATURES:
            available = ", ".join(cls.KNOWN_SIGNATURES.keys())
            raise KeyError(f"Unknown test case: {name}. Available: {available}")
        return cls.KNOWN_SIGNATURES[name]

    @classmethod
    def get_all_test_cases(cls) -> dict[str, SignatureTestCase]:
        """Get all test cases."""
        return cls.KNOWN_SIGNATURES.copy()


class BitFlyerSignatureBuilder(BaseTestDataBuilder):
    """Builder for bitFlyer signature parameters.

    Constructs parameters required for bitFlyer REST API signature generation.
    """

    def __init__(self, config: TestDataConfig | None = None):
        super().__init__(config)

    def _initialize_defaults(self) -> None:
        """Initialize default values."""
        self._data = {
            "api_secret": "test_secret",
            "method": "GET",
            "stub_path": URL("v1"),
            "relative_resource_path": URL("ticker"),
            "params": None,
            "timestamp": "2025-01-01 00:00:00.000000",
        }

    def with_api_secret(self, api_secret: str) -> "BitFlyerSignatureBuilder":
        """Set API secret."""
        return self._set_field("api_secret", api_secret)

    def with_post_method(self) -> "BitFlyerSignatureBuilder":
        """Set to POST method."""
        return self._set_field("method", "POST")

    def with_get_method(self) -> "BitFlyerSignatureBuilder":
        """Set to GET method."""
        return self._set_field("method", "GET")

    def with_method(self, method: str) -> "BitFlyerSignatureBuilder":
        """Set HTTP method."""
        return self._set_field("method", method)

    def with_stub_path(self, stub_path: str | URL) -> "BitFlyerSignatureBuilder":
        """Set stub path."""
        path = URL(stub_path) if isinstance(stub_path, str) else stub_path
        return self._set_field("stub_path", path)

    def with_relative_resource_path(
        self, relative_resource_path: str | URL
    ) -> "BitFlyerSignatureBuilder":
        """Set relative resource path."""
        path = URL(relative_resource_path) if isinstance(relative_resource_path, str) else relative_resource_path
        return self._set_field("relative_resource_path", path)

    def with_params(self, params: dict[str, str] | None) -> "BitFlyerSignatureBuilder":
        """Set parameters."""
        return self._set_field("params", params)

    def with_timestamp(self, timestamp: str) -> "BitFlyerSignatureBuilder":
        """Set timestamp."""
        return self._set_field("timestamp", timestamp)

    def build(self) -> dict[str, Any]:
        """Build and return signature parameters."""
        return self._data.copy()


class BitbankSignatureBuilder(BaseTestDataBuilder):
    """Builder for bitbank signature parameters.

    Constructs parameters required for bitbank REST API signature generation.
    """

    def __init__(self, config: TestDataConfig | None = None):
        super().__init__(config)

    def _initialize_defaults(self) -> None:
        """Initialize default values."""
        self._data = {
            "api_secret": "test_secret",
            "stub_path": URL("v1"),
            "relative_resource_path": URL("user/assets"),
            "params": {},
            "request_time": "1751156562472",
            "time_window_millisecond": "5000",
        }

    def with_api_secret(self, api_secret: str) -> "BitbankSignatureBuilder":
        """Set API secret."""
        return self._set_field("api_secret", api_secret)

    def with_stub_path(self, stub_path: str | URL) -> "BitbankSignatureBuilder":
        """Set stub path."""
        path = URL(stub_path) if isinstance(stub_path, str) else stub_path
        return self._set_field("stub_path", path)

    def with_relative_resource_path(self, relative_resource_path: str | URL) -> "BitbankSignatureBuilder":
        """Set relative resource path."""
        path = URL(relative_resource_path) if isinstance(relative_resource_path, str) else relative_resource_path
        return self._set_field("relative_resource_path", path)

    def with_params(self, params: dict[str, str]) -> "BitbankSignatureBuilder":
        """Set parameters."""
        return self._set_field("params", params)

    def with_request_time(self, request_time: str) -> "BitbankSignatureBuilder":
        """Set request time."""
        return self._set_field("request_time", request_time)

    def with_time_window(self, milliseconds: str) -> "BitbankSignatureBuilder":
        """Set time window."""
        return self._set_field("time_window_millisecond", milliseconds)

    def build(self) -> dict[str, Any]:
        """Build and return signature parameters."""
        return self._data.copy()


class SignatureValidator(BaseTestDataBuilder):
    """Class providing validation constants for signatures."""

    # Expected length of HMAC-SHA256 signature
    HMAC_SHA256_LENGTH = 64

    # Valid hexadecimal characters
    VALID_HEX_CHARS = "0123456789abcdef"

    @staticmethod
    def is_valid_hmac_signature(signature: str) -> bool:
        """Check if HMAC signature has valid format."""
        if len(signature) != SignatureValidator.HMAC_SHA256_LENGTH:
            return False
        return all(c in SignatureValidator.VALID_HEX_CHARS for c in signature)
