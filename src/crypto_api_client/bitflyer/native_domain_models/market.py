from __future__ import annotations

from pydantic import BaseModel

from .market_type import MarketType


class Market(BaseModel):
    """:term:`native domain model` representing bitFlyer market information.

    Receives JSON from API in the following format:

    .. code-block:: json

        {
            "product_code": "BTC_JPY",
            "market_type": "Spot"
        }
    """

    product_code: str
    market_type: MarketType

    model_config = {"frozen": True}
