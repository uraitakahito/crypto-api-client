from __future__ import annotations

from pydantic import BaseModel

from .health_status_type import HealthStatusType


class HealthStatus(BaseModel):
    """:term:`native domain model` representing bitFlyer exchange operational status.

    Receives JSON from API in the following format:

    .. code-block:: json

        {
            "status": "NORMAL"
        }

    .. warning::

        During scheduled maintenance at 4 AM JST, the status remains NORMAL.
        If you want to detect scheduled maintenance, use BoardState instead.
    """

    status: HealthStatusType

    model_config = {"frozen": True}
