from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator

from ..native_domain_models.withdrawal_fee import WithdrawalFee


class Asset(BaseModel):
    """:term:`native domain model` representing asset information.

    Models JSON received from :term:`API endpoint` in the following format:

    .. code-block:: json

        {
            "asset": "jpy",
            "amount_precision": 4,
            "onhand_amount": "100000.0000",
            "locked_amount": "0.0000",
            "free_amount": "100000.0000",
            "stop_deposit": false,
            "stop_withdrawal": false,
            "withdrawal_fee": {
                "threshold": "30000.0000",
                "under": "550.0000",
                "over": "770.0000"
            }
        }

    .. seealso::

        `Assets <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#assets>`__
    """

    asset: str
    amount_precision: int = Field(description="Number of decimal places for quantity")
    collateral_ratio: Decimal | None = Field(default=None, description="Collateral ratio")
    onhand_amount: Decimal
    locked_amount: Decimal = Field(description="Locked quantity (in orders, etc.)")
    withdrawing_amount: Decimal | None = Field(
        default=None, description="Quantity being withdrawn"
    )
    free_amount: Decimal
    stop_deposit: bool
    stop_withdrawal: bool
    withdrawal_fee: WithdrawalFee | None = Field(
        default=None,
        description="Withdrawal fee information",
    )
    network_list: list[dict[str, Any]] | None = Field(
        default=None,
        description="Network-specific details (cryptocurrency only)",
    )

    model_config = {"frozen": True}

    @field_validator("collateral_ratio", mode="before")
    @classmethod
    def validate_collateral_ratio(cls, v: Any) -> Decimal | None:
        """Validator to convert string to Decimal type"""
        if v is None:
            return None
        if isinstance(v, Decimal):
            return v
        if isinstance(v, str):
            return Decimal(v)
        # Error for other types
        msg = f"Invalid collateral_ratio type: {type(v)}"
        raise ValueError(msg)
