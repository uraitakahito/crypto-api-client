from __future__ import annotations

from crypto_api_client._base import Payload
from crypto_api_client.core.json_extractor import (
    _JsonExtractor,  # type: ignore[reportPrivateUsage]
)


class CreateOrderPayload(Payload):
    """:term:`native message payload` implementation for order submission.

    This native message payload receives JSON string like the following:

    .. code-block:: json

        "data": {
            "order_id": 12345678,
            "pair": "btc_jpy",
            "side": "buy",
            "type": "limit",
            "status": "UNFILLED",
            "price": "5000000",
            "amount": "0.001",
            ...
        }

    Extracts ``{...}`` portion from ``"data": {...}``.

    .. note::

        Uses :meth:`~crypto_api_client.core.json_extractor._JsonExtractor.extract_object`
        to extract the object.
    """

    @property
    def content_str(self) -> str:
        """:term:`payload content` JSON string

        Extracts ``{...}`` from ``"data": {...}``.

        :return: JSON string of payload content
        :rtype: str
        """
        return _JsonExtractor.extract_object(self._json_str)
