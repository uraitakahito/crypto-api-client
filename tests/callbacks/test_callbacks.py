"""Tests for async callbacks."""

import pytest

from tests.common.builders import CallbackTestBuilder


class TestAsyncCallbackIntegration:
    """Integration tests combining multiple callbacks."""

    @pytest.mark.asyncio
    async def test_multiple_callbacks_execution_order_with_builder(self) -> None:
        """Test that multiple callbacks execute in correct order (builder pattern)."""
        builder = (
            CallbackTestBuilder()
            .with_logging_callback("callback1")
            .with_logging_callback("callback2")
            .with_request_url("https://api.example.com")
        )

        execution_log = await builder.execute_callbacks()

        # Verify execution order
        assert execution_log == [
            "callback1_before",
            "callback2_before",
            "callback1_after",
            "callback2_after",
        ]
