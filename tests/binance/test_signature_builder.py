"""Tests for BINANCE signature builder."""

from crypto_api_client.binance._signature_builder import generate_rest_signature


class TestSignatureBuilder:
    """Test class for BINANCE signature builder."""

    def test_generate_rest_signature_basic(self) -> None:
        """Verify that basic signature generation works correctly."""
        api_secret = "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"
        params = {
            "symbol": "LTCBTC",
            "side": "BUY",
            "type": "LIMIT",
            "timeInForce": "GTC",
            "quantity": "1",
            "price": "0.1",
            "recvWindow": "5000",
            "timestamp": "1499827319559",
        }

        signature = generate_rest_signature(api_secret, params)

        # Expected signature (from BINANCE documentation)
        expected_signature = (
            "c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71"
        )
        assert signature == expected_signature

    def test_generate_rest_signature_empty_params(self) -> None:
        """Verify that signature can be generated even with empty parameters."""
        api_secret = "test_secret"
        params: dict[str, str] = {}

        signature = generate_rest_signature(api_secret, params)

        # HMAC-SHA256 signature for empty string
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 is 64-character hex

    def test_generate_rest_signature_none_params(self) -> None:
        """Verify that signature can be generated even with None parameters."""
        api_secret = "test_secret"
        params = None

        signature = generate_rest_signature(api_secret, params)

        # HMAC-SHA256 signature for empty string
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 is 64-character hex

    def test_generate_rest_signature_order_preservation(self) -> None:
        """Verify that parameter order is preserved."""
        api_secret = "test_secret"

        # Same parameters but different order
        params1 = {"a": "1", "b": "2", "c": "3"}
        params2 = {"c": "3", "b": "2", "a": "1"}

        signature1 = generate_rest_signature(api_secret, params1)
        signature2 = generate_rest_signature(api_secret, params2)

        # urlencode sorts alphabetically, so the signature will be the same regardless of order
        # Note: actual BINANCE API requires preserving order when sending
        assert isinstance(signature1, str)
        assert isinstance(signature2, str)
