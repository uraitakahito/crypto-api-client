from __future__ import annotations

from pydantic import BaseModel


class SpotStatusRequest(BaseModel):
    """:term:`native request` implementation for fetching exchange status

    Represents a request to bitbank's `/v1/spot/status` endpoint.
    No parameters required as it fetches status information for all currency pairs.

    .. seealso::

        `spot/status API <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#status>`__
    """

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Return string for path parameters"""
        return {}
