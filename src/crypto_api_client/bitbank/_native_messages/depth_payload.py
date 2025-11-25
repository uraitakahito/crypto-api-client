"""Payload processing for order book"""

from __future__ import annotations

from crypto_api_client._base import Payload
from crypto_api_client.core.json_extractor import (
    _JsonExtractor,  # type: ignore[reportPrivateUsage]
)


class DepthPayload(Payload):
    """:term:`native message payload` implementation for order book (Depth).

    This native message payload receives JSON string like the following:

    .. code-block:: json

        "data": {
            "asks": [["15350001", "0.1"], ["15350002", "0.5"]],
            "bids": [["15350000", "0.2"], ["15349999", "0.3"]],
            "timestamp": 1748558090326,
            "sequenceId": "1234567890"
        }

    Extracts ``{...}`` portion from ``"data": {...}``.

    .. note::

        Uses :meth:`~crypto_api_client.core.json_extractor._JsonExtractor.extract_object`
        to extract object.
    """

    @property
    def content_str(self) -> str:
        """:term:`payload content` JSON string

        Extracts ``{...}`` from ``"data": {...}``.

        :return: JSON string of payload content
        :rtype: str
        """
        return _JsonExtractor.extract_object(self._json_str)
