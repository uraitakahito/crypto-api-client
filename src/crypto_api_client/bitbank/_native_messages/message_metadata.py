"""Common metadata for bitbank API messages"""

from __future__ import annotations

from pydantic import BaseModel


class MessageMetadata(BaseModel):
    """Metadata portion of bitbank API message

    :term:`native message metadata` implementation.
    Contains status information indicating API success/failure.

    bitbank API includes "success" field commonly in all messages.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
                "success": 1,
                "data": {
                    "sell": "15350001",
                    "buy": "15350000",
                    "open": "15572550",
                    "high": "15836477",
                    "low": "15271389",
                    "last": "15350001",
                    "vol": "273.5234",
                    "timestamp": 1748558090326
                }
            }
    """

    success: int

    model_config = {"frozen": True}

    @property
    def json_str(self) -> str:
        """Return MessageMetadata as JSON string

        Returns:
            str: JSON string in '{"success": 1}' format
        """
        return f'{{"success": {self.success}}}'
