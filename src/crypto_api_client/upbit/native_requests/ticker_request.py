from __future__ import annotations

from pydantic import BaseModel


class TickerRequest(BaseModel):
    """Request to retrieve ticker information."""

    model_config = {"frozen": True}

    markets: str

    def to_query_params(self) -> dict[str, str]:
        """Convert to query parameters."""
        return {"markets": self.markets}
