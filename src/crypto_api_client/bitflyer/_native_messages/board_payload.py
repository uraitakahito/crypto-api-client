from __future__ import annotations

from crypto_api_client._base import Payload


class BoardPayload(Payload):
    """:term:`native message payload` implementation for order book.

    bitFlyer's order book :term:`API endpoint` returns order book without metadata.
    Therefore, :term:`native message payload` and :term:`native message` are identical.

    .. note::

        This class uses the default implementation (identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.
    """

    pass
