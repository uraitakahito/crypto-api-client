from __future__ import annotations

from datetime import timedelta

from pydantic import BaseModel, ConfigDict, Field


class HttpResponseData(BaseModel):
    """Pydantic model for :term:`http response data`

    Represents HTTP response data converted from httpx.Response.
    Provides runtime type checking and validation.

    .. seealso::
        :class:`~crypto_api_client.http_status_code.HttpStatusCode`
            Constants and helper methods for standard/non-standard HTTP status codes
    """

    model_config = ConfigDict(
        frozen=True,  # Ensure immutability
    )

    #
    # Required fields
    #

    # HTTP status code unified as int type
    # Reason: To handle non-standard status codes (CloudFlare 520-527, nginx 499, etc.)
    # without information loss. See HttpStatusCode class for details.
    http_status_code: int

    # Important: httpx normalizes HTTP header names to lowercase.
    # Example: "X-RateLimit-Remaining" -> "x-ratelimit-remaining"
    # Always specify headers in lowercase when retrieving them.
    headers: dict[str, str]
    response_body_text: str
    url: str

    #
    # Optional fields
    #
    response_body_bytes: bytes | None = None
    reason: str | None = None
    elapsed: timedelta | None = Field(default=None, description="Request processing time")
    cookies: dict[str, str] = Field(default_factory=dict)
    encoding: str | None = None
    request_method: str = Field(default="")
    request_url: str = Field(default="")
    request_path: str = Field(default="")
