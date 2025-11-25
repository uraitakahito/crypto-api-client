from __future__ import annotations

from crypto_api_client._base.payload import Payload


class ExchangeInfoPayload(Payload):
    """:term:`native message payload` for ExchangeInfo

    BINANCE exchange info :term:`API endpoint` returns JSON without metadata.
    Therefore, :term:`native message payload` matches :term:`native response`.

    Uses default implementation (`content_str` returns `_json_str` as-is).

    .. seealso::
        - :class:`crypto_api_client._base.payload.Payload`
    """

    pass
