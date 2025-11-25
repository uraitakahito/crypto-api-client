from __future__ import annotations

from crypto_api_client._base.payload import Payload
from crypto_api_client.core.json_extractor import (
    _JsonExtractor,  # type: ignore[reportPrivateUsage]
)


class UnsettledOrdersPayload(Payload):
    """:term:`native message payload` for unsettled orders list

    Holds only pure payload data with the ``success`` field excluded
    by :class:`UnsettledOrdersMessage`.

    Entire Coincheck response:

    .. code-block:: json

        {
            "success": true,  // ← Metadata (excluded by UnsettledOrdersMessage)
            "orders": [...]   // ← Payload (held by this class)
        }

    JSON held by this class:

    .. code-block:: json

        {
            "orders": [...]
        }

    .. note::

        Metadata (``success``) exclusion is already performed in
        :meth:`UnsettledOrdersMessage._extract_payload_json`,
        so this class only handles pure payload.

    .. seealso::
        - :term:`native message payload`
        - :term:`payload content`
        - :meth:`UnsettledOrdersMessage._extract_payload_json` - Metadata exclusion processing
    """

    @property
    def content_str(self) -> str:
        """Return :term:`payload content`

        Extract the value (array) of the `orders` key and return it as JSON string.

        .. note::

            The received JSON has the ``success`` field already excluded
            by ``_extract_payload_json()``, so it has the following format:

            .. code-block:: json

                {
                    "orders": [...]
                }

            This method extracts only the array portion of the ``orders`` key:

            .. code-block:: json

                [...]

        :return: JSON string of orders array
        :rtype: str
        """
        start_pos = self._json_str.find('"orders"')
        if start_pos == -1:
            raise ValueError('"orders" field not found in JSON')

        return _JsonExtractor.extract_array(self._json_str, start_pos=start_pos)
