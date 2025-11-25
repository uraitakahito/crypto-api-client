"""JSON parser that preserves Decimal precision

This module converts JSON to Pydantic models while preserving
numerical precision, which is critical for cryptocurrency exchange APIs.
"""

from __future__ import annotations

# ruff: noqa: ANN401
import json
from decimal import Decimal
from typing import Any, ClassVar, cast

from pydantic import TypeAdapter


class DecimalJsonParser:
    """JSON parser that preserves Decimal precision

    Converts JSON to Pydantic models while preserving
    numerical precision, which is critical for cryptocurrency exchange APIs.

    Features:
        - Parses floating-point numbers as Decimal type (precision preservation)
        - Performance optimization through TypeAdapter caching
        - Type-safe conversion

    .. code-block:: python

       ticker = DecimalJsonParser.parse(json_str, Ticker)
    """

    _adapter_cache: ClassVar[dict[type, TypeAdapter[Any]]] = {}

    @classmethod
    def parse[T](cls, json_str: str, model_type: type[T]) -> T:
        """Convert JSON string to model instance

        :param json_str: JSON string
        :type json_str: str
        :param model_type: Target Pydantic model type
        :type model_type: type[T]
        :return: Model instance
        :rtype: T
        """
        #
        # Parse JSON using Decimal type (preserve precision)
        #
        # NOTE:
        #
        #   Since Pydantic doesn't support JSON parsing with Decimal, we don't use
        #   the standard Pydantic method:
        #
        #     Ticker.model_validate_json(json_str)
        #
        #   Reference: https://docs.pydantic.dev/latest/api/type_adapter/#pydantic.type_adapter.TypeAdapter.validate_json
        #
        adapter = cls._get_or_create_adapter(model_type)
        python_obj = json.loads(json_str, parse_float=Decimal, parse_int=Decimal)
        return cast(T, adapter.validate_python(python_obj))

    @classmethod
    def _get_or_create_adapter(cls, model_type: type) -> TypeAdapter[Any]:
        """Get TypeAdapter (reuse from cache if available)

        :param model_type: Target Pydantic model type
        :type model_type: type
        :return: Cached TypeAdapter
        :rtype: TypeAdapter[Any]
        """
        if model_type not in cls._adapter_cache:
            cls._adapter_cache[model_type] = TypeAdapter(model_type)
        return cls._adapter_cache[model_type]

    @classmethod
    def clear_cache(cls) -> None:
        """Clear adapter cache

        Use this during testing or when memory management is needed.

        :rtype: None
        """
        cls._adapter_cache.clear()
