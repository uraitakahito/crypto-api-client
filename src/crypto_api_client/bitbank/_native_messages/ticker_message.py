"""Ticker message processing"""

from __future__ import annotations

from typing import Any, Dict, cast

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.ticker import Ticker
from .bitbank_message import BitbankMessage
from .ticker_payload import TickerPayload


class TickerMessage(BitbankMessage[TickerPayload, Ticker]):
    """:term:`native message` implementation for ticker

    Contains :term:`native message metadata` and :term:`native message payload`.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
                "success": 1,
                "data": {
                    "sell": "15350001",
                    "buy": "15350000",
                    "open": "15572550",
                    "high": "15836477",
                    "low": "15271389",
                    "last": "15350001",
                    "vol": "273.5234",
                    "timestamp": 1748558090326
                }
            }

    .. seealso::

        `Official Ticker documentation <https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-api.md#ticker>`__
    """

    def _create_payload(self, payload_json_str: str) -> TickerPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            "data": {
                "sell": "15350001",
                "buy": "15350000",
                "open": "15572550",
                "high": "15836477",
                "low": "15271389",
                "last": "15350001",
                "vol": "273.5234",
                "timestamp": 1748558090326
            }
        """
        return TickerPayload(payload_json_str)

    def to_domain_model(self) -> Ticker:
        """Generate :term:`native domain model` from :term:`payload content`"""
        data = cast(
            Dict[str, Any], DecimalJsonParser.parse(self.payload.content_str, dict)
        )

        return Ticker(**data)
