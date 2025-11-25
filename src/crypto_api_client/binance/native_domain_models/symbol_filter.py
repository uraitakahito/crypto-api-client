from __future__ import annotations

from pydantic import BaseModel


class SymbolFilter(BaseModel):
    """Filter applied to symbol

    :term:`native domain model` representing various restriction filters applied to BINANCE trading pairs.

    Since there are more than 10 filter types, each with different fields,
    no strict type definition is provided; `extra="allow"` handles this flexibly.

    Main filter types:
        - PRICE_FILTER: Price range restriction
        - LOT_SIZE: Order quantity restriction
        - MIN_NOTIONAL: Minimum order amount
        - ICEBERG_PARTS: Number of iceberg order splits
        - MARKET_LOT_SIZE: Market order quantity restriction
        - MAX_NUM_ORDERS: Maximum number of orders
        - MAX_NUM_ALGO_ORDERS: Maximum number of algo orders
        - And many more...

    :param filterType: String indicating filter type
    :type filterType: str

    .. note::
        This model has `extra="allow"` configured,
        dynamically accepting filterType-specific fields (minPrice, maxPrice, tickSize, etc.).

    .. seealso::
        `Filters <https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#filters>`_

    .. code-block:: json

        {
          "filterType": "PRICE_FILTER",
          "minPrice": "0.00000100",
          "maxPrice": "922327.00000000",
          "tickSize": "0.00000100"
        }
    """

    filterType: str

    model_config = {
        "frozen": True,
        "extra": "allow",  # Allow unknown fields
    }
