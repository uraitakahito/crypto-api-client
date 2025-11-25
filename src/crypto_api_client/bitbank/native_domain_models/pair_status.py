from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from .spot_status_type import SpotStatusType


class PairStatus(BaseModel):
    """:term:`native domain model` representing status information for each currency pair

    Models currency pair status information received from :term:`API endpoint`.

    .. code-block:: json

        {
            "pair": "btc_jpy",
            "status": "NORMAL",
            "min_amount": "0.0001"
        }

    :param pair: Currency pair (e.g. "btc_jpy", "eth_jpy")
    :type pair: str
    :param status: Exchange status
    :type status: SpotStatusType
    :param min_amount: Minimum order quantity based on current status
    :type min_amount: Decimal
    """

    pair: str
    status: SpotStatusType
    min_amount: Decimal

    model_config = {"frozen": True}
