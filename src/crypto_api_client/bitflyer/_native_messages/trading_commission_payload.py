"""Payload part of bitFlyer API trading commission response"""

from __future__ import annotations

from crypto_api_client._base import Payload


class TradingCommissionPayload(Payload):
    """:term:`native message payload` implementation for trading commission.

    Since bitFlyer's trading commission API directly returns a single object without metadata,
    this Payload becomes the Response itself.

    .. note::

        This class uses the default implementation (identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.
    """

    pass
