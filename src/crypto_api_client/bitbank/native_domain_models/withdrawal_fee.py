"""Model representing bitbank withdrawal fee information"""

from __future__ import annotations

from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    model_validator,  # pyright: ignore[reportUnknownVariableType]
)


class WithdrawalFee(BaseModel):
    """:term:`native domain model` representing bitbank withdrawal fee information.

    bitbank withdrawal fees have two formats depending on currency type:

    1. Fiat currency (JPY): threshold/under/over format
       - Fee varies based on withdrawal amount threshold

    2. Cryptocurrency: min/max format
       - Fixed fee (usually min and max are the same value)
    """

    # Fields for fiat currency (optional)
    threshold: Decimal | None = Field(
        default=None, description="Threshold where fee changes (for fiat currency)"
    )
    under: Decimal | None = Field(
        default=None, description="Fee for amounts below threshold (for fiat currency)"
    )
    over: Decimal | None = Field(
        default=None, description="Fee for amounts at or above threshold (for fiat currency)"
    )

    # Fields for cryptocurrency (optional)
    min: Decimal | None = Field(default=None, description="Minimum fee (for cryptocurrency)")
    max: Decimal | None = Field(default=None, description="Maximum fee (for cryptocurrency)")

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def validate_fee_structure(self) -> WithdrawalFee:
        """Validate validity of fee structure

        Confirms that only one of fiat currency format (threshold/under/over)
        or cryptocurrency format (min/max) is set.
        """
        has_fiat_fields = (
            self.threshold is not None
            or self.under is not None
            or self.over is not None
        )
        has_crypto_fields = self.min is not None or self.max is not None

        if has_fiat_fields and has_crypto_fields:
            msg = "Cannot have both fiat (threshold/under/over) and crypto (min/max) fee fields"
            raise ValueError(msg)

        if not has_fiat_fields and not has_crypto_fields:
            msg = "Must have either fiat (threshold/under/over) or crypto (min/max) fee fields"
            raise ValueError(msg)

        # For fiat currency format, all fields are required
        if has_fiat_fields and (
            self.threshold is None or self.under is None or self.over is None
        ):
            msg = "All fiat fee fields (threshold/under/over) must be set together"
            raise ValueError(msg)

        # For cryptocurrency format, all fields are required
        if has_crypto_fields and (self.min is None or self.max is None):
            msg = "All crypto fee fields (min/max) must be set together"
            raise ValueError(msg)

        return self
