from __future__ import annotations

import json

from pydantic import BaseModel, ValidationInfo, field_validator


class ExchangeInfoRequest(BaseModel):
    """:term:`native request` implementation for getting Exchange Information

    Corresponds to BINANCE `/api/v3/exchangeInfo` endpoint.
    All parameters are optional. Get all symbol information without specification.

    :param symbol: Specify single symbol (e.g., "BTCUSDT")
    :type symbol: str | None
    :param symbols: Specify multiple symbols (e.g., ["BTCUSDT", "ETHUSDT"])
    :type symbols: list[str] | None
    :param permissions: Filter by permission ("SPOT", "MARGIN", "LEVERAGED", etc.)
    :type permissions: str | None
    :param show_permission_sets: Whether to include permissionSets field
    :type show_permission_sets: bool | None
    :param symbol_status: Filter by status ("TRADING", "HALT", "BREAK")
    :type symbol_status: str | None

    .. warning::
        `symbol`, `symbols`, `permissions` are mutually exclusive.

    .. seealso::
        `Exchange Information <https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information>`_
    """

    symbol: str | None = None
    symbols: list[str] | None = None
    permissions: str | None = None
    show_permission_sets: bool | None = None
    symbol_status: str | None = None

    model_config = {"frozen": True}

    @field_validator("symbols")
    @classmethod
    def validate_symbols_mutual_exclusivity(
        cls, v: list[str] | None, info: ValidationInfo
    ) -> list[str] | None:
        if v is not None:
            if info.data.get("symbol") is not None:
                raise ValueError(
                    "Cannot specify both 'symbol' and 'symbols'. "
                    "These parameters are mutually exclusive."
                )
            if info.data.get("permissions") is not None:
                raise ValueError(
                    "Cannot specify both 'symbols' and 'permissions'. "
                    "These parameters are mutually exclusive."
                )
        return v

    @field_validator("permissions")
    @classmethod
    def validate_permissions_mutual_exclusivity(
        cls, v: str | None, info: ValidationInfo
    ) -> str | None:
        if v is not None:
            if info.data.get("symbol") is not None:
                raise ValueError(
                    "Cannot specify both 'permissions' and 'symbol'. "
                    "These parameters are mutually exclusive."
                )
            if info.data.get("symbols") is not None:
                raise ValueError(
                    "Cannot specify both 'permissions' and 'symbols'. "
                    "These parameters are mutually exclusive."
                )
        return v

    def to_query_params(self) -> dict[str, str]:
        """Return dictionary of str type for :term:`endpoint request`.

        .. note::
            - `symbols` array is converted to JSON array string
        """
        params: dict[str, str] = {}

        if self.symbol is not None:
            params["symbol"] = self.symbol

        if self.symbols is not None:
            # Convert array to JSON string (e.g., ["BTCUSDT","ETHUSDT"])
            params["symbols"] = json.dumps(self.symbols)

        if self.permissions is not None:
            params["permissions"] = self.permissions

        if self.show_permission_sets is not None:
            params["showPermissionSets"] = str(self.show_permission_sets).lower()

        if self.symbol_status is not None:
            params["symbolStatus"] = self.symbol_status

        return params
