"""Tests for HMAC signature generation."""

from crypto_api_client.security._hmac_signer import sign_message
from tests.common.crypto_test_utils import (
    assert_signatures_different,
    assert_valid_hmac_signature,
)
from tests.common.test_data_factory.signature_factory import SignatureDataFactory


class TestSignMessage:
    """Tests for the sign_message function."""

    def test_generate_hmac_signature_with_valid_inputs(self) -> None:
        """Verify that HMAC-SHA256 signature can be generated with valid inputs."""
        secret = "test_secret_key"
        message = "test_message"

        signature = sign_message(secret, message)

        # Verify using common utility
        assert_valid_hmac_signature(signature)

        # Verify that same inputs generate same signature
        signature2 = sign_message(secret, message)
        assert signature == signature2

    def test_generate_hmac_signature_with_empty_message(self) -> None:
        """Verify that signature can be generated even with empty message."""
        secret = "test_secret_key"
        message = ""

        signature = sign_message(secret, message)

        assert_valid_hmac_signature(signature)

    def test_generate_hmac_signature_with_empty_secret(self) -> None:
        """Verify that signature can be generated even with empty secret key."""
        secret = ""
        message = "test_message"

        signature = sign_message(secret, message)

        assert_valid_hmac_signature(signature)

    def test_signature_consistency(self) -> None:
        """Verify that different inputs generate different signatures."""
        secret = "test_secret_key"

        signature1 = sign_message(secret, "message1")
        signature2 = sign_message(secret, "message2")
        signature3 = sign_message("different_secret", "message1")

        # Verify using common utility
        assert_signatures_different(signature1, signature2, signature3)

    def test_signature_with_special_characters(self) -> None:
        """Verify that signature is correctly generated with special characters."""
        # Get test case from factory
        test_case = SignatureDataFactory.get_test_case("special_characters")

        signature = sign_message(test_case.secret, test_case.message)

        assert_valid_hmac_signature(signature)

    def test_signature_with_known_values(self) -> None:
        """Verify that correct signature is generated for known input values."""
        # Get test case with known values from factory
        test_case = SignatureDataFactory.get_test_case("hmac_doc_example")

        signature = sign_message(test_case.secret, test_case.message)

        assert signature == test_case.expected
        assert_valid_hmac_signature(signature)

    def test_signature_with_long_inputs(self) -> None:
        """Verify that signature is correctly generated even with long inputs."""
        # Get test case with long inputs from factory
        test_case = SignatureDataFactory.get_test_case("long_input")

        signature = sign_message(test_case.secret, test_case.message)

        assert_valid_hmac_signature(signature)

        # Same long inputs generate same signature
        signature2 = sign_message(test_case.secret, test_case.message)
        assert signature == signature2

    def test_signature_case_sensitivity(self) -> None:
        """Verify that different case letters generate different signatures."""
        secret = "Secret"

        signature_lower = sign_message(secret, "message")
        signature_upper = sign_message(secret, "MESSAGE")

        # Verify that different signatures are generated
        assert_signatures_different(signature_lower, signature_upper)
