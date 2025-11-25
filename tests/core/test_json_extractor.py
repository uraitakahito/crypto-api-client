"""Tests for _json_extractor module."""

import pytest

from crypto_api_client.core.json_extractor import _JsonExtractor


class TestJsonExtractor:
    """Tests for _JsonExtractor class."""

    def test_extract_object_simple(self):
        """Extract simple object."""
        text = '{"key": "value"}'
        result = _JsonExtractor.extract_object(text)
        assert result == '{"key": "value"}'

    def test_extract_object_from_field(self):
        """Extract object from field value."""
        text = '"data": {"key": "value", "num": 123}'
        result = _JsonExtractor.extract_object(text)
        assert result == '{"key": "value", "num": 123}'

    def test_extract_object_nested(self):
        """Extract nested object."""
        text = '{"outer": {"inner": {"deep": "value"}}}'
        result = _JsonExtractor.extract_object(text)
        assert result == '{"outer": {"inner": {"deep": "value"}}}'

    def test_extract_object_with_array(self):
        """Extract object containing array."""
        text = '{"items": [1, 2, 3], "count": 3}'
        result = _JsonExtractor.extract_object(text)
        assert result == '{"items": [1, 2, 3], "count": 3}'

    def test_extract_object_no_brace(self):
        """Test when opening brace is not found."""
        text = '"key": "value"'
        with pytest.raises(ValueError, match="Opening brace not found"):
            _JsonExtractor.extract_object(text)

    def test_extract_object_unclosed(self):
        """Test when closing brace is not found."""
        text = '{"key": "value"'
        with pytest.raises(ValueError, match="Closing brace not found"):
            _JsonExtractor.extract_object(text)

    def test_extract_field_with_object_simple(self):
        """Extract field and object."""
        text = '{"success": 1, "data": {"value": 123}}'
        result = _JsonExtractor.extract_field_with_object(text, "data")
        assert result == '"data": {"value": 123}'

    def test_extract_field_with_object_whitespace(self):
        """Extract field and object with whitespace."""
        text = '{"success": 1, "data"  :  {"value": 123}}'
        result = _JsonExtractor.extract_field_with_object(text, "data")
        assert result == '"data"  :  {"value": 123}'

    def test_extract_field_with_object_nested(self):
        """Extract field with nested object."""
        text = '{"data": {"nested": {"deep": {"value": 123}}}}'
        result = _JsonExtractor.extract_field_with_object(text, "data")
        assert result == '"data": {"nested": {"deep": {"value": 123}}}'

    def test_extract_field_with_object_not_found(self):
        """Test when field is not found."""
        text = '{"success": 1}'
        with pytest.raises(ValueError, match="Field 'data' not found"):
            _JsonExtractor.extract_field_with_object(text, "data")

    # ========== Tests for extract_array() ==========

    def test_extract_array_simple(self):
        """Extract simple array."""
        text = '[1, 2, 3]'
        result = _JsonExtractor.extract_array(text)
        assert result == '[1, 2, 3]'

    def test_extract_array_from_field(self):
        """Extract array from field value."""
        text = '"items": [{"id": 1}, {"id": 2}]'
        result = _JsonExtractor.extract_array(text)
        assert result == '[{"id": 1}, {"id": 2}]'

    def test_extract_array_nested(self):
        """Extract nested array."""
        text = '[1, [2, [3, 4]], 5]'
        result = _JsonExtractor.extract_array(text)
        assert result == '[1, [2, [3, 4]], 5]'

    def test_extract_array_with_objects(self):
        """Extract array containing objects."""
        text = '[{"key": "value"}, {"nested": {"deep": 123}}]'
        result = _JsonExtractor.extract_array(text)
        assert result == '[{"key": "value"}, {"nested": {"deep": 123}}]'

    def test_extract_array_empty(self):
        """Extract empty array."""
        text = '[]'
        result = _JsonExtractor.extract_array(text)
        assert result == '[]'

    def test_extract_array_with_start_pos(self):
        """Extract array with specified start position."""
        text = '"first": [1, 2], "second": [3, 4]'
        # Start search from "second" position
        start = text.find('"second"')
        result = _JsonExtractor.extract_array(text, start_pos=start)
        assert result == '[3, 4]'

    def test_extract_array_no_bracket(self):
        """Test when opening bracket is not found."""
        text = '"key": "value"'
        with pytest.raises(ValueError, match="Opening bracket not found"):
            _JsonExtractor.extract_array(text)

    def test_extract_array_unclosed(self):
        """Test when closing bracket is not found."""
        text = '[1, 2, 3'
        with pytest.raises(ValueError, match="Closing bracket not found"):
            _JsonExtractor.extract_array(text)

    def test_extract_array_complex_bitbank_response(self):
        """Test with actual bitbank response format data."""
        import json
        text = '''{
            "success": 1,
            "data": {
                "assets": [
                    {"asset": "jpy", "amount": "100000"},
                    {"asset": "btc", "amount": "0.5"}
                ]
            }
        }'''
        # Start search from "assets" field position
        start = text.find('"assets"')
        result = _JsonExtractor.extract_array(text, start_pos=start)
        expected = '''[
                    {"asset": "jpy", "amount": "100000"},
                    {"asset": "btc", "amount": "0.5"}
                ]'''
        # Compare ignoring whitespace
        assert json.loads(result) == json.loads(expected)
