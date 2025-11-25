from __future__ import annotations

import re
from abc import abstractmethod

from crypto_api_client._base import Message

from .message_metadata import MessageMetadata


class GmoCoinMessage[TPayload, TDomainModel](
    Message[MessageMetadata, TPayload, TDomainModel]
):
    """Base class for GMO Coin :term:`native message`

    Standardizes extraction of status and responsetime fields and retrieval of data field.
    metadata and payload properties are already implemented in the base class.
    """

    def _create_metadata(self, json_str: str) -> MessageMetadata:
        """Generate metadata from GMO Coin 'status' and 'responsetime' fields

        :param json_str: JSON string of API response
        :return: MessageMetadata instance
        :raises ValueError: If status or responsetime field is not found
        """
        # Extract status field
        status_match = re.search(r'"status"\s*:\s*(\d+)', json_str)
        if status_match is None:
            raise ValueError(
                f"metadata ('status' field) not found: {json_str}"
            )

        # Extract responsetime field
        responsetime_match = re.search(r'"responsetime"\s*:\s*"([^"]+)"', json_str)
        if responsetime_match is None:
            raise ValueError(
                f"metadata ('responsetime' field) not found: {json_str}"
            )

        return MessageMetadata(
            status=int(status_match.group(1)),
            responsetime=responsetime_match.group(1)
        )

    def _extract_payload_json(self, json_str: str) -> str:
        """Extract GMO Coin 'data' field

        :param json_str: Entire API response JSON string
        :return: Payload portion ('"data": [...] or "data": {...}' format)
        :raises ValueError: If 'data' field is not found

        .. note::

            Example: Extract '"data": [...]' from '{"status": 0, "data": [...], "responsetime": "..."}'

            GMO Coin API responses have the following format:

            .. code-block:: json

                {
                    "status": 0,
                    "data": [...],
                    "responsetime": "2025-01-30T12:34:56.789Z"
                }

            This function extracts the "data": [...] portion.
        """
        # Find content after "data":
        data_match = re.search(r'"data"\s*:\s*', json_str)
        if data_match is None:
            raise ValueError(f"'data' field not found: {json_str}")

        # Get position where "data": starts
        start_pos = data_match.start()

        # data_match.end() is the position after :
        # Find start position of array [ or object {
        value_start = data_match.end()

        # Skip whitespace
        while value_start < len(json_str) and json_str[value_start].isspace():
            value_start += 1

        if value_start >= len(json_str):
            raise ValueError(f"'data' field value not found: {json_str}")

        # Find end position of array or object
        if json_str[value_start] == "[":
            # Array case
            depth = 0
            for i in range(value_start, len(json_str)):
                if json_str[i] == "[":
                    depth += 1
                elif json_str[i] == "]":
                    depth -= 1
                    if depth == 0:
                        return json_str[start_pos : i + 1]
            raise ValueError(f"'data' array end not found: {json_str}")
        elif json_str[value_start] == "{":
            # Object case
            depth = 0
            for i in range(value_start, len(json_str)):
                if json_str[i] == "{":
                    depth += 1
                elif json_str[i] == "}":
                    depth -= 1
                    if depth == 0:
                        return json_str[start_pos : i + 1]
            raise ValueError(f"'data' object end not found: {json_str}")
        else:
            raise ValueError(
                f"'data' field value is not an array or object: {json_str[value_start:value_start+10]}"
            )

    @abstractmethod
    def to_domain_model(self) -> TDomainModel:
        """Convert to domain model

        Subclasses implement specific conversion logic.
        """
        pass
