"""Tests for CoincheckResponseValidator"""

import pytest

from crypto_api_client.coincheck.coincheck_response_validator import (
    CoincheckResponseValidator,
)
from crypto_api_client.errors.exceptions import ExchangeApiError
from crypto_api_client.http.http_response_data import HttpResponseData


class TestCoincheckResponseValidator:
    """Tests for CoincheckResponseValidator"""

    @pytest.fixture
    def validator(self):
        """Validator instance for testing"""
        return CoincheckResponseValidator()

    def test_extract_error_info_with_success_false_and_error_message(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that success: false and error message can be correctly extracted"""
        response_body = '{"success": false, "error": "invalid authentication"}'

        success, error_message = validator._extract_error_info(response_body)

        assert success is False
        assert error_message == "invalid authentication"

    def test_extract_error_info_with_success_true(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that success: true case can be correctly extracted"""
        response_body = '{"success": true, "data": {"jpy": "100000"}}'

        success, error_message = validator._extract_error_info(response_body)

        assert success is True
        assert error_message is None

    def test_extract_error_info_with_only_error(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that error-only field case can be processed"""
        response_body = '{"error": "some error"}'

        success, error_message = validator._extract_error_info(response_body)

        assert success is None
        assert error_message == "some error"

    def test_extract_error_info_with_only_success(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that success-only field case can be processed"""
        response_body = '{"success": false}'

        success, error_message = validator._extract_error_info(response_body)

        assert success is False
        assert error_message is None

    def test_extract_error_info_with_invalid_success_type(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that None is returned when success field has invalid type"""
        response_body = '{"success": "false", "error": "some error"}'

        success, error_message = validator._extract_error_info(response_body)

        assert success is None  # None because not boolean type
        assert error_message == "some error"

    def test_extract_error_info_with_invalid_error_type(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that None is returned when error field has invalid type"""
        response_body = '{"success": false, "error": 123}'

        success, error_message = validator._extract_error_info(response_body)

        assert success is False
        assert error_message is None  # None because not string type

    def test_extract_error_info_with_invalid_json(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that (None, None) is returned for invalid JSON"""
        response_body = "not a json"

        success, error_message = validator._extract_error_info(response_body)

        assert success is None
        assert error_message is None

    def test_extract_error_info_with_empty_json(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that (None, None) is returned for empty JSON"""
        response_body = "{}"

        success, error_message = validator._extract_error_info(response_body)

        assert success is None
        assert error_message is None

    async def test_validate_response_raises_exception_with_401_error(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that ExchangeApiError is raised for 401 error and includes success field"""
        response_data = HttpResponseData(
            http_status_code=401,
            headers={},
            url="https://coincheck.com/api/accounts/balance",
            response_body_text='{"success": false, "error": "invalid authentication"}',
        )

        with pytest.raises(ExchangeApiError) as exc_info:
            await validator.after_request(response_data)

        exception = exc_info.value
        assert exception.http_status_code == 401
        assert exception.api_status_code_1 == "False"  # boolean is converted to string
        assert exception.api_error_message_1 == "invalid authentication"
        assert "Coincheck API error" in exception.error_description
        assert "401" in exception.error_description
        assert "invalid authentication" in exception.error_description

    async def test_validate_response_raises_exception_with_400_error(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that ExchangeApiError is also raised for 400 error"""
        response_data = HttpResponseData(
            http_status_code=400,
            headers={},
            url="https://coincheck.com/api/accounts/balance",
            response_body_text='{"success": false, "error": "bad request"}',
        )

        with pytest.raises(ExchangeApiError) as exc_info:
            await validator.after_request(response_data)

        exception = exc_info.value
        assert exception.http_status_code == 400
        assert exception.api_status_code_1 == "False"
        assert exception.api_error_message_1 == "bad request"

    async def test_validate_response_raises_exception_without_success_field(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that error message is extracted even when success field is missing"""
        response_data = HttpResponseData(
            http_status_code=500,
            headers={},
            url="https://coincheck.com/api/accounts/balance",
            response_body_text='{"error": "internal server error"}',
        )

        with pytest.raises(ExchangeApiError) as exc_info:
            await validator.after_request(response_data)

        exception = exc_info.value
        assert exception.http_status_code == 500
        assert exception.api_status_code_1 is None  # No success field
        assert exception.api_error_message_1 == "internal server error"

    async def test_validate_response_no_error_on_success(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that no exception is raised for 200 response"""
        response_data = HttpResponseData(
            http_status_code=200,
            headers={},
            url="https://coincheck.com/api/accounts/balance",
            response_body_text='{"success": true, "data": {"jpy": "100000"}}',
        )

        # Verify that no exception is raised
        await validator.after_request(response_data)

    async def test_validate_response_with_malformed_json(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that ExchangeApiError is raised even for malformed JSON"""
        response_data = HttpResponseData(
            http_status_code=500,
            headers={},
            url="https://coincheck.com/api/accounts/balance",
            response_body_text="not a json",
        )

        with pytest.raises(ExchangeApiError) as exc_info:
            await validator.after_request(response_data)

        exception = exc_info.value
        assert exception.http_status_code == 500
        assert exception.api_status_code_1 is None  # Parse failed
        assert exception.api_error_message_1 is None  # Parse failed

    async def test_validate_response_preserves_response_body(
        self, validator: CoincheckResponseValidator
    ):
        """Verify that response body is included in exception"""
        response_body = '{"success": false, "error": "test error"}'
        response_data = HttpResponseData(
            http_status_code=401,
            headers={},
            url="https://coincheck.com/api/accounts/balance",
            response_body_text=response_body,
        )

        with pytest.raises(ExchangeApiError) as exc_info:
            await validator.after_request(response_data)

        exception = exc_info.value
        assert exception.response_body == response_body
