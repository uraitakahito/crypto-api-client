"""Payload part of bitFlyer API send child order response"""

from __future__ import annotations

from crypto_api_client._base import Payload


class SendChildOrderPayload(Payload):
    """:term:`native message payload` implementation for order submission.

    Since bitFlyer's send child order API directly returns a single object without metadata,
    this Payload becomes the Response itself.

    .. note::

        This class uses the default implementation (identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.
    """

    pass
