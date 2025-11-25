"""Message processing for order book"""

from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.depth import Depth
from .bitbank_message import BitbankMessage
from .depth_payload import DepthPayload


class DepthMessage(BitbankMessage[DepthPayload, Depth]):
    """:term:`native message` implementation for order book (Depth)

    Contains :term:`native message metadata` and :term:`native message payload`.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
                "success": 1,
                "data": {
                    "asks": [
                        ["15350001", "0.1"],
                        ["15350002", "0.5"]
                    ],
                    "bids": [
                        ["15350000", "0.2"],
                        ["15349999", "0.3"]
                    ],
                    "asks_over": "10.5",
                    "bids_under": "20.3",
                    "asks_under": "5.2",
                    "bids_over": "8.7",
                    "ask_market": "1.5",
                    "bid_market": "2.3",
                    "timestamp": 1748558090326,
                    "sequenceId": "1234567890"
                }
            }

    .. seealso::

        `Official Depth documentation <https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-api.md#depth>`__
    """

    def _create_payload(self, payload_json_str: str) -> DepthPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            "data": {
                "asks": [
                    ["15350001", "0.1"],
                    ["15350002", "0.5"]
                ],
                "bids": [
                    ["15350000", "0.2"],
                    ["15349999", "0.3"]
                ],
                "asks_over": "10.5",
                "bids_under": "20.3",
                "asks_under": "5.2",
                "bids_over": "8.7",
                "ask_market": "1.5",
                "bid_market": "2.3",
                "timestamp": 1748558090326,
                "sequenceId": "1234567890"
            }
        """
        return DepthPayload(payload_json_str)

    def to_domain_model(self) -> Depth:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, Depth)
