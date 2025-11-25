"""Payload portion of bitbank API assets response"""

from __future__ import annotations

from crypto_api_client._base import Payload
from crypto_api_client.core.json_extractor import (
    _JsonExtractor,  # type: ignore[reportPrivateUsage]
)


class AssetsPayload(Payload):
    """:term:`native message payload` implementation for asset information.

    This native message payload receives JSON string like the following:

    .. code-block:: json

        "data": {
            "assets": [
                {
                    "asset": "jpy",
                    "onhand_amount": "100000.0000",
                    "locked_amount": "0.0000",
                    ...
                }
            ]
        }

    Performs two-stage extraction:

    1. Extract ``{...}`` from ``"data": {...}``
    2. Extract ``[...]`` from ``{"assets": [...]}``

    .. note::

        Uses :meth:`~crypto_api_client.core.json_extractor._JsonExtractor.extract_object`
        and :meth:`~crypto_api_client.core.json_extractor._JsonExtractor.extract_array`
        in combination.
    """

    @property
    def content_str(self) -> str:
        """:term:`payload content` JSON string

        Performs two-stage extraction:

        1. Extract ``{...}`` from ``"data": {...}``
        2. Extract ``[...]`` from ``{"assets": [...]}``

        :return: JSON string of assets array
        :rtype: str
        """
        # Stage 1: Extract {...} portion from "data": {...}
        data_object = _JsonExtractor.extract_object(self._json_str)
        # Stage 2: Extract [...] portion from {"assets": [...]}

        start_pos = data_object.find('"assets"')
        return _JsonExtractor.extract_array(data_object, start_pos=start_pos)
