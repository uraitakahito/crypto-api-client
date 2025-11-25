from __future__ import annotations

from pydantic import (
    BaseModel,
    model_validator,  # pyright: ignore[reportUnknownVariableType]
)


class CancelChildOrderRequest(BaseModel):
    """:term:`native request` implementation for canceling an order.

    Either child_order_id or child_order_acceptance_id is required.

    :param product_code: Product code for the trading pair (e.g. "BTC_JPY")
    :type product_code: str
    :param child_order_id: ID of the order to cancel. e.g. "JOR20250228-192028-832244"
    :type child_order_id: str | None
    :param child_order_acceptance_id: Acceptance ID of the order to cancel. e.g. "JRF20250228-192028-006028"
    :type child_order_acceptance_id: str | None
    """

    product_code: str
    child_order_id: str | None = None
    child_order_acceptance_id: str | None = None

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def validate_order_identifiers(self) -> CancelChildOrderRequest:
        """Validate order identifiers

        Either child_order_id or child_order_acceptance_id is required
        """
        if not self.child_order_id and not self.child_order_acceptance_id:
            raise ValueError(
                "Either child_order_id or child_order_acceptance_id is required"
            )

        return self

    def to_query_params(self) -> dict[str, str]:
        """Return all-string dictionary for API request."""
        # Required parameters
        result = {"product_code": self.product_code}

        # Optional parameters
        optional_params = {
            "child_order_id": self.child_order_id,
            "child_order_acceptance_id": self.child_order_acceptance_id,
        }
        result.update({k: v for k, v in optional_params.items() if v is not None})

        return result
