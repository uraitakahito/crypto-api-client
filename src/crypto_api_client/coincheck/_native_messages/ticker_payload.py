from __future__ import annotations

from crypto_api_client._base import Payload


class TickerPayload(Payload):
    """Implementation of :term:`native message payload` for ticker.

    Coincheck's ticker :term:`API endpoint` returns ticker without metadata.
    Therefore, :term:`native message payload` and :term:`native response` are identical.

    .. note::

        This class uses the default implementation (Identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.
    """

    pass
