from __future__ import annotations

from abc import abstractmethod

from crypto_api_client._base import Message


class BitFlyerMessage[TPayload, TDomainModel](Message[None, TPayload, TDomainModel]):
    """Base class for bitFlyer :term:`native message`

    Since bitFlyer has no metadata, metadata is always None.
    The metadata and payload properties are implemented in the base class.
    """

    def _create_metadata(self, json_str: str) -> None:
        """bitFlyer has no metadata"""
        return None

    def _extract_payload_json(self, json_str: str) -> str:
        """For bitFlyer, entire response is payload"""
        return json_str

    @abstractmethod
    def to_domain_model(self) -> TDomainModel:
        """Convert to domain model

        Subclasses implement the specific conversion logic.
        """
        pass
