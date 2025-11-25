from __future__ import annotations

from crypto_api_client._base import Payload


class TickerPayload(Payload):
    """Implementation of ticker :term:`native message payload`

    Receives JSON string in '"data": [...]' format from base class (GmoCoinMessage)
    and extracts the array part [...].

    .. code-block:: json

        // Input (payload part):
        "data": [
            {"ask": "15350001", "bid": "15350000", ...}
        ]

        // Output (content_str):
        [
            {"ask": "15350001", "bid": "15350000", ...}
        ]

    .. note::

        GMO Coin API response structure:

        1. Complete response: {"status": 0, "data": [...], "responsetime": "..."}
        2. Payload part (extracted by GmoCoinMessage._extract_payload): "data": [...]
        3. Content (extracted by this class): [...]
    """

    @property
    def content_str(self) -> str:
        """JSON string of :term:`payload content`

        Extracts and returns the array part ``[...]`` from the received ``"data": [...]`` format string.

        :return: JSON string of payload content (array or object)
        :rtype: str
        :raises ValueError: If array or object is not found
        """
        return self._extract_array_or_object(self._json_str)

    @staticmethod
    def _extract_array_or_object(text: str) -> str:
        """Dynamically extract array or object

        Extracts from the first occurrence of ``[`` or ``{`` to the corresponding closing bracket.
        Handles nested structures.

        :param text: Source JSON string
        :type text: str
        :return: Extracted array or object
        :rtype: str
        :raises ValueError: If opening or closing character is not found

        .. note::

            This implementation does not use :class:`~crypto_api_client.core.json_extractor._JsonExtractor`
            but processes with custom logic.
            This is because it handles GMO Coin-specific response format.
        """

        # Find first [ or {
        start_bracket = text.find("[")
        start_brace = text.find("{")

        # Select whichever comes first
        if start_bracket == -1 and start_brace == -1:
            raise ValueError(f"Opening character ([ or {{}}) not found: {text}")

        if start_bracket == -1:
            start = start_brace
            open_char, close_char = "{", "}"
        elif start_brace == -1:
            start = start_bracket
            open_char, close_char = "[", "]"
        else:
            # If both found, select the earlier one
            if start_bracket < start_brace:
                start = start_bracket
                open_char, close_char = "[", "]"
            else:
                start = start_brace
                open_char, close_char = "{", "}"

        # Track nesting depth
        depth = 0
        for i in range(start, len(text)):
            if text[i] == open_char:
                depth += 1
            elif text[i] == close_char:
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]

        raise ValueError(f"Closing character ({close_char}) not found: {text}")
