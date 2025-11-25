from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.health_status import HealthStatus
from .bitflyer_message import BitFlyerMessage
from .health_status_payload import HealthStatusPayload


class HealthStatusMessage(BitFlyerMessage[HealthStatusPayload, HealthStatus]):
    """:term:`native message` implementation for health status

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    Returns exchange health status.

    .. hint::
        **JSON string example:**

        .. code-block:: json

           {
             "status": "NORMAL"
           }

    .. seealso::

        Exchange Status: https://lightning.bitflyer.com/docs?lang=en#exchange-status

    """

    def _create_payload(self, payload_json_str: str) -> HealthStatusPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

           {
             "status": "NORMAL"
           }
        """
        return HealthStatusPayload(payload_json_str)

    def to_domain_model(self) -> HealthStatus:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, HealthStatus)

    def to_health_status(self) -> HealthStatus:
        """Alias method for API client compatibility"""
        return self.to_domain_model()
