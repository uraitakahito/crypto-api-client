from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.order import Order
from .coincheck_message import CoincheckMessage
from .unsettled_orders_payload import UnsettledOrdersPayload


class UnsettledOrdersMessage(CoincheckMessage[UnsettledOrdersPayload, list[Order]]):
    """Implementation of :term:`native message` for own unsettled orders list

    :term:`native message metadata` and :term:`native message payload` are mixed at the same level.

    .. hint::

        **JSON example:**

        .. code-block:: json

            {
                "success": true,
                "orders": [
                    {
                        "id": 202835,
                        "order_type": "buy",
                        "rate": 26890,
                        "pair": "btc_jpy",
                        "pending_amount": "0.5527",
                        "pending_market_buy_amount": null,
                        "stop_loss_rate": null,
                        "created_at": "2015-01-10T05:55:38.000Z"
                    }
                ]
            }

    .. seealso::

        - Unsettled Orders API: https://coincheck.com/ja/documents/exchange/api#order-opens
        - :meth:`CoincheckMessage._extract_payload_json` - Implementation of metadata exclusion
    """

    def _create_payload(self, payload_json_str: str) -> UnsettledOrdersPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON with the ``success`` field excluded
        by ``CoincheckMessage._extract_payload_json()``, like this:

        .. code-block:: json

            {
                "orders": [
                    {
                        "id": 202835,
                        "order_type": "buy",
                        "rate": 26890,
                        "pair": "btc_jpy",
                        "pending_amount": "0.5527",
                        "pending_market_buy_amount": null,
                        "stop_loss_rate": null,
                        "created_at": "2015-01-10T05:55:38.000Z"
                    }
                ]
            }
        """
        return UnsettledOrdersPayload(payload_json_str)

    def to_domain_model(self) -> list[Order]:
        """Generate :term:`native domain model` list from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, list[Order])
