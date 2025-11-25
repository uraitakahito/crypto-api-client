from __future__ import annotations

from crypto_api_client._base import Payload


class DepthPayload(Payload):
    """:term:`native message payload` implementation for order book (Depth).

    BINANCE order book :term:`API endpoint` returns order book without metadata.
    Therefore, :term:`native message payload` matches :term:`native response`.

    .. note::

        This class uses the default implementation (Identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.
    """

    pass
