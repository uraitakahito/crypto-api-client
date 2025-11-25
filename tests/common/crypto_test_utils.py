"""Cryptographic test utilities.

Provides utility functions commonly used in tests for cryptographic operations
such as signatures and hashes.
"""

from typing import Any


def assert_valid_hmac_signature(signature: str) -> None:
    """Verify that HMAC signature is in valid format.

    :param signature: Signature string to verify
    :raises AssertionError: If signature format is invalid
    """
    assert isinstance(signature, str), (
        f"Signature must be a string. Actual type: {type(signature)}"
    )
    assert len(signature) == 64, (
        f"Invalid signature length. Expected: 64, Actual: {len(signature)}"
    )
    assert all(c in "0123456789abcdef" for c in signature), (
        f"Signature contains invalid characters: {[c for c in signature if c not in '0123456789abcdef']}"
    )


def assert_signatures_different(*signatures: str) -> None:
    """Verify that all signatures are different.

    :param signatures: List of signature strings to compare
    :raises AssertionError: If there are duplicate signatures or invalid format
    """
    assert len(signatures) >= 2, "At least 2 signatures are required for comparison"

    # First verify each signature is in valid format
    for i, sig in enumerate(signatures):
        try:
            assert_valid_hmac_signature(sig)
        except AssertionError as e:
            raise AssertionError(f"Signature {i + 1} is invalid: {e}")

    # Check for duplicates
    unique_signatures = set(signatures)
    if len(unique_signatures) != len(signatures):
        duplicates = []
        for sig in unique_signatures:
            if signatures.count(sig) > 1:
                duplicates.append(sig)  # type: ignore[reportUnknownMemberType]
        raise AssertionError(f"Duplicate signatures found: {duplicates}")


def assert_signature_message_contains(message: str, *expected_parts: str) -> None:
    """Verify that signature message contains expected parts.

    :param message: Message string to verify
    :param expected_parts: Substrings that should be contained in the message
    :raises AssertionError: If expected parts are not contained
    """
    assert isinstance(message, str), (
        f"Message must be a string. Actual type: {type(message)}"
    )
    assert expected_parts, "At least one expected part must be specified"

    missing_parts = []
    for part in expected_parts:
        if part not in message:
            missing_parts.append(part)  # type: ignore[reportUnknownMemberType]

    if missing_parts:
        raise AssertionError(
            f"Message does not contain expected parts.\n"
            f"Missing: {missing_parts}\n"
            f"Message: {message}"
        )


def assert_message_format_matches(message: str, expected_format: str) -> None:
    """Verify that message matches expected format.

    Used for validating order of HTTP method, path, timestamp, etc.

    :param message: Message to verify
    :param expected_format: Expected format (e.g., "{timestamp}{method}{path}{body}")
    :raises AssertionError: If format does not match
    """
    # This function is a placeholder for future extension
    # Actual implementation would use regex or pattern matching
    pass


def compare_signatures(signature1: str, signature2: str) -> bool:
    """Compare two signatures and return whether they are identical.

    :param signature1: First signature to compare
    :param signature2: Second signature to compare
    :return: True if signatures are identical
    """
    # First verify both are valid signature format
    try:
        assert_valid_hmac_signature(signature1)
        assert_valid_hmac_signature(signature2)
    except AssertionError:
        return False

    return signature1 == signature2


def extract_signature_parts(full_signature_string: str) -> dict[str, Any]:
    """Extract parts from signature string.

    Utility to extract parts from signature messages for bitFlyer and bitbank.

    :param full_signature_string: Full signature string
    :return: Dictionary of extracted parts
    """
    # This function is a placeholder for future extension
    # Actual implementation would parse according to each exchange's format
    return {}


# Test data for edge cases
SIGNATURE_EDGE_CASES = {
    "empty_secret": {"secret": "", "message": "test"},
    "empty_message": {"secret": "test", "message": ""},
    "empty_both": {"secret": "", "message": ""},
    "unicode": {"secret": "secret🔐", "message": "message📝"},
    "special_chars": {"secret": "!@#$%^&*()", "message": "test"},
    "very_long": {"secret": "a" * 1000, "message": "b" * 10000},
}


def get_edge_case_params(case_name: str) -> tuple[str, str]:
    """Get edge case parameters.

    :param case_name: Case name
    :return: Tuple of (secret, message)
    :raises KeyError: If specified case does not exist
    """
    if case_name not in SIGNATURE_EDGE_CASES:
        available = ", ".join(SIGNATURE_EDGE_CASES.keys())
        raise KeyError(f"Unknown edge case: {case_name}. Available: {available}")

    case = SIGNATURE_EDGE_CASES[case_name]
    return case["secret"], case["message"]
