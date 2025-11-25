from __future__ import annotations

from crypto_api_client.core import DecimalJsonParser

from ..native_domain_models import Ticker
from .ticker_payload import TickerPayload
from .upbit_message import UpbitMessage


class TickerMessage(UpbitMessage[TickerPayload, list[Ticker]]):
    """Implementation of ticker :term:`native message`.

    Processes response from Upbit ticker API.

    Response is always in array format and may contain multiple Tickers::

    Even when a single market is requested, it is returned as an array (with 1 element).

    .. seealso::

        - :class:`~crypto_api_client.upbit.native_domain_models.Ticker`
        - :class:`~crypto_api_client.upbit._native_messages.UpbitMessage`
    """

    def _create_payload(self, payload_json_str: str) -> TickerPayload:
        """Generate :term:`native message payload`."""
        return TickerPayload(payload_json_str)

    def to_domain_model(self) -> list[Ticker]:
        """Parse JSON array to list of Tickers.

        Generate list of Ticker objects from :term:`payload content`.
        """
        return DecimalJsonParser.parse(self.payload.content_str, list[Ticker])
