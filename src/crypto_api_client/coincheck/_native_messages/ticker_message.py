from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.ticker import Ticker
from .coincheck_message import CoincheckMessage
from .ticker_payload import TickerPayload


class TickerMessage(CoincheckMessage[TickerPayload, Ticker]):
    """Implementation of :term:`native message` for ticker

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    .. hint::

        **JSON string example:**

        .. code-block:: json

            {
                "last": 15350000,
                "bid": 15340000,
                "ask": 15350001,
                "high": 15836477,
                "low": 15271389,
                "volume": "273.5234",
                "timestamp": 1748558090
            }

    .. warning::

        Attempting to retrieve a non-existent ticker returns an HTML page with HTTP status code 401, not JSON.

    .. seealso::

        Ticker: https://coincheck.com/ja/documents/exchange/api#ticker
    """

    def _create_payload(self, payload_json_str: str) -> TickerPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like this:

        .. code-block:: json

            {
                "last": 15350000,
                "bid": 15340000,
                "ask": 15350001,
                "high": 15836477,
                "low": 15271389,
                "volume": "273.5234",
                "timestamp": 1748558090
            }
        """
        return TickerPayload(payload_json_str)

    def to_domain_model(self) -> Ticker:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, Ticker)
