"""Order book fetch request"""

from __future__ import annotations

from pydantic import BaseModel


class DepthRequest(BaseModel):
    """:term:`native request` implementation for fetching order book (Depth).

    .. seealso::

        `Depth <https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-api.md#depth>`__

    :param pair: Currency pair (e.g. "btc_jpy")
    :type pair: str
    """

    pair: str

    model_config = {"frozen": True}

    def get_pair_value(self) -> str:
        """Return valid pair"""
        return self.pair
