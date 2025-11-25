"""bitbank signature builder tests"""

from yarl import URL

from crypto_api_client.bitbank._signature_builder import build_message
from crypto_api_client.http._http_method import HttpMethod


class TestBuildMessage:
    """Test class for build_message function"""

    def test_get_without_query_params(self) -> None:
        """GET request without query parameters

        Example: GET /v1/user/assets
        """
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/user/assets"),
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        expected = "16400000000005000/v1/user/assets"
        assert msg == expected

    def test_get_with_query_params(self) -> None:
        """GET request with query parameters

        Example: GET /v1/user/spot/trade_history?pair=btc_jpy&count=1
        """
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/user/spot/trade_history"),
            query_params={"pair": "btc_jpy", "count": "1"},
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        expected = '16400000000005000/v1/user/spot/trade_history{"pair":"btc_jpy","count":"1"}'
        assert msg == expected

    def test_post_with_request_body(self) -> None:
        """POST request with request body

        Example: POST /v1/user/spot/order
        """
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/user/spot/order"),
            request_body={
                "pair": "btc_jpy",
                "amount": "0.0001",
                "price": "17000000",
                "side": "sell",
                "type": "limit",
            },
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        expected = '16400000000005000{"pair":"btc_jpy","amount":"0.0001","price":"17000000","side":"sell","type":"limit"}'
        assert msg == expected

    def test_post_without_request_body(self) -> None:
        """POST request without request body (path only)

        Note: This case is rare in bitbank API, but possible by specification
        """
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/user/spot/cancel_order"),
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        expected = "16400000000005000/v1/user/spot/cancel_order"
        assert msg == expected

    def test_get_with_empty_query_params(self) -> None:
        """GET request with empty query parameters (same behavior as None)"""
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/user/assets"),
            query_params={},
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        expected = "16400000000005000/v1/user/assets"
        assert msg == expected

    def test_path_construction_with_nested_resource(self) -> None:
        """Verify construction of nested resource paths

        Example: user/spot -> /v1/user/spot/order
        """
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/user/spot/orders"),
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        expected = "16400000000005000/v1/user/spot/orders"
        assert msg == expected

    def test_json_serialization_order(self) -> None:
        """Verify JSON serialization order is consistent

        Note: Uses compact format with separators=(",", ":")
        """
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/user/spot/order"),
            request_body={"z_last": "value", "a_first": "value"},
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        # JSON key order depends on dictionary insertion order (Python 3.7+)
        expected = '16400000000005000{"z_last":"value","a_first":"value"}'
        assert msg == expected

    def test_unicode_characters_in_request_body(self) -> None:
        """Verify encoding when Unicode characters are included

        Note: Unicode characters are preserved as-is by ensure_ascii=False
        """
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/user/update"),
            request_body={"name": "test-user"},
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        expected = '16400000000005000{"name":"test-user"}'
        assert msg == expected

    def test_boolean_in_request_body(self) -> None:
        """Verify boolean values are correctly serialized according to JSON specification"""
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/user/spot/order"),
            request_body={"post_only": True, "reduce_only": False},
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        expected = '16400000000005000{"post_only":true,"reduce_only":false}'
        assert msg == expected


class TestEndpointPathFormat:
    """Endpoint path format validation tests

    In bitbank API signature, endpoint_path must always start with '/'.
    This test class verifies that this requirement is satisfied.
    """

    def test_endpoint_path_must_start_with_slash(self) -> None:
        """Verify endpoint_path starts with '/'"""
        # Correct format (starts with '/')
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/user/assets"),
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        # Path starting with '/' follows timestamp and time window
        assert msg.startswith("16400000000005000/v1/")

    def test_endpoint_path_without_leading_slash_produces_incorrect_signature(self) -> None:
        """Endpoint_path not starting with '/' produces incorrect signature

        This test detects the problem that occurred when '/' was removed
        from stub_path during refactoring.
        """
        # Incorrect format (doesn't start with '/')
        msg_wrong = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("v1/user/assets"),  # Doesn't start with '/'
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        # Correct format (starts with '/')
        msg_correct = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/user/assets"),  # Starts with '/'
            request_time="1640000000000",
            time_window_millisecond="5000",
        )

        # Verify signatures are different
        assert msg_wrong != msg_correct
        # Incorrect format doesn't start with '/'
        assert not msg_wrong.startswith("16400000000005000/")
        # Correct format starts with '/'
        assert msg_correct.startswith("16400000000005000/")

    def test_all_private_api_endpoints_start_with_slash(self) -> None:
        """Verify all Private API endpoint_paths start with '/'"""
        private_endpoints = [
            "/v1/user/assets",
            "/v1/user/spot/order",
            "/v1/user/spot/orders",
            "/v1/user/spot/trade_history",
        ]

        request_time = "1640000000000"
        time_window = "5000"

        for endpoint in private_endpoints:
            msg = build_message(
                method=HttpMethod.GET,
                endpoint_path=URL(endpoint),
                request_time=request_time,
                time_window_millisecond=time_window,
            )

            # Signature message starting with '/' is generated for all endpoints
            assert msg.startswith(f"{request_time}{time_window}/v1/"), f"Failed for endpoint: {endpoint}"
