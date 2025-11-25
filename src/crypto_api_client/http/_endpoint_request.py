from __future__ import annotations

import json
from typing import Any, Dict

from pydantic import BaseModel, Field, computed_field
from yarl import URL

from crypto_api_client.http._http_method import HttpMethod
from crypto_api_client.security.secret_headers import SecretHeaders


class EndpointRequest(BaseModel):
    """Generic model representing an HTTP request to an :term:`API endpoint`

    The HTTP client receives this model and executes the request.
    Contains all information necessary to send to the :term:`API endpoint`.
    """

    method: HttpMethod
    base_url: URL = Field(
        ..., description=":term:`base URL` (e.g., URL('https://api.bitflyer.jp'))"
    )
    stub_path: URL | None = Field(
        None,
        description=":term:`stub path` (e.g., URL('/v1')). Includes leading slash. Usually represents version number. None if not present",
    )
    relative_resource_path: URL = Field(
        ...,
        description=":term:`relative resource path` (e.g., URL('ticker') or URL('me/sendchildorder'))",
    )
    params: Dict[str, Any] = Field(default_factory=dict, description="URL parameters")
    headers: SecretHeaders = Field(
        default_factory=SecretHeaders, description="HTTP headers"
    )
    body: Dict[str, Any] | None = Field(
        None, description="Request body (sent as JSON)"
    )

    @computed_field
    @property
    def body_json(self) -> str | None:
        """Body converted to JSON string"""
        if self.body is None:
            return None
        return json.dumps(self.body, separators=(",", ":"), ensure_ascii=False)

    @property
    def endpoint_path(self) -> URL:
        """Return :term:`endpoint path`"""
        if self.stub_path:
            return self.stub_path / self.relative_resource_path.path
        else:
            return self.relative_resource_path

    @property
    def api_endpoint(self) -> URL:
        """Return the complete :term:`API endpoint` URL (including parameters)

        :return: Complete :term:`API endpoint` URL (e.g., URL('https://api.bitflyer.jp/v1/ticker?product_code=BTC_JPY'))
        :rtype: yarl.URL
        """
        url = self.base_url.with_path(self.endpoint_path.path)

        if self.params:
            url = url.with_query(**self.params)

        return url

    model_config = {
        "frozen": True,
        "extra": "forbid",
        "arbitrary_types_allowed": True,  # Allow yarl.URL
    }
