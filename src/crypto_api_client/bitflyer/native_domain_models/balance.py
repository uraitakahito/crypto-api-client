from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class Balance(BaseModel):
    """:term:`native domain model` representing balance information.

    Models JSON received from :term:`API endpoint` like the following:

    .. code-block:: json

        {
            "currency_code": "JPY",
            "amount": 100000.0,
            "available": 10000.000000000000
        }

    .. seealso::

        `Get Account Asset Balance <https://lightning.bitflyer.com/docs?lang=en#get-account-asset-balance>`__
    """

    currency_code: str
    amount: Decimal
    available: Decimal

    model_config = {"frozen": True}
