"""Payload of cancel child order API response"""

from __future__ import annotations

from crypto_api_client._base import Payload


class CancelChildOrderPayload(Payload):
    """Response payload of cancel child order API

    bitFlyer's cancel child order API returns an empty response body on success.

    .. hint::

        **Response example (on success):**

        .. code-block:: json

            ""

    .. seealso::

        Cancel Order: https://lightning.bitflyer.com/docs?lang=en#cancel-order
    """

    @property
    def content_str(self) -> str:
        """Return JSON string of payload content

        On successful cancellation, an empty string is returned.

        :return: Empty string (indicates successful cancellation)
        :rtype: str
        """
        # Use default implementation as-is (returns empty string as-is)
        return self._json_str
