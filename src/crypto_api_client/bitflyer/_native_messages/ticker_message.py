from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.ticker import Ticker
from .bitflyer_message import BitFlyerMessage
from .ticker_payload import TickerPayload


class TickerMessage(BitFlyerMessage[TickerPayload, Ticker]):
    """:term:`native message` implementation for ticker

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    .. hint::

        **JSON string example:**

        .. code-block:: json

            {
                "product_code": "BTC_JPY",
                "state": "RUNNING",
                "timestamp": "2015-07-08T02:50:59.97",
                "tick_id": 3579,
                "best_bid": 30000,
                "best_ask": 36640,
                "best_bid_size": 0.1,
                "best_ask_size": 5,
                "total_bid_depth": 15.13,
                "total_ask_depth": 20,
                "market_bid_size": 0,
                "market_ask_size": 0,
                "ltp": 31690,
                "volume": 16819.26,
                "volume_by_product": 6819.26
            }

    .. seealso::

        Ticker: https://lightning.bitflyer.com/docs?lang=en#ticker
    """

    def _create_payload(self, payload_json_str: str) -> TickerPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            {
                "product_code": "BTC_JPY",
                "state": "RUNNING",
                "timestamp": "2015-07-08T02:50:59.97",
                "tick_id": 3579,
                "best_bid": 30000,
                "best_ask": 36640,
                "best_bid_size": 0.1,
                "best_ask_size": 5,
                "total_bid_depth": 15.13,
                "total_ask_depth": 20,
                "market_bid_size": 0,
                "market_ask_size": 0,
                "ltp": 31690,
                "volume": 16819.26,
                "volume_by_product": 6819.26
            }
        """
        return TickerPayload(payload_json_str)

    def to_domain_model(self) -> Ticker:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, Ticker)
