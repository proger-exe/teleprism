"""Order status transition tests."""

from pathlib import Path

import pytest

from teleprism.app.core.enums import OrderStatus
from teleprism.app.core.errors import TransitionError
from teleprism.app.core.ids import new_uuid
from teleprism.app.core.time import iso_after, iso_now
from teleprism.app.db.connection import Database
from teleprism.app.db.migrations import migrate
from teleprism.app.repositories.orders import OrderRepository
from teleprism.app.repositories.users import UserRepository
from teleprism.app.services.order_service import OrderService


async def create_user_and_order(tmp_path: Path) -> tuple[Database, str]:
    """Create a database with one draft order."""

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
        user = await UserRepository(db).get_by_telegram_id(1)
        orders = OrderRepository(db)
        order_id = new_uuid()
        await orders.create(
            {
                "id": order_id,
                "number": await orders.next_number(),
                "buyer_id": user["id"],
                "recipient_username": "shelby_dev",
                "stars_count": 100,
                "total_amount": "2.20",
                "status": OrderStatus.DRAFT.value,
                "created_at": iso_now(),
                "updated_at": iso_now(),
                "expires_at": iso_after(minutes=30),
            }
        )
    return database, order_id


async def test_valid_transition_is_saved(tmp_path: Path) -> None:
    """Allowed transition updates the order."""

    database, order_id = await create_user_and_order(tmp_path)
    async with database.connect() as db:
        service = OrderService(OrderRepository(db))
        order = await service.transition(order_id, OrderStatus.AWAITING_PAYMENT)
    assert order["status"] == OrderStatus.AWAITING_PAYMENT.value


async def test_invalid_transition_is_rejected(tmp_path: Path) -> None:
    """Disallowed transition raises error."""

    database, order_id = await create_user_and_order(tmp_path)
    async with database.connect() as db:
        service = OrderService(OrderRepository(db))
        with pytest.raises(TransitionError):
            await service.transition(order_id, OrderStatus.COMPLETED)
