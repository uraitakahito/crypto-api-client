"""Common metadata for Coincheck API messages"""

from __future__ import annotations

from pydantic import BaseModel


class MessageMetadata(BaseModel):
    """Metadata portion of Coincheck API messages

    Implementation of :term:`native message metadata`.
    Contains status information indicating success/failure of API.

    .. note::

        Only used with API endpoints that have metadata (Balance API, etc.).
        Not used with APIs without metadata (Ticker API, etc.).

    .. hint::

        **JSON string example (Balance API - with metadata):**

        .. code-block:: json

            {
                "success": true,
                "btc": "7.75052654",
                "btc_reserved": "3.5002"
            }

        **JSON string example (Ticker API - without metadata):**

        .. code-block:: json

            {
                "last": 15350000,
                "bid": 15340000,
                "ask": 15350001
            }

        For APIs without metadata,
        ``CoincheckMessage.metadata`` returns ``None``.

    .. seealso::

        - Balance API: https://coincheck.com/documents/exchange/api#account-balance
        - Ticker API: https://coincheck.com/ja/documents/exchange/api#ticker
    """

    success: bool

    model_config = {"frozen": True}

    @property
    def json_str(self) -> str:
        """Return MessageMetadata as JSON string

        Returns:
            str: JSON string in '{"success": true}' format
        """
        return f'{{"success": {"true" if self.success else "false"}}}'
