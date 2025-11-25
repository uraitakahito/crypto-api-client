"""Common message metadata"""

from __future__ import annotations

from pydantic import BaseModel


class MessageMetadata(BaseModel):
    """Message metadata part

    Implementation of :term:`native message metadata`.
    Contains status information indicating API success/failure and message timestamp.

    All messages include "status" and "responsetime" fields in common.

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
    """

    status: int
    responsetime: str

    model_config = {"frozen": True}

    @property
    def json_str(self) -> str:
        """Return MessageMetadata as JSON string

        Returns:
            str: JSON string in '{"status": 0, "responsetime": "2025-01-30T12:34:56.789Z"}' format
        """
        return f'{{"status": {self.status}, "responsetime": "{self.responsetime}"}}'
