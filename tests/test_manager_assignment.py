"""Manager assignment tests."""

from pathlib import Path

from teleprism.app.config import Settings
from teleprism.app.container import build_services
from teleprism.app.core.enums import OrderStatus
from teleprism.app.core.ids import new_uuid
from teleprism.app.core.time import iso_after, iso_now
from teleprism.app.db.connection import Database
from teleprism.app.db.migrations import migrate


async def test_only_one_manager_takes_order(tmp_path: Path) -> None:
    """Atomic assignment lets only one manager take a queued order."""

    database = Database(tmp_path / "test.sqlite3")
    async with database.connect() as db:
        await migrate(db)
        now = iso_now()
        await db.executemany(
            """
            INSERT INTO users (telegram_id, role, created_at, updated_at, last_seen_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (1, "USER", now, now, now),
                (2, "MANAGER", now, now, now),
                (3, "MANAGER", now, now, now),
            ],
        )
        services = build_services(db, Settings(database_path=tmp_path / "test.sqlite3"))
        user = await services.user_repo.get_by_telegram_id(1)
        manager_one = await services.user_repo.get_by_telegram_id(2)
        manager_two = await services.user_repo.get_by_telegram_id(3)
        order = await services.order_repo.create(
            {
                "id": new_uuid(),
                "number": await services.order_repo.next_number(),
                "buyer_id": user["id"],
                "recipient_username": "shelby_dev",
                "stars_count": 500,
                "total_amount": "9.80",
                "status": OrderStatus.QUEUED.value,
                "created_at": now,
                "updated_at": now,
                "expires_at": iso_after(minutes=30),
                "queued_at": now,
            }
        )
        first = await services.order_repo.assign_atomic(str(order["id"]), int(manager_one["id"]))
        second = await services.order_repo.assign_atomic(str(order["id"]), int(manager_two["id"]))
    assert first is not None
    assert second is None
