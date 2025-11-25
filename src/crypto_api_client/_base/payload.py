"""Base class for :term:`native message payload`

Holds JSON strings and provides processing as needed.
"""


from __future__ import annotations


class Payload:
    """Base class for all :term:`native message payload` implementations

    Holds JSON strings and processes them as needed before returning.
    The default implementation returns the JSON string as-is.

    Subclasses can customize in the following ways:

    **Pattern 1: Use default implementation (simplest)**

    If returning the JSON string as-is, no override is needed.
    Implementation complete with class definition only::

        class SimplePayload(Payload):
            \"\"\"docstring\"\"\"
            pass  # Use default implementation

    **Pattern 2: When extraction is needed**

    When extracting a portion from the JSON string using `_JsonExtractor`,
    override only the `content_str` property::

        class ExtractingPayload(Payload):
            \"\"\"docstring\"\"\"

            @property
            def content_str(self) -> str:
                return _JsonExtractor.extract_object(self._json_str)

    **Pattern 3: When complex processing is needed**

    When multi-stage extraction or custom logic is required,
    override the `content_str` property::

        class ComplexPayload(Payload):
            \"\"\"docstring\"\"\"

            @property
            def content_str(self) -> str:
                # Stage 1: Extract object
                obj = _JsonExtractor.extract_object(self._json_str)
                # Stage 2: Extract array
                start_pos = obj.find('"assets"')
                return _JsonExtractor.extract_array(obj, start_pos=start_pos)
    """

    def __init__(self, json_str: str) -> None:
        """Initialize :term:`native message payload`

        :param json_str: JSON string of payload portion
        :type json_str: str
        """
        self._json_str = json_str

    @property
    def content_str(self) -> str:
        """Return JSON string of :term:`payload content`

        By default, returns the JSON string passed at initialization as-is.
        Override this property in subclasses if extraction or processing is needed.

        :return: JSON string of payload content
        :rtype: str

        .. seealso::

            - :class:`crypto_api_client.core.json_extractor._JsonExtractor`
        """
        return self._json_str

    @property
    def raw_json(self) -> str:
        """Return original JSON string

        Returns the raw JSON string passed at initialization, before any processing by `content_str`.
        Useful for debugging and logging.

        :return: Raw JSON string passed at initialization
        :rtype: str
        """
        return self._json_str
