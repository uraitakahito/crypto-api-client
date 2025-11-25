from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.ticker import Ticker
from .binance_message import BinanceMessage
from .ticker_payload import TickerPayload


class TickerMessage(BinanceMessage[TickerPayload, Ticker]):
    """:term:`native message` implementation for ticker

    Does not contain :term:`native message metadata`, only :term:`native message payload`.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
                "symbol": "BTCUSDT",
                "priceChange": "-154.13000000",
                "priceChangePercent": "-0.740",
                "weightedAvgPrice": "20677.46305250",
                "prevClosePrice": "20825.27000000",
                "lastPrice": "20671.14000000",
                "lastQty": "0.00030000",
                "bidPrice": "20671.13000000",
                "bidQty": "0.05000000",
                "askPrice": "20671.14000000",
                "askQty": "0.94620000",
                "openPrice": "20825.27000000",
                "highPrice": "20972.46000000",
                "lowPrice": "20327.92000000",
                "volume": "72.65112300",
                "quoteVolume": "1502240.91155513",
                "openTime": 1655432400000,
                "closeTime": 1655446835460,
                "firstId": 11147809,
                "lastId": 11149775,
                "count": 1967
            }

    .. seealso::

        24hr Ticker Price Change Statistics: https://developers.binance.com/docs/binance-spot-api-docs/rest-api#24hr-ticker-price-change-statistics
    """

    def _create_payload(self, payload_json_str: str) -> TickerPayload:
        """Generate :term:`native message payload`"""
        return TickerPayload(payload_json_str)

    def to_domain_model(self) -> Ticker:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, Ticker)
