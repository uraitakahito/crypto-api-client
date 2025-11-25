from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class RateLimitType(Enum):
    """Rate limit type

    Defines the three types of rate limits provided by BINANCE.
    """

    REQUEST_WEIGHT = "REQUEST_WEIGHT"
    """Limit based on request weight"""

    ORDERS = "ORDERS"
    """Limit based on number of orders"""

    RAW_REQUESTS = "RAW_REQUESTS"
    """Limit based on raw number of requests"""


class RateLimitInterval(Enum):
    """Rate limit time interval"""

    SECOND = "SECOND"
    """Per second"""

    MINUTE = "MINUTE"
    """Per minute"""

    DAY = "DAY"
    """Per day"""


class RateLimit(BaseModel):
    """Rate limit information

    :term:`native domain model` representing BINANCE rate limit settings.

    :param rateLimitType: Rate limit type
    :type rateLimitType: RateLimitType
    :param interval: Time interval unit
    :type interval: RateLimitInterval
    :param intervalNum: Interval number (e.g., 1 minute, 10 seconds)
    :type intervalNum: int
    :param limit: Limit value
    :type limit: int

    .. note::
        For example, intervalNum=1, interval=MINUTE, limit=1200 means
        "up to 1200 times per minute".
    """

    rateLimitType: RateLimitType
    interval: RateLimitInterval
    intervalNum: int
    limit: int

    model_config = {"frozen": True}
