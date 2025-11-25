from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from .bitflyer_message import BitFlyerMessage
from .send_child_order_payload import SendChildOrderPayload


class SendChildOrderMessage(BitFlyerMessage[SendChildOrderPayload, str]):
    """:term:`native message` implementation for send child order

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    Returns order acceptance ID as a string.

    .. hint::

        **JSON string example:**

        .. code-block:: json

            {
                "child_order_acceptance_id": "JRF20150707-050237-639234"
            }
    """

    def _create_payload(self, payload_json_str: str) -> SendChildOrderPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            {
                "child_order_acceptance_id": "JRF20150707-050237-639234"
            }
        """
        return SendChildOrderPayload(payload_json_str)

    def to_domain_model(self) -> str:
        """Extract and return order acceptance ID"""
        # Extract child_order_acceptance_id value from entire JSON
        response_dict = DecimalJsonParser.parse(
            self.payload.content_str, dict[str, str]
        )
        return response_dict["child_order_acceptance_id"]
