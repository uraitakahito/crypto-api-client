from __future__ import annotations

from typing import Any, Dict

from yarl import URL

from crypto_api_client.security.secret_headers import SecretHeaders

from ._endpoint_request import EndpointRequest
from ._http_method import HttpMethod


class EndpointRequestBuilder:
    @staticmethod
    def get(
        base_url: URL,
        relative_stub_path: URL | None,
        relative_resource_path: URL,
        params: Dict[str, Any] | None = None,
        headers: SecretHeaders | None = None,
    ) -> EndpointRequest:
        """Build GET request"""
        stub_path = None
        if relative_stub_path and str(relative_stub_path):
            stub_path = URL("/") / relative_stub_path.path

        return EndpointRequest(
            method=HttpMethod.GET,
            base_url=base_url,
            stub_path=stub_path,
            relative_resource_path=relative_resource_path,
            params=params or {},
            headers=headers or SecretHeaders(),
            body=None,
        )

    @staticmethod
    def post(
        base_url: URL,
        relative_stub_path: URL | None,
        relative_resource_path: URL,
        body: Dict[str, Any] | None = None,
        params: Dict[str, Any] | None = None,
        headers: SecretHeaders | None = None,
    ) -> EndpointRequest:
        """Build POST request"""
        stub_path = None
        if relative_stub_path and str(relative_stub_path):
            stub_path = URL("/") / relative_stub_path.path

        return EndpointRequest(
            method=HttpMethod.POST,
            base_url=base_url,
            stub_path=stub_path,
            relative_resource_path=relative_resource_path,
            params=params or {},
            headers=headers or SecretHeaders(),
            body=body,
        )
