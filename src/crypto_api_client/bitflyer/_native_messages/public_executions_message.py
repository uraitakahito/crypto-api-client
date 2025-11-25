from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.public_execution import PublicExecution
from .bitflyer_message import BitFlyerMessage
from .public_executions_payload import PublicExecutionsPayload


class PublicExecutionsMessage(
    BitFlyerMessage[PublicExecutionsPayload, list[PublicExecution]]
):
    """:term:`native message` implementation for Public API executions

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    Returns execution history list as an array.

    .. hint::
       **JSON string example:**

       .. code-block:: json

          [
            {
              "id": 39287,
              "side": "BUY",
              "price": 31690,
              "size": 27.04,
              "exec_date": "2015-07-08T02:43:34.823",
              "buy_child_order_acceptance_id": "JRF20150707-200203-452209",
              "sell_child_order_acceptance_id": "JRF20150708-024334-060234"
            }
          ]

    .. seealso::

        Execution History: https://lightning.bitflyer.com/docs?lang=en#execution-history

    """

    def _create_payload(self, payload_json_str: str) -> PublicExecutionsPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

           [
             {
               "id": 39287,
               "side": "BUY",
               "price": 31690,
               "size": 27.04,
               "exec_date": "2015-07-08T02:43:34.823",
               "buy_child_order_acceptance_id": "JRF20150707-200203-452209",
               "sell_child_order_acceptance_id": "JRF20150708-024334-060234"
             }
           ]
        """
        return PublicExecutionsPayload(payload_json_str)

    def to_domain_model(self) -> list[PublicExecution]:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, list[PublicExecution])
