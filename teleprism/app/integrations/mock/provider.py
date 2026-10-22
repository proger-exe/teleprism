"""Mock payment provider: every address gets 'paid' in full after a fixed delay. No money moves."""

import time
from urllib.parse import urlencode

from teleprism.app.config import Settings
from teleprism.app.core.ids import new_nonce
from teleprism.app.integrations.cryptapi.schemas import CreateAddressResponse, LogsResponse, TransactionItem


class MockPaymentProvider:
    """Deterministic stand-in for CryptAPI; selected with PAYMENTS_PROVIDER=mock."""

    def __init__(self, settings: Settings) -> None:
        """Store settings; keep created addresses in memory (lost on restart, fine for a demo)."""

        self.settings = settings
        self._created: dict[str, tuple[float, str]] = {}

    def callback_url(self, payment_id: str, nonce: str | None = None) -> tuple[str, str]:
        """Same identifier scheme as the real provider so stored rows look identical."""

        callback_nonce = nonce or new_nonce()
        return f"mock://payments?{urlencode({'payment_id': payment_id, 'nonce': callback_nonce})}", callback_nonce

    async def create_address(self, callback: str, expected_amount: str | None = None) -> CreateAddressResponse:
        """Issue a fake TRC20-looking address and remember what it should receive."""

        self._created[callback] = (time.monotonic(), expected_amount or "0")
        return CreateAddressResponse(
            address_in="TMockDemoAddress0000000000000000000",
            address_out=None,
            callback_url=callback,
            minimum_transaction_coin="0",
            status="success",
        )

    async def logs(self, callback: str) -> LogsResponse:
        """Report nothing until the delay passes, then one confirmed transaction for the full amount."""

        created = self._created.get(callback)
        if created is None:
            return LogsResponse()
        started, amount = created
        if time.monotonic() - started < self.settings.mock_confirm_seconds:
            return LogsResponse()
        return LogsResponse(
            callbacks=[
                TransactionItem(
                    txid_in="mock-" + callback.rsplit("nonce=", 1)[-1],
                    value_coin=amount,
                    confirmations=self.settings.cryptapi_confirmations,
                    confirmed=True,
                )
            ]
        )
