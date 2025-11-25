from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property


class Message[TMetadata, TPayload, TDomainModel](ABC):
    """Abstract base class for all :term:`native message` implementations

    Defines the common interface that message classes for each exchange must implement.

    :param TMetadata: Type of metadata (can be None)
    :param TPayload: Type of payload
    :param TDomainModel: Return type of to_domain_model()

    .. note::

        ``metadata`` and ``payload`` are implemented with ``@cached_property``,
        generated on first access, and subsequently retrieved from cache.
    """

    def __init__(self, json_str: str):
        """Initialize message from JSON response string

        :param json_str: JSON string of API response
        :type json_str: str
        """
        self._json_str = json_str

    @cached_property
    def metadata(self) -> TMetadata:
        """Get metadata (generated on first access, cached thereafter)

        :return: Metadata (None for some exchanges)
        :rtype: TMetadata
        """
        return self._create_metadata(self._json_str)

    @cached_property
    def payload(self) -> TPayload:
        """Get payload (generated on first access, cached thereafter)

        :return: payload
        :rtype: TPayload
        """
        payload_json_str = self._extract_payload_json(self._json_str)
        return self._create_payload(payload_json_str)

    @abstractmethod
    def _create_metadata(self, json_str: str) -> TMetadata:
        """Implement in subclass: Generate metadata

        :param json_str: JSON string of entire API response
        :return: Metadata instance (None if no metadata)

        Implementation examples:

        **Without metadata (bitFlyer, BINANCE, Coincheck)**::

            def _create_metadata(self, json_str: str) -> None:
                return None

        **With metadata (bitbank)**::

            def _create_metadata(self, json_str: str) -> MessageMetadata:
                success_match = re.search(r'"success"\\s*:\\s*(\\d+)', json_str)
                if success_match is None:
                    raise ValueError("'success' field not found")
                return MessageMetadata(success=int(success_match.group(1)))

        **With metadata - multiple fields (GMO Coin)**::

            def _create_metadata(self, json_str: str) -> MessageMetadata:
                status_match = re.search(r'"status"\\s*:\\s*(\\d+)', json_str)
                responsetime_match = re.search(r'"responsetime"\\s*:\\s*"([^"]+)"', json_str)
                if not status_match or not responsetime_match:
                    raise ValueError("Metadata fields not found")
                return MessageMetadata(
                    status=int(status_match.group(1)),
                    responsetime=responsetime_match.group(1)
                )
        """
        pass

    @abstractmethod
    def _extract_payload_json(self, json_str: str) -> str:
        """Implement in subclass: Extract payload portion from JSON string

        :param json_str: JSON string of entire API response
        :return: JSON string of payload portion

        Implementation examples:

        **Without metadata (bitFlyer, BINANCE)**::

            def _extract_payload_json(self, json_str: str) -> str:
                # Entire response is payload
                return json_str

        **With metadata (bitbank, Coincheck, GMO Coin)**::

            def _extract_payload_json(self, json_str: str) -> str:
                # Extract JSON string including "data" field
                return _JsonExtractor.extract_field_with_object(json_str, "data")
        """
        pass

    @abstractmethod
    def _create_payload(self, payload_json_str: str) -> TPayload:
        """Implement in subclass: Generate payload

        :param payload_json_str: JSON string of payload portion
        :return: Payload instance

        .. note::

            The content of payload_json_str varies by exchange:

            **With metadata (bitbank, GMO Coin):**

            payload_json_str contains a JSON string including the "data" field.

            Example (bitbank)::

                # Full API response:
                '{"success": 1, "data": {"sell": "100", "buy": "99"}}'

                # payload_json_str (including "data" field):
                '"data": {"sell": "100", "buy": "99"}'

            **Without metadata (bitFlyer, BINANCE, Coincheck):**

            Since the entire API response is the payload,
            payload_json_str contains the entire response.

            Example (bitFlyer)::

                # Full API response = payload_json_str:
                '{"product_code": "BTC_JPY", "ltp": 100, "timestamp": "..."}'

        .. seealso::

            Implementation examples:

            - :class:`~crypto_api_client.bitflyer._native_messages.TickerMessage`
            - :class:`~crypto_api_client.bitbank._native_messages.TickerMessage`

        .. hint::

            Common implementation pattern::

                def _create_payload(self, payload_json_str: str) -> TickerPayload:
                    return TickerPayload(payload_json_str)
        """
        pass

    @abstractmethod
    def to_domain_model(self) -> TDomainModel:
        """Convert to domain model

        Generates a :term:`native domain model` from :term:`payload content`.

        .. note::

            The return type is specified by the type parameter ``TDomainModel``.

            - Single domain model (e.g., ``Ticker``)
            - List of domain models (e.g., ``list[Balance]``)
            - Union type (e.g., ``Union[Ticker, list[Ticker]]``)
            - None (e.g., ``CancelChildOrderMessage``)
            - str (e.g., ``SendChildOrderMessage``)

        :return: Type-safe domain model
        :rtype: TDomainModel
        """
        pass
