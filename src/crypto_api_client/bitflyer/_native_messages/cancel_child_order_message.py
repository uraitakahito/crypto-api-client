"""Cancel child order API response message"""

from __future__ import annotations

from .bitflyer_message import BitFlyerMessage
from .cancel_child_order_payload import CancelChildOrderPayload


class CancelChildOrderMessage(BitFlyerMessage[CancelChildOrderPayload, None]):
    """:term:`native message` implementation for cancel child order

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    On successful cancellation, an empty response body is returned.

    .. hint::

        **JSON string example (on success):**

        .. code-block:: json

            ""

    .. seealso::

        Cancel Order: https://lightning.bitflyer.com/docs?lang=en#cancel-order
    """

    def _create_payload(self, payload_json_str: str) -> CancelChildOrderPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument receives an empty string (on successful cancellation):

        .. code-block:: json

            ""
        """
        return CancelChildOrderPayload(payload_json_str)

    def to_domain_model(self) -> None:
        """Return None (indicates successful cancellation)

        On successful cancellation, bitFlyer API returns an empty response,
        so this method always returns None.
        """
        return None
