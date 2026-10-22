"""Mock provider confirms the exact expected amount after the configured delay."""

import pytest

from teleprism.app.config import Settings
from teleprism.app.integrations.mock.provider import MockPaymentProvider


@pytest.mark.asyncio
async def test_mock_pays_in_full_after_delay() -> None:
    provider = MockPaymentProvider(Settings(mock_confirm_seconds=0))
    callback, _ = provider.callback_url("p1")
    address = await provider.create_address(callback, "9.80")
    assert address.status == "success"
    logs = await provider.logs(callback)
    assert len(logs.callbacks) == 1
    assert logs.callbacks[0].confirmed and logs.callbacks[0].value_coin == "9.80"


@pytest.mark.asyncio
async def test_mock_is_silent_before_delay_and_for_unknown_callbacks() -> None:
    provider = MockPaymentProvider(Settings(mock_confirm_seconds=3600))
    callback, _ = provider.callback_url("p2")
    await provider.create_address(callback, "1")
    assert (await provider.logs(callback)).callbacks == []
    assert (await provider.logs("mock://payments?payment_id=nope")).callbacks == []
