"""Order book message"""

from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.board import Board
from .bitflyer_message import BitFlyerMessage
from .board_payload import BoardPayload


class BoardMessage(BitFlyerMessage[BoardPayload, Board]):
    """:term:`native message` implementation for order book

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
                "mid_price": 33320,
                "bids": [
                    {
                        "price": 30000,
                        "size": 0.1
                    },
                    {
                        "price": 29990,
                        "size": 0.5
                    }
                ],
                "asks": [
                    {
                        "price": 36640,
                        "size": 5
                    },
                    {
                        "price": 36700,
                        "size": 0.2
                    }
                ]
            }

    .. seealso::

        Order Book: https://lightning.bitflyer.com/docs?lang=en#order-book

    :param json_str: JSON string containing order book
    :type json_str: str
    """

    def _create_payload(self, payload_json_str: str) -> BoardPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            {
                "mid_price": 33320,
                "bids": [
                    {
                        "price": 30000,
                        "size": 0.1
                    },
                    {
                        "price": 29990,
                        "size": 0.5
                    }
                ],
                "asks": [
                    {
                        "price": 36640,
                        "size": 5
                    },
                    {
                        "price": 36700,
                        "size": 0.2
                    }
                ]
            }
        """
        return BoardPayload(payload_json_str)

    def to_domain_model(self) -> Board:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, Board)
