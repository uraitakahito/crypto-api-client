"""Payload part of bitFlyer API balances response"""

from __future__ import annotations

from crypto_api_client._base import Payload


class BalancesPayload(Payload):
    """:term:`native message payload` implementation for balance information.

    .. note::

        This class uses the default implementation (identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.
    """

    pass
