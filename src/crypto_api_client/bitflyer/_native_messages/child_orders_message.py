from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.child_order import ChildOrder
from .bitflyer_message import BitFlyerMessage
from .child_orders_payload import ChildOrdersPayload


class ChildOrdersMessage(BitFlyerMessage[ChildOrdersPayload, list[ChildOrder]]):
    """:term:`native message` implementation for child orders

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    Returns order list as an array.

    .. hint::
        **JSON string example:**

        .. code-block:: json

            [
                {
                    "id": 138398,
                    "child_order_id": "JOR20150707-084555-022523",
                    "product_code": "BTC_JPY",
                    "side": "BUY",
                    "child_order_type": "LIMIT",
                    "price": 30000,
                    "size": 0.1,
                    "executed_size": 0,
                    "child_order_state": "ACTIVE",
                    "expire_date": "2015-07-14T07:25:52",
                    "child_order_date": "2015-07-07T08:45:53",
                    "child_order_acceptance_id": "JRF20150707-084552-031927"
                }
            ]

    .. seealso::

        List Orders: https://lightning.bitflyer.com/docs?lang=en#list-orders

    """

    def _create_payload(self, payload_json_str: str) -> ChildOrdersPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            [
                {
                    "id": 138398,
                    "child_order_id": "JOR20150707-084555-022523",
                    "product_code": "BTC_JPY",
                    "side": "BUY",
                    "child_order_type": "LIMIT",
                    "price": 30000,
                    "size": 0.1,
                    "executed_size": 0,
                    "child_order_state": "ACTIVE",
                    "expire_date": "2015-07-14T07:25:52",
                    "child_order_date": "2015-07-07T08:45:53",
                    "child_order_acceptance_id": "JRF20150707-084552-031927"
                }
            ]
        """
        return ChildOrdersPayload(payload_json_str)

    def to_domain_model(self) -> list[ChildOrder]:
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
        return DecimalJsonParser.parse(updated_json, list[ChildOrder])
