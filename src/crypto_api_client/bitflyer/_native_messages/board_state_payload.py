from __future__ import annotations

from crypto_api_client._base.payload import Payload


class BoardStatePayload(Payload):
    """:term:`native message payload` for board state

    bitFlyer's board state :term:`API endpoint` returns flat raw JSON string without metadata.
    Therefore, :term:`native message payload` and :term:`native response` are identical.

    .. note::

        This class uses the default implementation (identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.
    """

    pass
