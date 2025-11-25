from __future__ import annotations

from enum import Enum


class ChildOrderState(Enum):
    """Enum representing order state.

    :param ACTIVE: Order is active.
    :type ACTIVE: ChildOrderState
    :param COMPLETED: Order is completed.
    :type COMPLETED: ChildOrderState
    :param CANCELED: Order is canceled.
    :type CANCELED: ChildOrderState
    :param EXPIRED: Order has expired.
    :type EXPIRED: ChildOrderState
    :param REJECTED: Order is rejected.
    :type REJECTED: ChildOrderState
    """

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
