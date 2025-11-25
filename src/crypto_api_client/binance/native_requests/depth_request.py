from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class DepthRequest(BaseModel):
    """:term:`native request` implementation for getting Depth.

    Corresponds to BINANCE `/api/v3/depth` endpoint.

    .. note::

        API Weight (rate limit) varies by limit parameter:
        - limit [1,100]: Weight 5
        - limit [101,500]: Weight 25
        - limit [501,1000]: Weight 50
        - limit [1001,5000]: Weight 250

    .. seealso::

        `Market Data endpoints <https://developers.binance.com/docs/binance-spot-api-docs/testnet/rest-api/market-data-endpoints>`__

    :param symbol: Target symbol (e.g., "BTCUSDT")
    :type symbol: str
    :param limit: Depth to retrieve (default: 100, max: 5000)
    :type limit: int | None
    """

    symbol: str
    limit: int | None = Field(None, ge=1, le=5000)

    model_config = {"frozen": True}

    @field_validator("limit", mode="before")
    @classmethod
    def validate_limit(cls, v: int | None) -> int | None:
        """Validate limit value

        :param v: limit value
        :type v: int | None
        :return: Validated limit value
        :rtype: int | None
        """
        if v is not None:
            if v < 1:
                raise ValueError(f"limit must be >= 1, got {v}")
            if v > 5000:
                raise ValueError(f"limit must be <= 5000, got {v}")
        return v

    def to_query_params(self) -> dict[str, str]:
        """Return dictionary of str type for :term:`endpoint request`."""
        # Required parameter
        result = {"symbol": self.symbol}

        # Conditional parameter
        if self.limit is not None:
            result["limit"] = str(self.limit)

        return result
