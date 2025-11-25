"""HTTP method Enum definition"""

from __future__ import annotations

from enum import Enum


class HttpMethod(Enum):
    """Enum representing HTTP methods"""

    GET = "GET"
    POST = "POST"

    def __str__(self) -> str:
        """Return string representation.

        This method must not be deleted.

        Reason:
            It is directly used as str(method) in bitFlyer API signature generation
            (_signature_builder.py).
            Without this method, it would become "HttpMethod.GET" string,
            and correct signature cannot be generated.

        :return: String value of HTTP method ("GET" or "POST")
        :rtype: str
        """
        return self.value
