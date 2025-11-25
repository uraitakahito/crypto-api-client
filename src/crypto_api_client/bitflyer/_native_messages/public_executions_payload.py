"""Payload part of bitFlyer Public API executions response"""

from __future__ import annotations

from crypto_api_client._base import Payload


class PublicExecutionsPayload(Payload):
    """:term:`native message payload` implementation for execution history (Public API).

    .. note::

        This class uses the default implementation (identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.
    """

    pass
