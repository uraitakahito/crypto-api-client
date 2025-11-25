from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.exchange_info import ExchangeInfo
from .binance_message import BinanceMessage
from .exchange_info_payload import ExchangeInfoPayload


class ExchangeInfoMessage(BinanceMessage[ExchangeInfoPayload, ExchangeInfo]):
    """:term:`native message` implementation for ExchangeInfo

    Processes response from BINANCE `/api/v3/exchangeInfo` :term:`API endpoint`.

    Does not contain :term:`native message metadata`, only :term:`native message payload`.

    .. hint::
        **Example JSON string:**

        .. code-block:: json

            {
              "timezone": "UTC",
              "serverTime": 1565246363776,
              "rateLimits": [
                {
                  "rateLimitType": "REQUEST_WEIGHT",
                  "interval": "MINUTE",
                  "intervalNum": 1,
                  "limit": 1200
                }
              ],
              "exchangeFilters": [],
              "symbols": [
                {
                  "symbol": "BTCUSDT",
                  "status": "TRADING",
                  "baseAsset": "BTC",
                  "baseAssetPrecision": 8,
                  "quoteAsset": "USDT",
                  "orderTypes": ["LIMIT", "MARKET"],
                  "filters": [...]
                }
              ]
            }

    .. seealso::
        `Exchange Information <https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information>`_
    """

    def _create_payload(self, payload_json_str: str) -> ExchangeInfoPayload:
        """Generate :term:`native message payload`"""
        return ExchangeInfoPayload(payload_json_str)

    def to_domain_model(self) -> ExchangeInfo:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, ExchangeInfo)
