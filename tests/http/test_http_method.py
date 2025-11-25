"""Tests for HttpMethod."""

from crypto_api_client.http._http_method import HttpMethod


class TestHttpMethod:
    """Tests for HttpMethod Enum."""

    def test_enum_values(self) -> None:
        """Test that Enum values are correctly defined."""
        assert HttpMethod.GET.value == "GET"
        assert HttpMethod.POST.value == "POST"

    def test_enum_members_count(self) -> None:
        """Test that Enum member count is correct."""
        assert len(HttpMethod) == 2

    def test_str_method(self) -> None:
        """Test that __str__ method returns value."""
        assert str(HttpMethod.GET) == "GET"
        assert str(HttpMethod.POST) == "POST"
