"""Order book message"""

from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.order_book import OrderBook
from .coincheck_message import CoincheckMessage
from .order_book_payload import OrderBookPayload


class OrderBookMessage(CoincheckMessage[OrderBookPayload, OrderBook]):
    """Order book :term:`native message`

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    .. hint::

        **JSON string example:**

        .. code-block:: json

            {
                "asks": [
                    ["15350001", "0.1"],
                    ["15350002", "0.5"]
                ],
                "bids": [
                    ["15350000", "0.2"],
                    ["15349999", "0.3"]
                ]
            }

    .. seealso::

        Order Book: https://coincheck.com/documents/exchange/api#order-book
    """

    def _create_payload(self, payload_json_str: str) -> OrderBookPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like this:

        .. code-block:: json

            {
                "asks": [
                    ["15350001", "0.1"],
                    ["15350002", "0.5"]
                ],
                "bids": [
                    ["15350000", "0.2"],
                    ["15349999", "0.3"]
                ]
            }
        """
        return OrderBookPayload(payload_json_str)

    def to_domain_model(self) -> OrderBook:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, OrderBook)
