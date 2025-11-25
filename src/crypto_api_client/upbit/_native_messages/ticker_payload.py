from __future__ import annotations

from crypto_api_client._base import Payload


class TickerPayload(Payload):
    """Implementation of ticker :term:`native message payload`.

    Upbit ticker API response is returned as-is in array format,
    so no data processing is needed. Uses default implementation as-is.

    Response format::

        [
            {
                "market": "KRW-BTC",
                "trade_price": 4687000.0,
                "opening_price": 4380000.0,
                ...
            }
        ]

    See Also:
        - :class:`~crypto_api_client._base.Payload`
        - :class:`~crypto_api_client.bitflyer._native_messages.TickerPayload`
          (Similar pattern requiring no processing)
    """

    pass
