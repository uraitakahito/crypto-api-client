from __future__ import annotations

import re
from abc import abstractmethod

from crypto_api_client._base import Message

from .message_metadata import MessageMetadata


class CoincheckMessage[TPayload, TDomainModel](
    Message[MessageMetadata | None, TPayload, TDomainModel]
):
    """Base class for Coincheck :term:`native message`

    metadata and payload properties are already implemented in the base class.

    **Metadata presence:**

    - **Balance API, etc.**: Has metadata (``success: bool``)
    - **Ticker API, etc.**: No metadata (``None``)

    **Metadata and payload structure:**

    In Balance API (with metadata), metadata (``success``) and payload are mixed at the same level:

    .. code-block:: json

        {
            "success": true,  // ← Metadata
            "btc": "7.75052654",  // ← Payload
            "btc_reserved": "3.5002"  // ← Payload
        }

    Ticker API (no metadata):

    .. code-block:: json

        {
            "last": 15350000,  // ← Payload only
            "bid": 15340000,
            "ask": 15350001
        }

    **_extract_payload_json() behavior:**

    This base class automatically selects the appropriate processing
    based on the result of ``_create_metadata()``:

    - With metadata → Exclude ``success`` field
    - Without metadata → Return entire response as-is

    .. seealso::

        - :class:`MessageMetadata` - Metadata class
        - :meth:`_extract_payload_json` - Payload extraction implementation
        - Balance API: https://coincheck.com/documents/exchange/api#account-balance
        - Ticker API: https://coincheck.com/documents/exchange/api#ticker
    """

    def _create_metadata(self, json_str: str) -> MessageMetadata | None:
        """Extract 'success' field from JSON and generate metadata

        Returns metadata if 'success' field exists (Balance API, etc.),
        returns None if it doesn't exist (Ticker API, etc.).

        :param json_str: JSON string of API response
        :return: MessageMetadata instance, or None (for APIs without metadata)
        """
        success_match = re.search(r'"success"\s*:\s*(true|false)', json_str)

        if success_match is None:
            return None

        success_value = success_match.group(1) == "true"
        return MessageMetadata(success=success_value)

    def _extract_payload_json(self, json_str: str) -> str:
        """Return entire response or JSON string after excluding success field

        Coincheck API has two patterns:

        1. **With metadata (Balance, Unsettled Orders, etc.)**:
           Returns payload excluding `success` field

        2. **Without metadata (Ticker, etc.)**:
           Returns entire response as-is as payload

        This base class implementation automatically selects appropriate processing
        based on the result of ``self.metadata`` property.

        .. list-table:: Behavior by API
           :header-rows: 1
           :widths: 20 40 40

           * - API
             - Input JSON
             - Output JSON
           * - Balance
             - ``{"success": true, "jpy": "1000.0"}``
             - ``{"jpy": "1000.0"}``
           * - Unsettled Orders
             - ``{"success": true, "orders": [...]}``
             - ``{"orders": [...]}``
           * - Ticker
             - ``{"last": "15350001", "bid": "15350000"}``
             - ``{"last": "15350001", "bid": "15350000"}``

        .. note::

            **About precision preservation:**

            When excluding `success` field, we manipulate the JSON string directly.
            Using ``json.loads()`` -> ``json.dumps()`` may cause precision loss
            because numbers pass through Python's float type.

        :param json_str: JSON string of API response
        :type json_str: str
        :return: JSON string of payload portion
        :rtype: str

        .. seealso::

            - :attr:`metadata` - Cached metadata property
            - :meth:`_create_metadata` - Determine presence of metadata
            - :class:`BalanceMessage` - Example of API with metadata
            - :class:`TickerMessage` - Example of API without metadata
        """
        if self.metadata is None:
            return json_str

        # Exclude success field
        # Remove "success": true or "success": false
        pattern = r'"success"\s*:\s*(?:true|false)\s*,?\s*'
        result = re.sub(pattern, "", json_str)

        # Remove extra commas at beginning or end (in case of {, or ,} format)
        result = re.sub(r"{\s*,", "{", result)
        result = re.sub(r",\s*}", "}", result)

        return result

    @abstractmethod
    def to_domain_model(self) -> TDomainModel:
        """Convert to domain model

        Subclasses implement specific conversion logic.
        """
        pass
