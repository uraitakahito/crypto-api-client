from __future__ import annotations

from pydantic import BaseModel

from .symbol_filter import SymbolFilter
from .symbol_status import SymbolStatus


class ExchangeSymbol(BaseModel):
    """Trading pair detailed information

    :term:`native domain model` holding comprehensive information about BINANCE trading pairs.

    :param symbol: Symbol name (e.g., "BTCUSDT")
    :type symbol: str
    :param status: Trading status
    :type status: SymbolStatus
    :param baseAsset: Base currency (e.g., "BTC")
    :type baseAsset: str
    :param baseAssetPrecision: Base currency precision
    :type baseAssetPrecision: int
    :param quoteAsset: Quote currency (e.g., "USDT")
    :type quoteAsset: str
    :param quotePrecision: Quote currency precision
    :type quotePrecision: int
    :param quoteAssetPrecision: Quote asset precision
    :type quoteAssetPrecision: int
    :param orderTypes: List of supported order types
    :type orderTypes: list[str]
    :param icebergAllowed: Whether iceberg orders are allowed
    :type icebergAllowed: bool
    :param ocoAllowed: Whether OCO orders are allowed
    :type ocoAllowed: bool
    :param otoAllowed: Whether OTO orders are allowed
    :type otoAllowed: bool
    :param quoteOrderQtyMarketAllowed: Whether market orders by quote quantity are allowed
    :type quoteOrderQtyMarketAllowed: bool
    :param allowTrailingStop: Whether trailing stops are allowed
    :type allowTrailingStop: bool
    :param cancelReplaceAllowed: Whether order cancel-replace is allowed
    :type cancelReplaceAllowed: bool
    :param isSpotTradingAllowed: Whether spot trading is allowed
    :type isSpotTradingAllowed: bool
    :param isMarginTradingAllowed: Whether margin trading is allowed
    :type isMarginTradingAllowed: bool
    :param filters: List of filters applied to this symbol
    :type filters: list[SymbolFilter]
    :param permissions: List of required permissions
    :type permissions: list[str]
    :param permissionSets: Permission sets (expressing OR/AND logic)
    :type permissionSets: list[list[list[str]]] | None
    :param defaultSelfTradePreventionMode: Default self-trade prevention mode
    :type defaultSelfTradePreventionMode: str
    :param allowedSelfTradePreventionModes: List of allowed self-trade prevention modes
    :type allowedSelfTradePreventionModes: list[str]

    .. note::
        **permissionSets logical structure**

        In actual API responses, returned in `list[list[str]]` format:

        - `[["SPOT"]]` → SPOT permission required
        - `[["SPOT", "MARGIN"]]` → SPOT OR MARGIN permission required

    .. seealso::
        `Exchange Information <https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information>`_
    """

    symbol: str
    status: SymbolStatus
    baseAsset: str
    baseAssetPrecision: int
    quoteAsset: str
    quotePrecision: int
    quoteAssetPrecision: int
    orderTypes: list[str]
    icebergAllowed: bool
    ocoAllowed: bool
    otoAllowed: bool
    quoteOrderQtyMarketAllowed: bool
    allowTrailingStop: bool
    cancelReplaceAllowed: bool
    isSpotTradingAllowed: bool
    isMarginTradingAllowed: bool
    filters: list[SymbolFilter]
    permissions: list[str]
    permissionSets: list[list[str]] | None = None
    defaultSelfTradePreventionMode: str
    allowedSelfTradePreventionModes: list[str]

    model_config = {
        "frozen": True,
        "populate_by_name": True,
    }
