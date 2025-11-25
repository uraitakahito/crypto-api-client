"""Private API own execution history message"""

from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.private_execution import PrivateExecution
from .bitflyer_message import BitFlyerMessage
from .private_executions_payload import PrivateExecutionsPayload


class PrivateExecutionsMessage(
    BitFlyerMessage[PrivateExecutionsPayload, list[PrivateExecution]]
):
    """:term:`native message` implementation for Private API own execution history

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    Returns own execution history list as an array.

    .. hint::
       **JSON string example:**

       .. code-block:: json

          [
            {
              "id": 100001,
              "side": "BUY",
              "price": 15900000,
              "size": 0.001,
              "exec_date": "2025-01-01T10:00:00Z",
              "commission": 0.0000015,
              "child_order_id": "JOR20250101-100000-123456",
              "child_order_acceptance_id": "JRF20250101-100000-123456"
            },
            {
              "id": 100002,
              "side": "SELL",
              "price": 16000000,
              "size": 0.002,
              "exec_date": "2025-01-01T11:00:00Z",
              "commission": 0.0000030,
              "child_order_id": "JOR20250101-110000-234567",
              "child_order_acceptance_id": "JRF20250101-110000-234567"
            }
          ]

    .. seealso::

        Get My Executions: https://lightning.bitflyer.com/docs?lang=en#execution-history

    """

    def _create_payload(self, payload_json_str: str) -> PrivateExecutionsPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

           [
             {
               "id": 100001,
               "side": "BUY",
               "price": 15900000,
               "size": 0.001,
               "exec_date": "2025-01-01T10:00:00Z",
               "commission": 0.0000015,
               "child_order_id": "JOR20250101-100000-123456",
               "child_order_acceptance_id": "JRF20250101-100000-123456"
             }
           ]
        """
        return PrivateExecutionsPayload(payload_json_str)

    def to_domain_model(self) -> list[PrivateExecution]:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(
            self.payload.content_str, list[PrivateExecution]
        )
