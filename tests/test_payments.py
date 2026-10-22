"""Payment aggregation tests."""

from pathlib import Path

from teleprism.app.config import Settings
from teleprism.app.container import build_services
from teleprism.app.core.enums import OrderStatus, PaymentStatus
from teleprism.app.core.ids import new_uuid
from teleprism.app.core.time import iso_after, iso_now
from teleprism.app.db.connection import Database
from teleprism.app.db.migrations import migrate
from teleprism.app.integrations.cryptapi.schemas import LogsResponse, TransactionItem


class FakeProvider:
    """Fake CryptAPI provider."""

    def __init__(self, items: list[TransactionItem]) -> None:
        """Store fake items."""

        self.items = items

    async def logs(self, callback: str) -> LogsResponse:
        """Return fake logs."""

        return LogsResponse(callbacks=self.items)


async def seed_payment(tmp_path: Path, expected: str = "9.80") -> tuple[Database, str]:
    """Create one awaiting payment."""

    database = Database(tmp_path / "test.sqlite3")
    async with database.connect() as db:
        await migrate(db)
        await db.execute(
            """
            INSERT INTO users (telegram_id, role, created_at, updated_at, last_seen_at)
            VALUES (1, 'USER', ?, ?, ?)
            """,
            (iso_now(), iso_now(), iso_now()),
        )
        services = build_services(db, Settings(database_path=tmp_path / "test.sqlite3"))
        user = await services.user_repo.get_by_telegram_id(1)
        order = await services.order_repo.create(
            {
                "id": new_uuid(),
                "number": await services.order_repo.next_number(),
                "buyer_id": user["id"],
                "recipient_username": "shelby_dev",
                "stars_count": 500,
                "total_amount": expected,
                "status": OrderStatus.AWAITING_PAYMENT.value,
                "created_at": iso_now(),
                "updated_at": iso_now(),
                "expires_at": iso_after(minutes=30),
            }
        )
        payment = await services.payment_repo.create(
            {
                "id": new_uuid(),
                "order_id": order["id"],
                "ticker": "trc20/usdt",
                "network": "TRC20",
                "expected_amount": expected,
                "callback_url": "https://ack.example.test/cb",
                "callback_nonce": "nonce",
                "status": PaymentStatus.WAITING.value,
                "next_poll_at": iso_now(),
                "created_at": iso_now(),
                "expires_at": iso_after(minutes=30),
                "grace_expires_at": iso_after(hours=24),
            }
        )
    return database, str(payment["id"])


async def test_payment_sums_multiple_confirmed_transactions_once(tmp_path: Path) -> None:
    """Confirmed totals dedupe by txid and queue the order."""

    database, payment_id = await seed_payment(tmp_path)
    items = [
        TransactionItem(txid_in="a", value_coin="5.00", confirmed=True, raw={"txid_in": "a"}),
        TransactionItem(txid_in="b", value_coin="4.80", confirmed=True, raw={"txid_in": "b"}),
        TransactionItem(txid_in="a", value_coin="5.00", confirmed=True, raw={"txid_in": "a"}),
    ]
    async with database.connect() as db:
        settings = Settings(database_path=tmp_path / "test.sqlite3")
        services = build_services(db, settings)
        services.payments.provider = FakeProvider(items)  # type: ignore[assignment]
        payment = await services.payment_repo.get(payment_id)
        await services.payments.poll_payment(payment)
        refreshed = await services.payment_repo.get(payment_id)
        order = await services.order_repo.get(str(refreshed["order_id"]))
        txs = await services.payment_repo.transactions(payment_id)
    assert refreshed["confirmed_amount"] == "9.800000"
    assert refreshed["status"] == PaymentStatus.CONFIRMED.value
    assert order["status"] == OrderStatus.QUEUED.value
    assert len(txs) == 2
