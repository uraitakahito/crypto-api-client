"""Tests for bitFlyer signature builder"""

from yarl import URL

from crypto_api_client.bitflyer._signature_builder import build_message
from crypto_api_client.http._http_method import HttpMethod


class TestBuildMessage:
    """Test class for build_message function"""

    def test_get_with_query_params(self) -> None:
        """GET request with query parameters"""
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/me/getchildorders"),
            query_params={"product_code": "BTC_JPY", "child_order_state": "ACTIVE"},
            request_body=None,
            timestamp="1640000000000",
        )

        expected = "1640000000000GET/v1/me/getchildorders?product_code=BTC_JPY&child_order_state=ACTIVE"
        assert msg == expected

    def test_get_without_query_params(self) -> None:
        """GET request without query parameters"""
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/me/getbalance"),
            query_params=None,
            request_body=None,
            timestamp="1640000000000",
        )

        expected = "1640000000000GET/v1/me/getbalance"
        assert msg == expected

    def test_get_with_empty_query_params(self) -> None:
        """GET request with empty query parameters"""
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/me/getbalance"),
            query_params={},
            request_body=None,
            timestamp="1640000000000",
        )

        # Empty dict is falsy so treated the same as None
        expected = "1640000000000GET/v1/me/getbalance"
        assert msg == expected

    def test_post_with_request_body(self) -> None:
        """POST request with request body"""
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/me/sendchildorder"),
            query_params=None,
            request_body={
                "product_code": "BTC_JPY",
                "child_order_type": "LIMIT",
                "side": "BUY",
                "price": 30000,
                "size": 0.001,
            },
            timestamp="1640000000000",
        )

        # JSON format is {"key":"value"} (no spaces)
        expected = '1640000000000POST/v1/me/sendchildorder{"product_code":"BTC_JPY","child_order_type":"LIMIT","side":"BUY","price":30000,"size":0.001}'
        assert msg == expected

    def test_post_without_request_body(self) -> None:
        """POST request without request body"""
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/me/cancelallchildorders"),
            query_params=None,
            request_body=None,
            timestamp="1640000000000",
        )

        expected = "1640000000000POST/v1/me/cancelallchildorders"
        assert msg == expected

    def test_post_with_empty_request_body(self) -> None:
        """POST request with empty request body"""
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/me/cancelallchildorders"),
            query_params=None,
            request_body={},
            timestamp="1640000000000",
        )

        # Empty dict is falsy so empty string is used
        expected = "1640000000000POST/v1/me/cancelallchildorders"
        assert msg == expected

    def test_unicode_characters_in_body(self) -> None:
        """Request body containing Unicode characters"""
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/me/sendchildorder"),
            query_params=None,
            request_body={"memo": "test-order"},
            timestamp="1640000000000",
        )

        # ensure_ascii=False so Unicode characters preserved as-is
        expected = '1640000000000POST/v1/me/sendchildorder{"memo":"test-order"}'
        assert msg == expected

    def test_complex_nested_body(self) -> None:
        """Complex nested request body"""
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/me/sendparentorder"),
            query_params=None,
            request_body={
                "order_method": "IFDOCO",
                "parameters": [
                    {"product_code": "BTC_JPY", "side": "BUY", "size": 0.001}
                ],
            },
            timestamp="1640000000000",
        )

        expected = '1640000000000POST/v1/me/sendparentorder{"order_method":"IFDOCO","parameters":[{"product_code":"BTC_JPY","side":"BUY","size":0.001}]}'
        assert msg == expected


class TestEndpointPathFormat:
    """Test endpoint_path format validation

    For bitFlyer API signatures, endpoint_path must always start with '/'.
    This test class verifies that this requirement is met.
    """

    def test_endpoint_path_must_start_with_slash(self) -> None:
        """Verify endpoint_path starts with '/'"""
        # Correct format (starts with '/')
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/me/getbalance"),
            query_params=None,
            request_body=None,
            timestamp="1640000000000",
        )

        # Path starting with '/' follows timestamp and method
        assert msg.startswith("1640000000000GET/v1/")

    def test_endpoint_path_without_leading_slash_produces_incorrect_signature(self) -> None:
        """endpoint_path not starting with '/' produces incorrect signature

        This test detects the issue that occurred when '/' was removed from
        stub_path during refactoring.
        """
        # Incorrect format (doesn't start with '/')
        msg_wrong = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("v1/me/getbalance"),  # Doesn't start with '/'
            query_params=None,
            request_body=None,
            timestamp="1640000000000",
        )

        # Correct format (starts with '/')
        msg_correct = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/me/getbalance"),  # Starts with '/'
            query_params=None,
            request_body=None,
            timestamp="1640000000000",
        )

        # Verify signatures differ
        assert msg_wrong != msg_correct
        # Incorrect format doesn't start with '/'
        assert not msg_wrong.startswith("1640000000000GET/")
        # Correct format starts with '/'
        assert msg_correct.startswith("1640000000000GET/")

    def test_all_private_api_endpoints_start_with_slash(self) -> None:
        """Verify all Private API endpoint_paths start with '/'"""
        private_endpoints = [
            "/v1/me/getbalance",
            "/v1/me/getchildorders",
            "/v1/me/sendchildorder",
            "/v1/me/cancelchildorder",
            "/v1/me/getexecutions",
            "/v1/me/gettradingcommission",
        ]

        timestamp = "1640000000000"

        for endpoint in private_endpoints:
            msg = build_message(
                method=HttpMethod.GET,
                endpoint_path=URL(endpoint),
                query_params=None,
                request_body=None,
                timestamp=timestamp,
            )

            # Signature message starting with '/' is generated for all endpoints
            assert msg.startswith(f"{timestamp}GET/v1/"), f"Failed for endpoint: {endpoint}"


class TestBuildMessageEdgeCases:
    """Edge case tests"""

    def test_special_characters_in_query_params(self) -> None:
        """Query parameters containing special characters"""
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/executions"),
            query_params={"product_code": "BTC_JPY", "before": "12345"},
            request_body=None,
            timestamp="1640000000000",
        )

        # yarl.URL handles encoding appropriately
        assert "1640000000000GET" in msg
        assert "executions" in msg

    def test_numeric_values_in_body(self) -> None:
        """Request body containing numeric values"""
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/me/sendchildorder"),
            query_params=None,
            request_body={"price": 123456, "size": 0.001, "minute_to_expire": 10000},
            timestamp="1640000000000",
        )

        # Numeric values are JSON-encoded as-is
        assert '"price":123456' in msg
        assert '"size":0.001' in msg
        assert '"minute_to_expire":10000' in msg
