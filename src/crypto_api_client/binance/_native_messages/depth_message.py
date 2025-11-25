from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.depth import Depth
from .binance_message import BinanceMessage
from .depth_payload import DepthPayload


class DepthMessage(BinanceMessage[DepthPayload, Depth]):
    """:term:`native message` implementation for depth

    Does not contain :term:`native message metadata`, only :term:`native message payload`.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
                "lastUpdateId": 1027024,
                "bids": [
                    ["4.00000000", "431.00000000"],
                    ["3.99000000", "100.00000000"]
                ],
                "asks": [
                    ["4.00000200", "12.00000000"],
                    ["4.00000400", "22.00000000"]
                ]
            }

    .. seealso::

        Order Book: https://developers.binance.com/docs/binance-spot-api-docs/testnet/rest-api/market-data-endpoints

    :param json_str: JSON string containing depth
    :type json_str: str
    """

    def _create_payload(self, payload_json_str: str) -> DepthPayload:
        """Generate :term:`native message payload`"""
        return DepthPayload(payload_json_str)

    def to_domain_model(self) -> Depth:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, Depth)
