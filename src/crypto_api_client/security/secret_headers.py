from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any, Final, Generic, Iterable, Iterator, Protocol, TypeVar, cast

import httpx

_KT = TypeVar("_KT")
_VT_co = TypeVar("_VT_co", covariant=True)


class _SupportsKeysAndGetItem(Protocol, Generic[_KT, _VT_co]):
    """Protocol for dict-like objects

    Type of objects that support keys() and __getitem__() methods.
    dict and Mapping are examples.
    """
    def keys(self) -> Iterable[_KT]: ...
    def __getitem__(self, __key: _KT) -> _VT_co: ...


class SecretHeaders(MutableMapping[str, str]):
    """Class to protect sensitive information in HTTP headers

    Automatically masks specified headers while maintaining compatibility
    with httpx.Headers.

    Features:
    - Automatic masking in logs and debug output
    - Mutual conversion support with httpx.Headers
    - Case-insensitive detection
    - Complete implementation of MutableMapping protocol

    .. code-block:: python

        headers = SecretHeaders({"ACCESS-KEY": "sk-1234567890"})
        print(headers)  # {'ACCESS-KEY': '********'}
        headers.to_httpx_headers()  # httpx.Headers with actual values
    """

    # Patterns for sensitive header names (case-insensitive)
    _SENSITIVE_PATTERNS: Final[list[str]] = [
        "ACCESS-KEY",  # bitbank/bitFlyer
        "ACCESS-SIGN",  # bitFlyer
        "ACCESS-SIGNATURE",  # bitbank
        # Not currently used, but kept as sensitive for future compatibility
        "ACCESS-SECRET",
        "API-KEY",
        "API-SECRET",
        "APIKEY",
        "APISECRET",
        "AUTHORIZATION",
        "X-API-KEY",
        "X-API-SECRET",
        "X-AUTH-TOKEN",
        "X-MBX-APIKEY",
        "SIGNATURE",
    ]

    def __init__(self, headers: dict[str, str] | httpx.Headers | None = None) -> None:
        super().__init__()

        # httpx.Headers automatically converts keys to lowercase,
        # so we use a custom dictionary to preserve original keys
        self._data: dict[str, str] = {}
        self._original_keys: dict[
            str, str
        ] = {}  # Mapping from lowercase keys to original keys

        if headers is not None:
            if isinstance(headers, httpx.Headers):
                # Construct from httpx.Headers
                for key in headers:
                    self._data[key.lower()] = headers[key]
                    self._original_keys[key.lower()] = key
            else:
                # Construct from dict
                for key, value in headers.items():
                    self._data[key.lower()] = value
                    self._original_keys[key.lower()] = key

        # Record sensitive header keys (normalized to lowercase)
        self._sensitive_keys: set[str] = set()
        for key in self._data:
            if self._is_sensitive(key):
                self._sensitive_keys.add(key)

    def _is_sensitive(self, key: str) -> bool:
        key_upper = key.upper()
        return any(pattern in key_upper for pattern in self._SENSITIVE_PATTERNS)

    def __delitem__(self, key: str) -> None:
        """Delete a header

        :param key: Header name
        :type key: str
        """
        key_lower = key.lower()
        del self._data[key_lower]
        del self._original_keys[key_lower]
        self._sensitive_keys.discard(key_lower)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SecretHeaders):
            return self._data == other._data
        elif isinstance(other, dict):
            try:
                other_dict = cast(dict[Any, Any], other)
                other_lower: dict[str, str] = {
                    str(k).lower(): str(v) for k, v in other_dict.items()
                }
                return self._data == other_lower
            except (AttributeError, TypeError):
                return False
        elif isinstance(other, httpx.Headers):
            other_lower: dict[str, str] = {k.lower(): v for k, v in other.items()}
            return self._data == other_lower
        return NotImplemented

    def __getitem__(self, key: str) -> str:
        """Get header value (returns actual value)

        :param key: Header name
        :type key: str
        :return: Header value
        :rtype: str
        """
        return self._data[key.lower()]

    def __iter__(self) -> Iterator[str]:
        """Iterate over header keys (returns original key names)

        :return: Iterator of keys
        :rtype: Iterator[str]
        """
        return iter(self._original_keys.values())

    def __len__(self) -> int:
        return len(self._data)

    def __setitem__(self, key: str, value: str) -> None:
        """Set a header

        :param key: Header name
        :type key: str
        :param value: Header value
        :type value: str
        """
        key_lower = key.lower()
        self._data[key_lower] = value
        self._original_keys[key_lower] = key
        if self._is_sensitive(key_lower):
            self._sensitive_keys.add(key_lower)

    def __str__(self) -> str:
        """String representation (sensitive information hidden)

        :return: Masked string representation
        :rtype: str
        """
        safe_headers: dict[str, str] = {}
        for key_lower, original_key in self._original_keys.items():
            value = self._data[key_lower]
            safe_headers[original_key] = self._mask_value(key_lower, value)
        return str(safe_headers)

    def _mask_value(self, key: str, value: str) -> str:
        if key.lower() in self._sensitive_keys:
            if len(value) > 3:
                return f"{value[:3]}{'*' * 8}"
            else:
                return "*" * 10
        return value

    def __repr__(self) -> str:
        return f"SecretHeaders({self.__str__()})"

    def __contains__(self, key: object) -> bool:
        """Check key existence (case-insensitive)

        :param key: Header name
        :type key: object
        :return: True if key exists
        :rtype: bool
        """
        if isinstance(key, str):
            return key.lower() in self._data
        return False

    def copy(self) -> SecretHeaders:
        headers_dict: dict[str, str] = {}
        for key_lower, original_key in self._original_keys.items():
            headers_dict[original_key] = self._data[key_lower]
        return SecretHeaders(headers_dict)

    def get_masked_dict(self) -> dict[str, str]:
        """Get masked dictionary format (for log output)

        :return: Masked dictionary
        :rtype: dict[str, str]
        """
        result: dict[str, str] = {}
        for key_lower, original_key in self._original_keys.items():
            value = self._data[key_lower]
            result[original_key] = self._mask_value(key_lower, value)
        return result

    def to_httpx_headers(self) -> httpx.Headers:
        """Convert to httpx.Headers (used when actually sending requests)

        :return: httpx.Headers with actual values
        :rtype: httpx.Headers
        """
        # Create dictionary with original key names
        headers_dict: dict[str, str] = {}
        for key_lower, original_key in self._original_keys.items():
            headers_dict[original_key] = self._data[key_lower]
        return httpx.Headers(headers_dict)

    def update(
        self,
        __m: _SupportsKeysAndGetItem[str, str] | Iterable[tuple[str, str]] = (),
        /,
        **kwargs: str
    ) -> None:
        """Update headers (MutableMapping compliant)

        Update headers from a dictionary, Mapping, or iterable of (key, value) pairs.
        For httpx.Headers, use update_from_httpx() or convert with dict().

        :param __m: Dictionary, Mapping, or iterable of (key, value) pairs
        :type __m: _SupportsKeysAndGetItem[str, str] | Iterable[tuple[str, str]]
        :param kwargs: Headers specified as keyword arguments
        :type kwargs: str

        Usage examples:
            >>> headers = SecretHeaders()
            >>> headers.update({"Content-Type": "application/json"})
            >>> headers.update([("Accept", "text/html"), ("X-Custom", "value")])
            >>> headers.update(Accept="application/json")

            # When using httpx.Headers
            >>> httpx_headers = httpx.Headers({"X-Custom": "value"})
            >>> headers.update(dict(httpx_headers))
            >>> # or
            >>> headers.update_from_httpx(httpx_headers)
        """
        # Process only if __m is not empty
        if __m:
            # If __m is _SupportsKeysAndGetItem (dict, Mapping, etc.)
            if hasattr(__m, "keys") and hasattr(__m, "__getitem__"):
                obj = cast(_SupportsKeysAndGetItem[str, str], __m)
                for key in obj.keys():
                    value = obj[key]
                    self[key] = value
            # If __m is Iterable[tuple[str, str]]
            else:
                iterable = cast(Iterable[tuple[str, str]], __m)
                for key, value in iterable:
                    self[key] = value

        # Process keyword arguments
        for key, value in kwargs.items():
            self[key] = value

    def update_from_httpx(self, headers: httpx.Headers, **kwargs: str) -> None:
        """Dedicated method to update from httpx.Headers

        Updates headers directly from an httpx.Headers object.
        More explicit intent and type-safe than update() method.

        :param headers: httpx.Headers object
        :type headers: httpx.Headers
        :param kwargs: Additional keyword arguments
        :type kwargs: str

        Usage examples:
            >>> headers = SecretHeaders()
            >>> httpx_headers = httpx.Headers({"X-Custom": "value"})
            >>> headers.update_from_httpx(httpx_headers)
            >>> headers.update_from_httpx(httpx_headers, Accept="application/json")
        """
        for key, value in headers.items():
            self[key] = str(value)
        for key, value in kwargs.items():
            self[key] = value

    @classmethod
    def from_dict(cls, headers: dict[str, str]) -> SecretHeaders:
        return cls(headers)

    @classmethod
    def from_httpx_headers(cls, headers: httpx.Headers) -> SecretHeaders:
        return cls(headers)
