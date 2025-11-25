from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser
from crypto_api_client.gmocoin._native_messages.gmocoin_message import (
    GmoCoinMessage,
)
from crypto_api_client.gmocoin._native_messages.orderbook_payload import (
    OrderBookPayload,
)
from crypto_api_client.gmocoin.native_domain_models import OrderBook


class OrderBookMessage(GmoCoinMessage[OrderBookPayload, OrderBook]):
    """Implementation of OrderBook :term:`native message`

    Contains :term:`native message metadata` and :term:`native message payload`.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
                "status": 0,
                "data": {
                    "asks": [
                        {"price": "455659", "size": "0.1"}
                    ],
                    "bids": [
                        {"price": "455665", "size": "0.1"}
                    ],
                    "symbol": "BTC"
                },
                "responsetime": "2019-03-19T02:15:06.026Z"
            }

    .. seealso::

        `OrderBooks API <https://api.coin.z.com/docs/#orderbooks>`__
    """

    def _create_payload(self, payload_json_str: str) -> OrderBookPayload:
        """Create :term:`native message payload`

        Since the payload part has already been extracted by the base class,
        we simply pass it as is.
        """
        return OrderBookPayload(payload_json_str)

    def to_domain_model(self) -> OrderBook:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, OrderBook)
