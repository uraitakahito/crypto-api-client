from __future__ import annotations

import json
from typing import Any

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.ticker import Ticker
from .gmocoin_message import GmoCoinMessage
from .ticker_payload import TickerPayload


class TickerMessage(GmoCoinMessage[TickerPayload, list[Ticker]]):
    """Implementation of ticker :term:`native message`

    Contains :term:`native message metadata` and :term:`native message payload`.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
                "status": 0,
                "data": [
                    {
                        "ask": "15350001",
                        "bid": "15350000",
                        "high": "15836477",
                        "last": "15350001",
                        "low": "15271389",
                        "symbol": "BTC_JPY",
                        "timestamp": "2025-01-30T12:34:56.789Z",
                        "volume": "273.5234"
                    }
                ],
                "responsetime": "2025-01-30T12:34:56.789Z"
            }

    .. seealso::

        `Official ticker API documentation <https://api.coin.z.com/docs/#ticker>`__
    """

    def _create_payload(self, payload_json_str: str) -> TickerPayload:
        """Create :term:`native message payload`

        Since the payload part has already been extracted by the base class,
        we simply pass it as is.
        """
        return TickerPayload(payload_json_str)

    def to_domain_model(self) -> list[Ticker]:
        """Generate :term:`native domain model` from :term:`payload content`

        Assumes that the data part of GMO Coin API is always in array format.
        If it is not an array, it is treated as an API specification change or
        abnormal response and raises an error.
        """
        # Parse payload JSON string
        data: Any = json.loads(self.payload.content_str)

        if not isinstance(data, list):
            raise ValueError(
                f"GMO Coin API response is not in expected array format. "
                f"Received data type: {type(data).__name__}"
            )

        # Convert each element of the array to Ticker
        tickers: list[Ticker] = []
        for item in data:  # type: ignore[misc]
            ticker = DecimalJsonParser.parse(json.dumps(item), Ticker)
            tickers.append(ticker)

        return tickers
