"""Tests for SecretHeaders class"""

import httpx

from crypto_api_client.security.secret_headers import SecretHeaders


class TestSecretHeaders:
    """Test class for SecretHeaders class"""

    def test_masking_sensitive_headers(self):
        """Verify that sensitive headers are masked"""
        headers = SecretHeaders(
            {
                "ACCESS-KEY": "sk-1234567890abcdef",
                "ACCESS-SIGN": "signature_value_123456",
                "API-KEY": "apikey123456789",
                "Content-Type": "application/json",
            }
        )

        # Masked in __str__
        str_repr = str(headers)
        assert "sk-********" in str_repr
        assert "sig********" in str_repr
        assert "api********" in str_repr
        assert "application/json" in str_repr  # Non-sensitive headers remain unchanged

        # Also masked in get_masked_dict()
        masked = headers.get_masked_dict()
        assert masked["ACCESS-KEY"] == "sk-********"
        assert masked["ACCESS-SIGN"] == "sig********"
        assert masked["API-KEY"] == "api********"
        assert masked["Content-Type"] == "application/json"

    def test_preserving_non_sensitive_headers(self):
        """Verify that non-sensitive headers are preserved"""
        headers = SecretHeaders(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "crypto-api-client/1.0",
                "X-Request-ID": "abc123",
            }
        )

        # All preserved
        str_repr = str(headers)
        assert "application/json" in str_repr
        assert "crypto-api-client/1.0" in str_repr
        assert "abc123" in str_repr

        # Actual values are accessible
        assert headers["Content-Type"] == "application/json"
        assert headers["User-Agent"] == "crypto-api-client/1.0"

    def test_httpx_headers_conversion(self):
        """Verify that conversion to httpx.Headers works correctly"""
        headers = SecretHeaders(
            {"ACCESS-KEY": "secret_key_123", "Content-Type": "application/json"}
        )

        # Convert to httpx.Headers (actual values preserved)
        httpx_headers = headers.to_httpx_headers()
        assert isinstance(httpx_headers, httpx.Headers)
        assert httpx_headers["ACCESS-KEY"] == "secret_key_123"
        assert httpx_headers["Content-Type"] == "application/json"

    def test_string_representation(self):
        """Verify that string representation is masked"""
        headers = SecretHeaders(
            {"Authorization": "Bearer token123456789", "X-API-KEY": "xapikey987654321"}
        )

        # Masked in __str__ and __repr__
        str_repr = str(headers)
        repr_repr = repr(headers)

        assert "Bea********" in str_repr
        assert "xap********" in str_repr
        assert "SecretHeaders(" in repr_repr
        assert "Bea********" in repr_repr

    def test_case_insensitive_detection(self):
        """Verify case-insensitive detection"""
        # Headers with different cases are treated as the same
        headers1 = SecretHeaders({"access-key": "lowercase_key"})
        headers2 = SecretHeaders({"Access-Key": "mixedcase_key"})
        headers3 = SecretHeaders({"ACCESS-KEY": "uppercase_key"})

        # All masked
        assert "low********" in str(headers1)
        assert "mix********" in str(headers2)
        assert "upp********" in str(headers3)

        # When setting the same header with different cases, the last one is used
        headers = SecretHeaders()
        headers["access-key"] = "first"
        headers["Access-Key"] = "second"  # Same header (different case)
        headers["ACCESS-KEY"] = "third"  # Same header (different case)

        # Last value is preserved
        assert headers["access-key"] == "third"
        assert headers["Access-Key"] == "third"
        assert headers["ACCESS-KEY"] == "third"

    def test_short_values(self):
        """Test masking of short values"""
        headers = SecretHeaders(
            {
                "API-KEY": "ab",  # 3 characters or less
                "ACCESS-KEY": "abc",  # Exactly 3 characters
                "X-API-KEY": "abcd",  # 4 characters
            }
        )

        masked = headers.get_masked_dict()
        assert masked["API-KEY"] == "**********"  # 3 characters or less: fully masked
        assert masked["ACCESS-KEY"] == "**********"  # 3 characters or less: fully masked
        assert masked["X-API-KEY"] == "abc********"  # 4 characters or more: first 3 characters

    def test_mutable_mapping_operations(self):
        """Verify MutableMapping protocol operations"""
        headers = SecretHeaders()

        # Set
        headers["Content-Type"] = "application/json"
        headers["API-KEY"] = "test_key_123"
        assert len(headers) == 2

        # Get
        assert headers["Content-Type"] == "application/json"
        assert headers["API-KEY"] == "test_key_123"

        # Existence check
        assert "Content-Type" in headers
        assert "API-KEY" in headers
        assert "Not-Exists" not in headers

        # Delete
        del headers["Content-Type"]
        assert len(headers) == 1
        assert "Content-Type" not in headers

        # Iteration
        headers["Another-Header"] = "value"
        keys = list(headers)
        assert "API-KEY" in keys
        assert "Another-Header" in keys

    def test_update_method(self):
        """Test update method (MutableMapping compliant)"""
        headers = SecretHeaders({"Content-Type": "text/plain"})

        # Update with dict
        headers.update({"Content-Type": "application/json", "API-KEY": "new_key"})
        assert headers["Content-Type"] == "application/json"
        assert headers["API-KEY"] == "new_key"

        # Update with keyword arguments
        headers.update(Accept="application/json")
        assert headers["Accept"] == "application/json"

        # Update with iterable
        headers.update([("X-Custom-1", "value1"), ("X-Custom-2", "value2")])
        assert headers["X-Custom-1"] == "value1"
        assert headers["X-Custom-2"] == "value2"

        # Update with httpx.Headers (converted with dict())
        httpx_headers = httpx.Headers({"X-Custom": "value"})
        headers.update(dict(httpx_headers))
        assert headers["X-Custom"] == "value"

    def test_copy_method(self):
        """Test copy method"""
        original = SecretHeaders(
            {"API-KEY": "original_key", "Content-Type": "application/json"}
        )

        copied = original.copy()

        # Same content
        assert copied["API-KEY"] == original["API-KEY"]
        assert copied["Content-Type"] == original["Content-Type"]

        # Different instance
        assert copied is not original

        # Changes don't affect original
        copied["API-KEY"] = "modified_key"
        assert original["API-KEY"] == "original_key"

    def test_update_from_httpx_method(self):
        """Test update_from_httpx method"""
        headers = SecretHeaders({"Content-Type": "text/plain"})

        # Update from httpx.Headers
        httpx_headers = httpx.Headers({"X-Custom": "value", "Accept": "text/html"})
        headers.update_from_httpx(httpx_headers)
        assert headers["X-Custom"] == "value"
        assert headers["Accept"] == "text/html"

        # Combination of httpx.Headers and keyword arguments
        httpx_headers2 = httpx.Headers({"X-Another": "value2"})
        headers.update_from_httpx(httpx_headers2, Authorization="Bearer token")
        assert headers["X-Another"] == "value2"
        assert headers["Authorization"] == "Bearer token"

        # Verify that sensitive information is correctly masked
        masked = headers.get_masked_dict()
        assert "***" in masked["Authorization"]  # Masked

    def test_equality(self):
        """Test equality comparison"""
        headers1 = SecretHeaders({"API-KEY": "key1", "Content-Type": "json"})
        headers2 = SecretHeaders({"API-KEY": "key1", "Content-Type": "json"})
        headers3 = SecretHeaders({"API-KEY": "key2", "Content-Type": "json"})

        # Between SecretHeaders
        assert headers1 == headers2
        assert headers1 != headers3

        # Comparison with dict
        assert headers1 == {"API-KEY": "key1", "Content-Type": "json"}
        assert headers1 != {"API-KEY": "key2", "Content-Type": "json"}

        # Comparison with httpx.Headers
        httpx_headers = httpx.Headers({"API-KEY": "key1", "Content-Type": "json"})
        assert headers1 == httpx_headers

    def test_from_dict_factory(self):
        """Test from_dict factory method"""
        headers = SecretHeaders.from_dict(
            {"API-KEY": "test_key", "Content-Type": "application/json"}
        )

        assert isinstance(headers, SecretHeaders)
        assert headers["API-KEY"] == "test_key"
        assert headers["Content-Type"] == "application/json"

    def test_from_httpx_headers_factory(self):
        """Test from_httpx_headers factory method"""
        httpx_headers = httpx.Headers(
            {"API-KEY": "test_key", "Content-Type": "application/json"}
        )

        headers = SecretHeaders.from_httpx_headers(httpx_headers)

        assert isinstance(headers, SecretHeaders)
        assert headers["API-KEY"] == "test_key"
        assert headers["Content-Type"] == "application/json"

    def test_binance_specific_headers(self):
        """Test Binance-specific header masking"""
        headers = SecretHeaders({"X-MBX-APIKEY": "binance_api_key_123456"})

        masked = headers.get_masked_dict()
        assert masked["X-MBX-APIKEY"] == "bin********"

    def test_authorization_bearer_token(self):
        """Test Authorization header Bearer token masking"""
        headers = SecretHeaders(
            {
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
            }
        )

        masked = headers.get_masked_dict()
        # Only show first 3 characters of Bearer token
        assert masked["Authorization"].startswith("Bea********")
