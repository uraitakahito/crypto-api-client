from __future__ import annotations

from pydantic import BaseModel

from .board_state_type import BoardStateType
from .health_status_type import HealthStatusType


class BoardState(BaseModel):
    """:term:`native domain model` representing board state

    Models JSON received from :term:`API endpoint` like the following:

    .. code-block:: json

        {
            "health": "NORMAL",
            "state": "RUNNING"
        }

    .. seealso::

        Orderbook Status: https://lightning.bitflyer.com/docs?lang=en#orderbook-status
    """

    health: HealthStatusType
    state: BoardStateType

    model_config = {"frozen": True}
