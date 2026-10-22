"""CryptAPI HTTP client."""

from typing import Any

import aiohttp
from aiohttp import ClientTimeout
from tenacity import retry, stop_after_attempt, wait_exponential

from teleprism.app.core.errors import PaymentProviderError
from teleprism.app.integrations.cryptapi.parser import parse_logs
from teleprism.app.integrations.cryptapi.schemas import CreateAddressResponse, LogsResponse


class CryptAPIClient:
    """Small polling-only CryptAPI client."""

    def __init__(self, ticker: str, session: aiohttp.ClientSession | None = None) -> None:
        """Store ticker and optional HTTP session."""

        self.ticker = ticker.strip("/")
        self.session = session
        self.base_url = f"https://api.cryptapi.io/{self.ticker}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
    async def create_address(
        self, address: str, callback: str, confirmations: int, pending: bool = True
    ) -> CreateAddressResponse:
        """Create a CryptAPI inbound address."""

        payload = await self._get_json(
            f"{self.base_url}/create/",
            {
                "address": address,
                "callback": callback,
                "confirmations": confirmations,
                "pending": int(pending),
            },
        )
        response = CreateAddressResponse.model_validate(payload)
        if response.status != "success":
            raise PaymentProviderError("CryptAPI address creation failed.")
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
    async def logs(self, callback: str) -> LogsResponse:
        """Fetch CryptAPI logs by exact callback URL."""

        payload = await self._get_json(f"{self.base_url}/logs/", {"callback": callback})
        return parse_logs(payload)

    async def _get_json(self, url: str, params: dict[str, object]) -> dict[str, Any]:
        """Perform a GET request and decode JSON."""

        if self.session is not None:
            return await self._get_json_with_session(self.session, url, params)
        async with aiohttp.ClientSession() as session:
            return await self._get_json_with_session(session, url, params)

    async def _get_json_with_session(
        self, session: aiohttp.ClientSession, url: str, params: dict[str, object]
    ) -> dict[str, Any]:
        """Perform a GET request with an existing session."""

        request_params: dict[str, str | int | float] = {
            key: int(value) if isinstance(value, bool) else value
            for key, value in params.items()
            if isinstance(value, (str, int, float, bool))
        }
        async with session.get(
            url,
            params=request_params,
            timeout=ClientTimeout(total=20),
        ) as response:
            if response.status >= 400:
                raise PaymentProviderError(f"CryptAPI HTTP {response.status}")
            data = await response.json()
            if not isinstance(data, dict):
                raise PaymentProviderError("CryptAPI returned non-object JSON.")
            return data
