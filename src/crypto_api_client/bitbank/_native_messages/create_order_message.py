"""Message processing for order submission"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, cast

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models import Order, OrderStatus, OrderType, Side
from .bitbank_message import BitbankMessage
from .create_order_payload import CreateOrderPayload


class CreateOrderMessage(BitbankMessage[CreateOrderPayload, Order]):
    """:term:`native message` implementation for order

    Contains :term:`native message metadata` and :term:`native message payload`.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
                "success": 1,
                "data": {
                    "order_id": 12345678,
                    "pair": "btc_jpy",
                    "side": "buy",
                    "type": "limit",
                    "status": "UNFILLED",
                    "price": "5000000",
                    "amount": "0.001",
                    "executed_amount": "0",
                    "average_price": "0",
                    "ordered_at": 1614556800000,
                    "executed_at": null,
                    "canceled_at": null,
                    "trigger_price": null,
                    "post_only": false
                }
            }

    .. seealso::

        `bitbank-api-docs <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#create-new-order>`__
    """

    def _create_payload(self, payload_json_str: str) -> CreateOrderPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            "data": {
                "order_id": 12345678,
                "pair": "btc_jpy",
                "side": "buy",
                "type": "limit",
                "status": "UNFILLED",
                "price": "5000000",
                "amount": "0.001",
                "executed_amount": "0",
                "average_price": "0",
                "ordered_at": 1614556800000,
                "executed_at": null,
                "canceled_at": null,
                "trigger_price": null,
                "post_only": false
            }
        """
        return CreateOrderPayload(payload_json_str)

    def to_domain_model(self) -> Order:
        """Generate :term:`native domain model` from :term:`payload content`"""
        data = cast(
            dict[str, Any], DecimalJsonParser.parse(self.payload.content_str, dict)
        )

        return Order(
            order_id=int(data["order_id"]),
            pair=data["pair"],
            side=Side(data["side"]),
            type=OrderType(data["type"]),
            status=OrderStatus(data["status"]),
            price=Decimal(data["price"]) if data.get("price") else None,
            amount=Decimal(data["amount"]) if data.get("amount") else None,
            executed_amount=Decimal(data["executed_amount"]),
            average_price=Decimal(data["average_price"])
            if data.get("average_price")
            else None,
            ordered_at=datetime.fromtimestamp(
                int(data["ordered_at"]) / 1000, tz=timezone.utc
            ),  # Convert milliseconds to seconds
            executed_at=datetime.fromtimestamp(
                int(data["executed_at"]) / 1000, tz=timezone.utc
            )
            if data.get("executed_at")
            else None,
            canceled_at=datetime.fromtimestamp(
                int(data["canceled_at"]) / 1000, tz=timezone.utc
            )
            if data.get("canceled_at")
            else None,
            trigger_price=Decimal(data["trigger_price"])
            if data.get("trigger_price")
            else None,
            post_only=data.get("post_only"),
        )  # Convert milliseconds to seconds
