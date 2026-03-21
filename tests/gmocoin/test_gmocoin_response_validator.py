"""Tests for GMO Coin ResponseValidator"""

import pytest

from crypto_api_client.errors.exceptions import ExchangeApiError
from crypto_api_client.gmocoin.gmocoin_response_validator import (
    GmoCoinResponseValidator,
)
from crypto_api_client.http.http_response_data import HttpResponseData
from tests.common.test_data_factory import GmocoinDataFactory


class TestExtractErrorInfo:
    """Tests for _extract_error_info method"""

    @pytest.fixture
    def validator(self) -> GmoCoinResponseValidator:
        return GmoCoinResponseValidator()

    def test_success_response(self, validator: GmoCoinResponseValidator) -> None:
        """Test extraction from success response (status=0, no messages)"""
        ticker_data = GmocoinDataFactory.ticker().minimal().build()
        body = GmocoinDataFactory.ticker_response_json(ticker_data)
        status, messages = validator._extract_error_info(body)

        assert status == 0
        assert messages == []

    def test_maintenance_response(self, validator: GmoCoinResponseValidator) -> None:
        """Test extraction from actual maintenance response"""
        body = GmocoinDataFactory.maintenance_response_json()
        status, messages = validator._extract_error_info(body)

        assert status == 5
        assert len(messages) == 1
        assert messages[0] == ("ERR-5201", "MAINTENANCE. Please wait for a while")

    def test_generic_error_response(self, validator: GmoCoinResponseValidator) -> None:
        """Test extraction from generic error response"""
        body = GmocoinDataFactory.message().error_preset().to_json()
        status, messages = validator._extract_error_info(body)

        assert status == 1
        assert len(messages) == 1
        assert messages[0] == ("ERR-0001", "System error")

    def test_multiple_error_messages(self, validator: GmoCoinResponseValidator) -> None:
        """Test extraction with multiple error messages"""
        body = '{"status": 1, "messages": [{"message_code": "ERR-0001", "message_string": "Error 1"}, {"message_code": "ERR-0002", "message_string": "Error 2"}]}'
        status, messages = validator._extract_error_info(body)

        assert status == 1
        assert len(messages) == 2

    def test_empty_messages_array(self, validator: GmoCoinResponseValidator) -> None:
        """Test extraction with empty messages array"""
        body = '{"status": 1, "messages": []}'
        status, messages = validator._extract_error_info(body)

        assert status == 1
        assert messages == []

    def test_empty_string(self, validator: GmoCoinResponseValidator) -> None:
        """Test extraction from empty string"""
        status, messages = validator._extract_error_info("")

        assert status is None
        assert messages == []

    def test_invalid_json(self, validator: GmoCoinResponseValidator) -> None:
        """Test extraction from invalid JSON"""
        status, messages = validator._extract_error_info("not json")

        assert status is None
        assert messages == []

    def test_missing_status_field(self, validator: GmoCoinResponseValidator) -> None:
        """Test extraction when status field is missing"""
        body = '{"messages": [{"message_code": "ERR-0001", "message_string": "Error"}]}'
        status, messages = validator._extract_error_info(body)

        assert status is None
        assert len(messages) == 1

    def test_missing_messages_field(self, validator: GmoCoinResponseValidator) -> None:
        """Test extraction when messages field is missing"""
        body = '{"status": 0}'
        status, messages = validator._extract_error_info(body)

        assert status == 0
        assert messages == []


class TestValidateResponse:
    """Tests for _validate_response method"""

    @pytest.fixture
    def validator(self) -> GmoCoinResponseValidator:
        return GmoCoinResponseValidator()

    def _make_response(self, status_code: int, body: str) -> HttpResponseData:
        return HttpResponseData(
            http_status_code=status_code,
            headers={},
            response_body_text=body,
            url="https://api.coin.z.com/public/v1/ticker",
        )

    def test_success_response_no_error(
        self, validator: GmoCoinResponseValidator
    ) -> None:
        """Test that success response does not raise"""
        ticker_data = GmocoinDataFactory.ticker().minimal().build()
        body = GmocoinDataFactory.ticker_response_json(ticker_data)
        response = self._make_response(200, body)

        validator._validate_response(response)

    def test_maintenance_response_raises(
        self, validator: GmoCoinResponseValidator
    ) -> None:
        """Test that maintenance response (HTTP 200 + status=5) raises ExchangeApiError"""
        body = GmocoinDataFactory.maintenance_response_json()
        response = self._make_response(200, body)

        with pytest.raises(ExchangeApiError) as exc_info:
            validator._validate_response(response)

        assert exc_info.value.api_status_code_1 == "5"
        assert "ERR-5201" in str(exc_info.value.api_error_message_1)

    def test_http_error_with_json(self, validator: GmoCoinResponseValidator) -> None:
        """Test that HTTP error with valid JSON raises ExchangeApiError"""
        body = GmocoinDataFactory.message().error_preset().to_json()
        response = self._make_response(500, body)

        with pytest.raises(ExchangeApiError) as exc_info:
            validator._validate_response(response)

        assert exc_info.value.http_status_code == 500

    def test_http_error_with_invalid_json(
        self, validator: GmoCoinResponseValidator
    ) -> None:
        """Test that HTTP error with invalid JSON raises ExchangeApiError"""
        response = self._make_response(500, "Internal Server Error")

        with pytest.raises(ExchangeApiError):
            validator._validate_response(response)


class TestBeforeRequest:
    """Tests for before_request method"""

    async def test_before_request_is_noop(self) -> None:
        """Test that before_request does nothing"""
        from yarl import URL

        from crypto_api_client.security.secret_headers import SecretHeaders

        validator = GmoCoinResponseValidator()
        await validator.before_request(
            URL("https://api.coin.z.com/public/v1/ticker"),
            SecretHeaders(),
            None,
        )
