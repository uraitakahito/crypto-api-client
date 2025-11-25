"""Payload part of bitFlyer API markets response"""

from __future__ import annotations

from crypto_api_client._base import Payload


class MarketsPayload(Payload):
    """:term:`native message payload` implementation for market information.

    .. note::

        This class uses the default implementation (identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.
    """

    pass
