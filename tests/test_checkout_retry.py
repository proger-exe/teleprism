"""Checkout payment creation retry tests."""

from pathlib import Path

import pytest

from teleprism.app.config import Settings
from teleprism.app.container import build_services
from teleprism.app.core.errors import PaymentProviderError
from teleprism.app.core.time import iso_now
from teleprism.app.db.connection import Database
from teleprism.app.db.migrations import migrate
from teleprism.app.integrations.cryptapi.provider import CryptAPIProvider
from teleprism.app.integrations.cryptapi.schemas import CreateAddressResponse


class FailingProvider:
    """Provider that fails address creation."""

    def callback_url(self, payment_id: str, nonce: str | None = None) -> tuple[str, str]:
        """Return stable callback URL."""

        return f"https://ack.example.test/cb?payment_id={payment_id}", nonce or "nonce"

    async def create_address(self, callback: str, expected_amount: str | None = None) -> CreateAddressResponse:
        """Fail address creation."""

        raise PaymentProviderError("provider down")


class WorkingProvider(FailingProvider):
    """Provider that creates an address."""

    async def create_address(self, callback: str, expected_amount: str | None = None) -> CreateAddressResponse:
        """Return fake address."""

        return CreateAddressResponse(
            address_in="TXabc",
            address_out="wallet",
            callback_url=callback,
            minimum_transaction_coin="1",
            status="success",
        )


def test_cryptapi_callback_sink_has_passive_default() -> None:
    """Missing callback sink still yields a stable CryptAPI callback URL."""

    provider = CryptAPIProvider(Settings(cryptapi_callback_sink=""))
    callback, nonce = provider.callback_url("payment-id", nonce="known")
    assert callback == "https://teleprism.local/cryptapi?payment_id=payment-id&nonce=known"
    assert nonce == "known"


def test_blank_cryptapi_wallet_uses_default_address() -> None:
    """Blank env wallet does not override the bundled TRC20 address."""

    settings = Settings(cryptapi_wallet_address="")
    assert settings.cryptapi_wallet_address == ""


async def test_failed_payment_create_can_retry_without_duplicate_order_payment(tmp_path: Path) -> None:
    """A failed CryptAPI create leaves a reusable payment row."""

    database = Database(tmp_path / "test.sqlite3")
    settings = Settings(
        database_path=tmp_path / "test.sqlite3",
        cryptapi_callback_sink="https://ack.example.test/cb",
        cryptapi_wallet_address="wallet",
    )
    async with database.connect() as db:
        await migrate(db)
        now = iso_now()
        await db.execute(
            """
            INSERT INTO users (telegram_id, role, created_at, updated_at, last_seen_at)
            VALUES (1, 'USER', ?, ?, ?)
            """,
            (now, now, now),
        )
        services = build_services(db, settings)
        user = await services.user_repo.get_by_telegram_id(1)
        order = await services.checkout.create_order(int(user["id"]), "shelby_dev", 500)
        services.checkout.provider = FailingProvider()  # type: ignore[assignment]
        with pytest.raises(PaymentProviderError):
            await services.checkout.confirm_order(str(order["id"]))
        failed = await services.payment_repo.by_order(str(order["id"]))
        assert failed["status"] == "FAILED"

        services.checkout.provider = WorkingProvider()  # type: ignore[assignment]
        _, payment = await services.checkout.confirm_order(str(order["id"]))
        assert payment["address_in"] == "TXabc"
        rows = await services.payment_repo.by_order(str(order["id"]))
        assert rows["id"] == failed["id"]
