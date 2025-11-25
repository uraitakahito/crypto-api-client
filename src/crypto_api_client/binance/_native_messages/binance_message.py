from __future__ import annotations

from abc import abstractmethod

from crypto_api_client._base import Message


class BinanceMessage[TPayload, TDomainModel](Message[None, TPayload, TDomainModel]):
    """Base class for BINANCE :term:`native message`

    BINANCE does not have metadata, so metadata is always None.
    metadata and payload properties are already implemented in the base class.
    """

    def _create_metadata(self, json_str: str) -> None:
        """BINANCE has no metadata"""
        return None

    def _extract_payload_json(self, json_str: str) -> str:
        """For BINANCE, entire response is payload"""
        return json_str

    @abstractmethod
    def to_domain_model(self) -> TDomainModel:
        """Convert to domain model

        Subclasses implement specific conversion logic.
        """
        pass
