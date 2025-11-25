from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar

from crypto_api_client._base import Message, Payload

TPayload = TypeVar("TPayload", bound=Payload)
TDomainModel = TypeVar("TDomainModel")


class UpbitMessage(
    Message[None, TPayload, TDomainModel], ABC, Generic[TPayload, TDomainModel]
):
    """Base class for Upbit :term:`native message`.

    Upbit API responses do not have metadata wrapper,
    so the metadata type parameter is always ``None`` (bitFlyer pattern).

    Response returns data array or object directly::

        [
            {"market": "KRW-BTC", "trade_price": 4687000.0, ...},
            {"market": "KRW-ETH", "trade_price": 123000.0, ...}
        ]

    Type Parameters:
        TPayload: Type of Payload.
        TDomainModel: Type of Domain model.

    See Also:
        - :class:`~crypto_api_client._base.Message`
        - :class:`~crypto_api_client.bitflyer._native_messages.BitFlyerMessage`
          (Similar pattern without metadata)
    """

    def _create_metadata(self, json_str: str) -> None:
        """No metadata."""
        return None

    def _extract_payload_json(self, json_str: str) -> str:
        """Return entire response as payload.

        Since Upbit API has no metadata wrapper,
        the entire response JSON becomes the payload.
        """
        return json_str
