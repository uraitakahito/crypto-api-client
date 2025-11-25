from __future__ import annotations

from crypto_api_client._base import Payload
from crypto_api_client.core.json_extractor import (
    _JsonExtractor,  # type: ignore[reportPrivateUsage]
)


class TickerPayload(Payload):
    """:term:`native message payload` implementation for ticker.

    This native message payload receives JSON string like the following:

    .. code-block:: json

        "data": {
            "sell": "15350001",
            "buy": "15350000",
            "last": "15350001",
            "vol": "273.5234",
            "timestamp": 1748558090326
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
