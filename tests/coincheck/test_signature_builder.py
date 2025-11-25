"""Coincheck signature builder tests"""

from pydantic import SecretStr
from yarl import URL

from crypto_api_client.coincheck._signature_builder import build_message
from crypto_api_client.security._hmac_signer import sign_message


class TestSignatureBuilder:
    """Tests for signature message construction"""

    def test_build_message_basic(self):
        """Basic message construction test"""
        nonce = "1640000000000"
        api_endpoint = URL("https://coincheck.com/api/accounts/balance")
        body = ""

        message = build_message(nonce, api_endpoint, body)

        # Message format: nonce + api_endpoint + body
        expected = "1640000000000https://coincheck.com/api/accounts/balance"
        assert message == expected

    def test_build_message_with_body(self):
        """Message construction test with request body"""
        nonce = "1640000000000"
        api_endpoint = URL("https://coincheck.com/api/exchange/orders")
        body = '{"pair":"btc_jpy","order_type":"buy","rate":"1000000","amount":"0.001"}'

        message = build_message(nonce, api_endpoint, body)

        expected = (
            "1640000000000https://coincheck.com/api/exchange/orders"
            + '{"pair":"btc_jpy","order_type":"buy","rate":"1000000","amount":"0.001"}'
        )
        assert message == expected

    def test_build_message_with_leading_slash(self):
        """Verify that api_endpoint is correctly processed as a complete URL"""
        nonce = "1640000000000"
        # Specify complete URL directly
        api_endpoint = URL("https://coincheck.com/api/accounts/balance")
        body = ""

        message = build_message(nonce, api_endpoint, body)

        # Verify that complete URL is correctly processed
        expected = "1640000000000https://coincheck.com/api/accounts/balance"
        assert message == expected

    def test_build_message_deterministic(self):
        """Verify that same input produces same message"""
        nonce = "1640000000000"
        api_endpoint = URL("https://coincheck.com/api/accounts/balance")
        body = ""

        message1 = build_message(nonce, api_endpoint, body)
        message2 = build_message(nonce, api_endpoint, body)

        assert message1 == message2

    def test_build_message_different_nonces(self):
        """Verify that different nonces produce different messages"""
        api_endpoint = URL("https://coincheck.com/api/accounts/balance")
        body = ""

        message1 = build_message("1640000000000", api_endpoint, body)
        message2 = build_message("1640000000001", api_endpoint, body)

        # Different nonces should produce different messages
        assert message1 != message2

    def test_signature_generation_with_build_message(self):
        """Signature generation test combining build_message and sign_message"""
        api_secret = SecretStr("test-secret-key")
        nonce = "1640000000000"
        api_endpoint = URL("https://coincheck.com/api/accounts/balance")
        body = ""

        # Build message
        message = build_message(nonce, api_endpoint, body)

        # Generate signature
        signature = sign_message(api_secret, message)

        # Verify signature is a hex string
        assert isinstance(signature, str)
        assert len(signature) > 0
        # HMAC-SHA256 result is 64 characters (256 bits)
        assert len(signature) == 64

    def test_signature_deterministic(self):
        """Verify that same input produces same signature"""
        api_secret = SecretStr("test-secret-key")
        nonce = "1640000000000"
        api_endpoint = URL("https://coincheck.com/api/accounts/balance")
        body = ""

        message1 = build_message(nonce, api_endpoint, body)
        signature1 = sign_message(api_secret, message1)

        message2 = build_message(nonce, api_endpoint, body)
        signature2 = sign_message(api_secret, message2)

        assert signature1 == signature2
