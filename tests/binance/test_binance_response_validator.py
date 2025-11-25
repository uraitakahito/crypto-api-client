"""Tests for BinanceResponseValidator"""

import pytest

from crypto_api_client.binance.binance_response_validator import (
    BinanceResponseValidator,
)
from crypto_api_client.errors.exceptions import ExchangeApiError
from crypto_api_client.http.http_response_data import HttpResponseData


class TestBinanceResponseValidator:
    """Tests for BinanceResponseValidator"""

    @pytest.fixture
    def validator(self):
        """Validator instance for testing"""
        return BinanceResponseValidator()

    def test_extract_error_info_with_code_and_msg(
        self, validator: BinanceResponseValidator
    ):
        """Verify that code and msg can be correctly extracted"""
        response_body = '{"code": -1121, "msg": "Invalid symbol."}'

        code, message = validator._extract_error_info(response_body)

        assert code == -1121
        assert message == "Invalid symbol."

    def test_extract_error_info_with_only_code(
        self, validator: BinanceResponseValidator
    ):
        """Verify that code-only case can be correctly extracted"""
        response_body = '{"code": -1100}'

        code, message = validator._extract_error_info(response_body)

        assert code == -1100
        assert message is None

    def test_extract_error_info_with_only_msg(
        self, validator: BinanceResponseValidator
    ):
        """Verify that msg-only case can be processed"""
        response_body = '{"msg": "Some error"}'

        code, message = validator._extract_error_info(response_body)

        assert code is None
        assert message == "Some error"

    def test_extract_error_info_with_invalid_code_type(
        self, validator: BinanceResponseValidator
    ):
        """Verify that None is returned when code field has invalid type"""
        response_body = '{"code": "-1121", "msg": "Invalid symbol."}'

        code, message = validator._extract_error_info(response_body)

        assert code is None  # None because not int type
        assert message == "Invalid symbol."

    def test_extract_error_info_with_invalid_msg_type(
        self, validator: BinanceResponseValidator
    ):
        """Verify that None is returned when msg field has invalid type"""
        response_body = '{"code": -1121, "msg": 123}'

        code, message = validator._extract_error_info(response_body)

        assert code == -1121
        assert message is None  # None because not str type

    def test_extract_error_info_with_invalid_json(
        self, validator: BinanceResponseValidator
    ):
        """Verify that (None, None) is returned for invalid JSON"""
        response_body = "not a json"

        code, message = validator._extract_error_info(response_body)

        assert code is None
        assert message is None

    def test_extract_error_info_with_empty_json(
        self, validator: BinanceResponseValidator
    ):
        """Verify that (None, None) is returned for empty JSON"""
        response_body = "{}"

        code, message = validator._extract_error_info(response_body)

        assert code is None
        assert message is None

    def test_extract_error_info_with_positive_code(
        self, validator: BinanceResponseValidator
    ):
        """Verify that positive integer code is also accepted"""
        response_body = '{"code": 1000, "msg": "Success"}'

        code, message = validator._extract_error_info(response_body)

        assert code == 1000
        assert message == "Success"

    async def test_validate_response_raises_exception_with_400_error(
        self, validator: BinanceResponseValidator
    ):
        """Verify that ExchangeApiError is raised for 400 error and includes code and msg fields"""
        response_data = HttpResponseData(
            http_status_code=400,
            headers={},
            url="https://api.binance.com/api/v3/ticker/24hr",
            response_body_text='{"code": -1121, "msg": "Invalid symbol."}',
        )

        with pytest.raises(ExchangeApiError) as exc_info:
            await validator.after_request(response_data)

        exception = exc_info.value
        assert exception.http_status_code == 400
        assert exception.api_status_code_1 == "-1121"  # int is converted to string
        assert exception.api_error_message_1 == "Invalid symbol."
        assert "Binance API error" in exception.error_description
        assert "400" in exception.error_description
        assert "-1121" in exception.error_description
        assert "Invalid symbol." in exception.error_description

    async def test_validate_response_raises_exception_with_401_error(
        self, validator: BinanceResponseValidator
    ):
        """Verify that ExchangeApiError is also raised for 401 error"""
        response_data = HttpResponseData(
            http_status_code=401,
            headers={},
            url="https://api.binance.com/api/v3/account",
            response_body_text='{"code": -2014, "msg": "API-key format invalid."}',
        )

        with pytest.raises(ExchangeApiError) as exc_info:
            await validator.after_request(response_data)

        exception = exc_info.value
        assert exception.http_status_code == 401
        assert exception.api_status_code_1 == "-2014"
        assert exception.api_error_message_1 == "API-key format invalid."

    async def test_validate_response_raises_exception_without_code_field(
        self, validator: BinanceResponseValidator
    ):
        """Verify that error message is extracted even when code field is missing"""
        response_data = HttpResponseData(
            http_status_code=500,
            headers={},
            url="https://api.binance.com/api/v3/ticker/24hr",
            response_body_text='{"msg": "Internal server error"}',
        )

        with pytest.raises(ExchangeApiError) as exc_info:
            await validator.after_request(response_data)

        exception = exc_info.value
        assert exception.http_status_code == 500
        assert exception.api_status_code_1 is None  # No code field
        assert exception.api_error_message_1 == "Internal server error"

    async def test_validate_response_no_error_on_success(
        self, validator: BinanceResponseValidator
    ):
        """Verify that no exception is raised for 200 response"""
        response_data = HttpResponseData(
            http_status_code=200,
            headers={},
            url="https://api.binance.com/api/v3/ticker/24hr",
            response_body_text='{"symbol": "BTCUSDT", "lastPrice": "50000.00"}',
        )

        # Verify that no exception is raised
        await validator.after_request(response_data)

    async def test_validate_response_with_malformed_json(
        self, validator: BinanceResponseValidator
    ):
        """Verify that ExchangeApiError is raised even for malformed JSON"""
        response_data = HttpResponseData(
            http_status_code=500,
            headers={},
            url="https://api.binance.com/api/v3/ticker/24hr",
            response_body_text="not a json",
        )

        with pytest.raises(ExchangeApiError) as exc_info:
            await validator.after_request(response_data)

        exception = exc_info.value
        assert exception.http_status_code == 500
        assert exception.api_status_code_1 is None  # Parse failed
        assert exception.api_error_message_1 is None  # Parse failed

    async def test_validate_response_preserves_response_body(
        self, validator: BinanceResponseValidator
    ):
        """Verify that response body is included in exception"""
        response_body = '{"code": -1000, "msg": "An unknown error occurred"}'
        response_data = HttpResponseData(
            http_status_code=500,
            headers={},
            url="https://api.binance.com/api/v3/ticker/24hr",
            response_body_text=response_body,
        )

        with pytest.raises(ExchangeApiError) as exc_info:
            await validator.after_request(response_data)

        exception = exc_info.value
        assert exception.response_body == response_body
