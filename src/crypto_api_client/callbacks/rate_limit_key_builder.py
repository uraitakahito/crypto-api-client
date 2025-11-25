from __future__ import annotations

import hashlib
import re
import time
from collections.abc import Sequence


class RateLimitKeyBuilder:
    """Redis key generation utility for rate limiters"""

    @staticmethod
    def build_key(
        key_prefix: str, label: str, window_seconds: int, timestamp: int | None = None
    ) -> str:
        now = timestamp if timestamp is not None else int(time.time())
        window = now // window_seconds
        return f"{key_prefix}:{label}:WINDOW:{window}".upper()

    @staticmethod
    def generate_label_from_patterns(
        url_patterns: Sequence[str | re.Pattern[str]],
    ) -> str:
        """Generate label from list of URL patterns

        :param url_patterns: List of URL patterns (strings or regex patterns)
        :return: Generated label (e.g., "PATTERN_12345678")

        The same pattern set always generates the same label.
        """
        # Convert Pattern objects to strings
        patterns = [p.pattern if isinstance(p, re.Pattern) else p for p in url_patterns]
        # Sort to ensure consistency
        patterns_str = ",".join(sorted(patterns))

        hash_digest = hashlib.sha1(patterns_str.encode("utf-8")).hexdigest()[:8]
        return f"PATTERN_{hash_digest}"

    @staticmethod
    def get_window_for_timestamp(timestamp: int, window_seconds: int) -> int:
        """Calculate window number from timestamp

        :param timestamp: UNIX timestamp
        :param window_seconds: Window duration in seconds
        :return: Window number

        Example:
            >>> RateLimitKeyBuilder.get_window_for_timestamp(1609459200, 300)
            5364864
        """
        return timestamp // window_seconds

    @staticmethod
    def parse_key(key: str) -> dict[str, str | int] | None:
        """Parse Redis key to get its components

        :param key: Redis key
        :return: Dictionary of parsed results, or None if cannot parse

        Example:
            >>> RateLimitKeyBuilder.parse_key(
            ...     "RATE_LIMIT:URL_PATTERN:GENERAL:WINDOW:5364864"
            ... )
            {
                'prefix': 'RATE_LIMIT:URL_PATTERN',
                'label': 'GENERAL',
                'window': 5364864
            }
        """
        parts = key.upper().split(":")
        # Need at least 4 parts: PREFIX:LABEL:WINDOW:number
        if len(parts) >= 4:
            # Verify second-to-last is "WINDOW"
            window_index = -1
            for i in range(len(parts) - 1, 0, -1):
                if parts[i - 1] == "WINDOW":
                    window_index = i
                    break

            if window_index > 0:
                try:
                    window = int(parts[window_index])
                    # Parse parts before WINDOW:number
                    # First part is prefix, part before WINDOW is label
                    prefix_and_label_parts = parts[: window_index - 1]

                    if len(prefix_and_label_parts) >= 2:
                        # Account for labels containing multiple colons
                        # Identify PREFIX part (up to first colon, or specific pattern)
                        # For simplicity, treat first two as prefix
                        if "URL_PATTERN" in parts[1]:
                            # RATE_LIMIT:URL_PATTERN format
                            prefix = ":".join(parts[:2])
                            label = ":".join(parts[2 : window_index - 1])
                        else:
                            # Other formats (first one is prefix)
                            prefix = parts[0]
                            label = ":".join(parts[1 : window_index - 1])

                        return {"prefix": prefix, "label": label, "window": window}
                except (ValueError, IndexError):
                    return None
        return None

    @staticmethod
    def build_search_pattern(
        key_prefix: str, label: str | None = None, window: int | None = None
    ) -> str:
        """Generate pattern for Redis search

        :param key_prefix: Key prefix (e.g., "RATE_LIMIT:URL_PATTERN")
        :param label: Label (matches all labels if omitted)
        :param window: Window number (matches all windows if omitted)
        :return: Pattern for Redis KEYS/SCAN (uppercase)

        Examples:
            >>> RateLimitKeyBuilder.build_search_pattern("RATE_LIMIT:URL_PATTERN")
            'RATE_LIMIT:URL_PATTERN:*:WINDOW:*'

            >>> RateLimitKeyBuilder.build_search_pattern(
            ...     "RATE_LIMIT:URL_PATTERN",
            ...     label="GENERAL"
            ... )
            'RATE_LIMIT:URL_PATTERN:GENERAL:WINDOW:*'

            >>> RateLimitKeyBuilder.build_search_pattern(
            ...     "RATE_LIMIT:URL_PATTERN",
            ...     window=5364864
            ... )
            'RATE_LIMIT:URL_PATTERN:*:WINDOW:5364864'

            >>> RateLimitKeyBuilder.build_search_pattern(
            ...     "RATE_LIMIT:URL_PATTERN",
            ...     label="TICKER",
            ...     window=5364864
            ... )
            'RATE_LIMIT:URL_PATTERN:TICKER:WINDOW:5364864'
        """
        label_part = label if label is not None else "*"
        window_part = str(window) if window is not None else "*"
        return f"{key_prefix}:{label_part}:WINDOW:{window_part}".upper()
