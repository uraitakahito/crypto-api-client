"""Tests for RateLimitKeyBuilder"""

import re

from crypto_api_client.callbacks.rate_limit_key_builder import RateLimitKeyBuilder


class TestRateLimitKeyBuilder:
    """Test class for RateLimitKeyBuilder"""

    def test_build_key(self):
        """Test key generation accuracy"""
        key = RateLimitKeyBuilder.build_key(
            key_prefix="RATE_LIMIT:URL_PATTERN",
            label="GENERAL",
            window_seconds=300,
            timestamp=1609459200,
        )

        # Verify key is converted to uppercase
        assert key == "RATE_LIMIT:URL_PATTERN:GENERAL:WINDOW:5364864"
        assert key.isupper()

    def test_build_key_with_custom_timestamp(self):
        """Test behavior with specified timestamp"""
        # Different timestamps within same window
        key1 = RateLimitKeyBuilder.build_key("PREFIX", "LABEL", 300, timestamp=1000)
        key2 = RateLimitKeyBuilder.build_key("PREFIX", "LABEL", 300, timestamp=1100)

        # Same key because same window
        assert key1 == key2
        assert key1 == "PREFIX:LABEL:WINDOW:3"

        # Timestamp in different window
        key3 = RateLimitKeyBuilder.build_key("PREFIX", "LABEL", 300, timestamp=1300)

        # Different key because different window
        assert key1 != key3
        assert key3 == "PREFIX:LABEL:WINDOW:4"

    def test_build_key_without_timestamp(self):
        """Uses current time when timestamp is omitted"""
        key = RateLimitKeyBuilder.build_key("PREFIX", "LABEL", 300)

        # Verify key is generated
        assert key.startswith("PREFIX:LABEL:WINDOW:")
        assert key.isupper()

    def test_generate_label_from_patterns(self):
        """Test label generation from patterns"""
        patterns = ["api/v1/ticker", "api/v1/markets"]
        label = RateLimitKeyBuilder.generate_label_from_patterns(patterns)

        # Verify label is in expected format
        assert label.startswith("PATTERN_")
        assert len(label) == 16  # "PATTERN_" + 8-character hash

    def test_generate_label_consistency(self):
        """Test that same patterns generate same label"""
        patterns1 = ["pattern1", "pattern2"]
        patterns2 = ["pattern2", "pattern1"]  # Different order

        label1 = RateLimitKeyBuilder.generate_label_from_patterns(patterns1)
        label2 = RateLimitKeyBuilder.generate_label_from_patterns(patterns2)

        # Same label because sorted
        assert label1 == label2

    def test_generate_label_with_regex_patterns(self):
        """Test label generation from regex patterns"""
        patterns = [re.compile(r"api/v1/.*"), "api/v2/ticker"]

        label = RateLimitKeyBuilder.generate_label_from_patterns(patterns)

        assert label.startswith("PATTERN_")
        assert len(label) == 16

    def test_generate_label_with_empty_patterns(self):
        """Test label generation with empty pattern list"""
        label = RateLimitKeyBuilder.generate_label_from_patterns([])

        assert label.startswith("PATTERN_")
        assert len(label) == 16

    def test_get_window_for_timestamp(self):
        """Test window number calculation accuracy"""
        window = RateLimitKeyBuilder.get_window_for_timestamp(
            timestamp=1609459200, window_seconds=300
        )

        assert window == 5364864

        # Boundary value tests
        assert RateLimitKeyBuilder.get_window_for_timestamp(0, 300) == 0
        assert RateLimitKeyBuilder.get_window_for_timestamp(299, 300) == 0
        assert RateLimitKeyBuilder.get_window_for_timestamp(300, 300) == 1
        assert RateLimitKeyBuilder.get_window_for_timestamp(301, 300) == 1

    def test_parse_key(self):
        """Test key parsing"""
        key = "RATE_LIMIT:URL_PATTERN:GENERAL:WINDOW:5364864"
        result = RateLimitKeyBuilder.parse_key(key)

        assert result is not None
        assert result["prefix"] == "RATE_LIMIT:URL_PATTERN"
        assert result["label"] == "GENERAL"
        assert result["window"] == 5364864

    def test_parse_key_with_lowercase(self):
        """Test that lowercase keys can also be parsed"""
        key = "rate_limit:url_pattern:general:window:123"
        result = RateLimitKeyBuilder.parse_key(key)

        assert result is not None
        assert result["prefix"] == "RATE_LIMIT:URL_PATTERN"
        assert result["label"] == "GENERAL"
        assert result["window"] == 123

    def test_parse_key_with_complex_label(self):
        """Test parsing keys with complex labels"""
        key = "PREFIX:LABEL:WITH:COLONS:WINDOW:456"
        result = RateLimitKeyBuilder.parse_key(key)

        assert result is not None
        assert result["prefix"] == "PREFIX"
        assert result["label"] == "LABEL:WITH:COLONS"
        assert result["window"] == 456

    def test_parse_key_invalid_format(self):
        """Invalid format keys return None"""
        # No WINDOW
        assert RateLimitKeyBuilder.parse_key("PREFIX:LABEL:123") is None

        # Not a number
        assert RateLimitKeyBuilder.parse_key("PREFIX:LABEL:WINDOW:ABC") is None

        # Too short
        assert RateLimitKeyBuilder.parse_key("PREFIX") is None

        # Empty string
        assert RateLimitKeyBuilder.parse_key("") is None

    def test_build_key_special_characters(self):
        """Test key generation with labels containing special characters"""
        key = RateLimitKeyBuilder.build_key("PREFIX", "LABEL-123_456", 300, 1000)

        assert key == "PREFIX:LABEL-123_456:WINDOW:3"

    def test_generate_label_deterministic(self):
        """Test that label generation is deterministic"""
        patterns = ["api/v1/ticker", "api/v1/markets", "api/v1/depth"]

        # Same result even with multiple generations
        labels = [
            RateLimitKeyBuilder.generate_label_from_patterns(patterns) for _ in range(5)
        ]

        assert all(label == labels[0] for label in labels)

    def test_build_search_pattern_all(self):
        """Test pattern generation that matches all keys"""
        pattern = RateLimitKeyBuilder.build_search_pattern("RATE_LIMIT:URL_PATTERN")
        assert pattern == "RATE_LIMIT:URL_PATTERN:*:WINDOW:*"

    def test_build_search_pattern_with_label(self):
        """Test pattern generation with label specified"""
        pattern = RateLimitKeyBuilder.build_search_pattern(
            "RATE_LIMIT:URL_PATTERN", label="GENERAL"
        )
        assert pattern == "RATE_LIMIT:URL_PATTERN:GENERAL:WINDOW:*"

    def test_build_search_pattern_with_window(self):
        """Test pattern generation with window specified"""
        pattern = RateLimitKeyBuilder.build_search_pattern(
            "RATE_LIMIT:URL_PATTERN", window=5364864
        )
        assert pattern == "RATE_LIMIT:URL_PATTERN:*:WINDOW:5364864"

    def test_build_search_pattern_with_both(self):
        """Test pattern generation with both label and window specified"""
        pattern = RateLimitKeyBuilder.build_search_pattern(
            "RATE_LIMIT:URL_PATTERN", label="TICKER", window=5364864
        )
        assert pattern == "RATE_LIMIT:URL_PATTERN:TICKER:WINDOW:5364864"

    def test_build_search_pattern_lowercase(self):
        """Test that uppercase pattern is generated even with lowercase input"""
        pattern = RateLimitKeyBuilder.build_search_pattern(
            "rate_limit:url_pattern", label="general"
        )
        assert pattern == "RATE_LIMIT:URL_PATTERN:GENERAL:WINDOW:*"
        assert pattern.isupper()
