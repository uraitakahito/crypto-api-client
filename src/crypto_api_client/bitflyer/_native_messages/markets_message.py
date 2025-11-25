from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.market import Market
from .bitflyer_message import BitFlyerMessage
from .markets_payload import MarketsPayload


class MarketsMessage(BitFlyerMessage[MarketsPayload, list[Market]]):
    """:term:`native message` implementation for markets

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    Returns list of available markets as an array.

    .. hint::
        **JSON string example:**

        .. code-block:: json

            [
                {
                    "product_code": "BTC_JPY",
                    "market_type": "Spot",
                    "alias": "BTC/JPY"
                },
                {
                    "product_code": "FX_BTC_JPY",
                    "market_type": "FX"
                }
            ]

        .. seealso::

            Market List: https://lightning.bitflyer.com/docs?lang=en#market-list
    """

    def _create_payload(self, payload_json_str: str) -> MarketsPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            [
                {
                    "product_code": "BTC_JPY",
                    "market_type": "Spot",
                    "alias": "BTC/JPY"
                },
                {
                    "product_code": "FX_BTC_JPY",
                    "market_type": "FX"
                }
            ]
        """
        return MarketsPayload(payload_json_str)

    def to_domain_model(self) -> list[Market]:
        """Generate :term:`native domain model` from :term:`payload content`"""
        import json

        # Parse JSON as array
        data = json.loads(self.payload.content_str)

        # Map product_code to pair for each element
        for item in data:
            if "product_code" in item and "pair" not in item:
                item["pair"] = item["product_code"]

        # Convert back to JSON string and parse
        updated_json = json.dumps(data)
        return DecimalJsonParser.parse(updated_json, list[Market])
