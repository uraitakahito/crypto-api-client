from __future__ import annotations

import re
from abc import abstractmethod

from crypto_api_client._base import Message
from crypto_api_client.core.json_extractor import (
    _JsonExtractor,  # type: ignore[reportPrivateUsage]
)

from .message_metadata import MessageMetadata


class BitbankMessage[TPayload, TDomainModel](
    Message[MessageMetadata, TPayload, TDomainModel]
):
    """Base class for bitbank :term:`native message`

    Standardizes extraction of success field and retrieval of data field.
    metadata and payload properties are already implemented in base class.
    """

    def _create_metadata(self, json_str: str) -> MessageMetadata:
        """Extract 'success' field from JSON and generate metadata

        :param json_str: API response JSON string
        :return: MessageMetadata instance
        """
        success_match = re.search(r'"success"\s*:\s*(\d+)', json_str)
        if success_match is None:
            raise ValueError(
                f"metadata ('success' field) not found: {json_str}"
            )
        return MessageMetadata(success=int(success_match.group(1)))

    def _extract_payload_json(self, json_str: str) -> str:
        """Extract bitbank 'data' field

        :param json_str: API response JSON string
        :return: Payload portion JSON string (including "data" field)
        """
        return _JsonExtractor.extract_field_with_object(json_str, "data")

    @abstractmethod
    def to_domain_model(self) -> TDomainModel:
        """Convert to domain model

        Subclasses implement specific conversion logic.
        """
        pass
