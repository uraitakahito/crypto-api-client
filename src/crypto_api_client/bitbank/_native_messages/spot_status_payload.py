"""Native message payload for spot status"""

from __future__ import annotations

from crypto_api_client._base import Payload
from crypto_api_client.core.json_extractor import (
    _JsonExtractor,  # type: ignore[reportPrivateUsage]
)


class SpotStatusPayload(Payload):
    """:term:`native message payload` implementation for spot status.

    This native message payload receives JSON string like the following:

    .. code-block:: json

        "data": {
            "statuses": [
                {
                    "pair": "btc_jpy",
                    "status": "NORMAL",
                    "min_amount": "0.0001"
                }
            ]
        }

    Performs two-stage extraction:

    1. Extract ``{...}`` from ``"data": {...}``
    2. Extract ``[...]`` from ``{"statuses": [...]}``

    .. note::

        Uses :meth:`~crypto_api_client.core.json_extractor._JsonExtractor.extract_object`
        and
        :meth:`~crypto_api_client.core.json_extractor._JsonExtractor.extract_array`
        in combination.
    """

    @property
    def content_str(self) -> str:
        """:term:`payload content` JSON string

        Performs two-stage extraction:

        1. Extract ``{...}`` from ``"data": {...}``
        2. Extract ``[...]`` from ``{"statuses": [...]}``

        :return: JSON string of statuses array
        :rtype: str
        """
        # 1. Extract {...} portion from "data": {...}
        data_object = _JsonExtractor.extract_object(self._json_str)
        # 2. Extract [...] portion from {"statuses": [...]}

        start_pos = data_object.find('"statuses"')
        return _JsonExtractor.extract_array(data_object, start_pos=start_pos)
