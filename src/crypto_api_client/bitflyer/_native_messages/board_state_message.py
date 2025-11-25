from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.board_state import BoardState
from .bitflyer_message import BitFlyerMessage
from .board_state_payload import BoardStatePayload


class BoardStateMessage(BitFlyerMessage[BoardStatePayload, BoardState]):
    """:term:`native message` implementation for board state

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
              "health": "NORMAL",
              "state": "RUNNING"
            }

    .. seealso::

        Orderbook Status: https://lightning.bitflyer.com/docs?lang=en#orderbook-status
    """

    def _create_payload(self, payload_json_str: str) -> BoardStatePayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            {
              "health": "NORMAL",
              "state": "RUNNING"
            }
        """
        return BoardStatePayload(payload_json_str)

    def to_domain_model(self) -> BoardState:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, BoardState)
