"""CryptAPI payment provider facade."""

from urllib.parse import urlencode

from teleprism.app.config import Settings
from teleprism.app.core.errors import PaymentProviderError
from teleprism.app.core.ids import new_nonce
from teleprism.app.integrations.cryptapi.client import CryptAPIClient
from teleprism.app.integrations.cryptapi.schemas import CreateAddressResponse, LogsResponse


class CryptAPIProvider:
    """Create addresses and poll logs without webhook state changes."""

    DEFAULT_CALLBACK_SINK = "https://teleprism.local/cryptapi"

    def __init__(self, settings: Settings, client: CryptAPIClient | None = None) -> None:
        """Store settings and client."""

        self.settings = settings
        self.client = client or CryptAPIClient(settings.cryptapi_ticker)

    def callback_url(self, payment_id: str, nonce: str | None = None) -> tuple[str, str]:
        """Build a passive callback sink URL used only as provider identifier."""

        callback_nonce = nonce or new_nonce()
        sink = self.settings.cryptapi_callback_sink or self.DEFAULT_CALLBACK_SINK
        separator = "&" if "?" in sink else "?"
        query = urlencode({"payment_id": payment_id, "nonce": callback_nonce})
        return f"{sink}{separator}{query}", callback_nonce

    async def create_address(self, callback: str, expected_amount: str | None = None) -> CreateAddressResponse:
        """Create provider address; CryptAPI does not need the amount up front."""

        if not self.settings.cryptapi_wallet_address:
            raise PaymentProviderError("CRYPTAPI_WALLET_ADDRESS is not configured.")
        return await self.client.create_address(
            self.settings.cryptapi_wallet_address,
            callback,
            self.settings.cryptapi_confirmations,
            pending=True,
        )

    async def logs(self, callback: str) -> LogsResponse:
        """Poll provider logs."""

        return await self.client.logs(callback)
