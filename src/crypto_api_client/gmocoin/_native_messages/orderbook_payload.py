from __future__ import annotations

from crypto_api_client._base import Payload
from crypto_api_client.core.json_extractor import (
    _JsonExtractor,  # type: ignore[reportPrivateUsage]
)


class OrderBookPayload(Payload):
    """Implementation of OrderBook payload

    Processes the payload part of GMO Coin orderBook API response.

    GMO Coin response structure:
    {
        "status": 0,
        "data": {...},  ← This is the payload
        "responsetime": "..."
    }

    This native message payload receives a JSON string like this:

    .. code-block:: json

        "data": {
            "asks": [
                {"price": "455659", "size": "0.1"}
            ],
            "bids": [
                {"price": "455665", "size": "0.1"}
            ],
            "symbol": "BTC"
        }

    Extracts the ``{...}`` part from ``"data": {...}``.

    .. note::

        Uses :meth:`~crypto_api_client.core.json_extractor._JsonExtractor.extract_object`
        to extract the object.
    """

    @property
    def content_str(self) -> str:
        """Get JSON string of :term:`payload content`

        Extracts ``{...}`` from ``"data": {...}``.

        Input example: "data": {"asks": [...], "bids": [...], "symbol": "BTC"}
        Output example: {"asks": [...], "bids": [...], "symbol": "BTC"}

        :return: JSON string of payload content
        :rtype: str
        """
        # Extract {...} part from "data": {...}
        return _JsonExtractor.extract_object(self._json_str)
