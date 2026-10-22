"""Payment provider contract shared by CryptAPI and the mock used for demos."""

from typing import Protocol

from teleprism.app.integrations.cryptapi.schemas import CreateAddressResponse, LogsResponse


class PaymentProvider(Protocol):
    """Create a deposit address for a payment and poll its transactions."""

    def callback_url(self, payment_id: str, nonce: str | None = None) -> tuple[str, str]:
        """Build the provider-side identifier for a payment."""

    async def create_address(self, callback: str, expected_amount: str | None = None) -> CreateAddressResponse:
        """Create a deposit address bound to the callback."""

    async def logs(self, callback: str) -> LogsResponse:
        """Return transactions seen for the callback."""
