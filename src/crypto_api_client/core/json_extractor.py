"""Generic utilities for JSON processing

This module provides functionality for extracting specific parts from JSON strings.
Primarily used in processing exchange API responses.
"""
# pyright: reportUnusedClass=false

from __future__ import annotations

import re


class _JsonExtractor:
    """Internal utility class for extracting specific parts from JSON strings

    Exchange API responses often have nested structures, so we need to
    efficiently extract only specific parts.
    This class centralizes such processing.

    Note: This class is for internal use only. It is not exposed to external APIs.
    """

    @staticmethod
    def extract_object(text: str, start_pos: int = 0) -> str:
        """Extract the first object (part enclosed by {}) from JSON string

        :param text: Text to parse
        :type text: str
        :param start_pos: Search start position (default: 0)
        :type start_pos: int
        :return: Extracted JSON object string
        :rtype: str
        :raises ValueError: If object is not found or braces are invalid

        .. code-block:: python

            >>> text = '"data": {"value": 123, "nested": {"key": "val"}}'
            >>> _JsonExtractor.extract_object(text)
            '{"value": 123, "nested": {"key": "val"}}'
        """
        start = text.find("{", start_pos)
        if start == -1:
            raise ValueError(f"Opening brace not found: {text}")

        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        raise ValueError(f"Closing brace not found: {text}")

    @staticmethod
    def extract_field_with_object(text: str, field_name: str) -> str:
        """Extract a string containing specific field and its object value

        :param text: JSON text to parse
        :type text: str
        :param field_name: Field name to extract
        :type field_name: str
        :return: String in the format "field_name": {...}
        :rtype: str
        :raises ValueError: If field is not found or braces are invalid

        .. code-block:: python

            >>> text = '{"success": 1, "data": {"value": 123}}'
            >>> _JsonExtractor.extract_field_with_object(text, "data")
            '"data": {"value": 123}'
        """
        pattern = re.compile(rf'"{re.escape(field_name)}"\s*:\s*{{')
        match = pattern.search(text)
        if not match:
            raise ValueError(f"Field '{field_name}' not found: {text}")

        start = match.start()
        brace_start = text.find("{", match.end() - 1)
        if brace_start == -1:
            raise ValueError(f"Opening brace not found: {text}")

        # Track nesting of braces
        depth = 0
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        raise ValueError(f"Closing brace not found: {text}")

    @staticmethod
    def extract_array(text: str, start_pos: int = 0) -> str:
        """Extract the first array (part enclosed by []) from JSON string

        :param text: Text to parse
        :type text: str
        :param start_pos: Search start position (default: 0)
        :type start_pos: int
        :return: Extracted JSON array string (including [])
        :rtype: str
        :raises ValueError: If array is not found or brackets are invalid

        Example usage:

        .. code-block:: python

            text = '"data": [{"id": 1}, {"id": 2}]'
            _JsonExtractor.extract_array(text)
            # '[{"id": 1}, {"id": 2}]'

            text = '{"items": [1, 2, [3, 4]], "count": 4}'
            _JsonExtractor.extract_array(text)
            # '[1, 2, [3, 4]]'
        """
        start = text.find("[", start_pos)
        if start == -1:
            raise ValueError(f"Opening bracket not found: {text}")

        depth = 0
        for i in range(start, len(text)):
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        raise ValueError(f"Closing bracket not found: {text}")
