"""Order book payload"""

from __future__ import annotations

from crypto_api_client._base.payload import Payload


class OrderBookPayload(Payload):
    """Implementation of :term:`native message payload` for order book.

    Coincheck's order book :term:`API endpoint` returns order book without metadata.
    Therefore, :term:`native message payload` and :term:`native response` are identical.

    .. note::

        This class uses the default implementation (Identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.
    """

    pass
