"""Tests for Payload base class"""


from crypto_api_client._base import Payload


class TestPayloadDefaultBehavior:
    """Test Payload default behavior"""

    def test_identity_transformation(self):
        """Default implementation returns JSON string as-is"""
        json_str = '{"key": "value"}'
        payload = Payload(json_str)

        assert payload.content_str == json_str

    def test_raw_json_property(self):
        """raw_json property returns original JSON string"""
        json_str = '{"key": "value"}'
        payload = Payload(json_str)

        assert payload.raw_json == json_str

    def test_content_str_and_raw_json_are_same_for_default(self):
        """In default implementation, content_str and raw_json are the same"""
        json_str = '{"key": "value"}'
        payload = Payload(json_str)

        assert payload.content_str == payload.raw_json

    def test_handles_complex_json(self):
        """Can handle complex JSON structures correctly"""
        json_str = '{"nested": {"key": "value"}, "array": [1, 2, 3]}'
        payload = Payload(json_str)

        assert payload.content_str == json_str
        assert payload.raw_json == json_str


class TestPayloadInheritance:
    """Test Payload inheritance behavior"""

    def test_simple_inheritance(self):
        """Simple inheritance uses default implementation"""

        class SimplePayload(Payload):
            pass

        json_str = '{"test": 123}'
        payload = SimplePayload(json_str)

        assert payload.content_str == json_str
        assert payload.raw_json == json_str

    def test_override_content_str(self):
        """Can override content_str"""

        class CustomPayload(Payload):
            @property
            def content_str(self) -> str:
                return "custom"

        json_str = '{"test": 123}'
        payload = CustomPayload(json_str)

        assert payload.content_str == "custom"
        assert payload.raw_json == json_str  # raw_json remains unchanged

    def test_content_str_with_extraction(self):
        """Can implement extraction logic in content_str"""

        class ExtractingPayload(Payload):
            @property
            def content_str(self) -> str:
                # Simple extraction logic (for testing)
                return self._json_str.replace('"data": ', "")

        json_str = '"data": {"key": "value"}'
        payload = ExtractingPayload(json_str)

        assert payload.content_str == '{"key": "value"}'
        assert payload.raw_json == json_str


class TestPayloadEdgeCases:
    """Test Payload edge cases"""

    def test_empty_json_string(self):
        """Can handle empty JSON string"""
        json_str = ""
        payload = Payload(json_str)

        assert payload.content_str == ""
        assert payload.raw_json == ""

    def test_json_with_unicode(self):
        """Can handle JSON string with Unicode characters"""
        json_str = '{"message": "Hello World 🌍"}'
        payload = Payload(json_str)

        assert payload.content_str == json_str
        assert payload.raw_json == json_str

    def test_json_with_special_characters(self):
        """Can handle JSON string with special characters"""
        json_str = '{"message": "Line1\\nLine2\\tTabbed"}'
        payload = Payload(json_str)

        assert payload.content_str == json_str
        assert payload.raw_json == json_str
