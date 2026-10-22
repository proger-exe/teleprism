"""Order repository."""

from typing import Any

import aiosqlite
import orjson

from teleprism.app.core.enums import OrderStatus
from teleprism.app.core.time import iso_now
from teleprism.app.repositories.base import fetch_all, fetch_one


class OrderRepository:
    """Persist orders and order events."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Store database connection."""

        self.db = db

    async def next_number(self) -> int:
        """Return next human order number."""

        row = await fetch_one(self.db, "SELECT COALESCE(MAX(number), 1000) + 1 AS value FROM orders")
        if row is None:
            raise RuntimeError("Could not compute next order number.")
        return int(row["value"])

    async def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Insert an order row."""

        keys = ", ".join(payload)
        placeholders = ", ".join("?" for _ in payload)
        await self.db.execute(
            f"INSERT INTO orders ({keys}) VALUES ({placeholders})",  # noqa: S608
            tuple(payload.values()),
        )
        return await self.get(payload["id"]) or {}

    async def get(self, order_id: str) -> dict[str, Any] | None:
        """Return order by ID."""

        return await fetch_one(self.db, "SELECT * FROM orders WHERE id = ?", (order_id,))

    async def get_by_number(self, number: int) -> dict[str, Any] | None:
        """Return order by number."""

        return await fetch_one(self.db, "SELECT * FROM orders WHERE number = ?", (number,))

    async def recent_for_user(self, buyer_id: int, limit: int = 5, offset: int = 0) -> list[dict[str, Any]]:
        """Return recent user orders."""

        return await fetch_all(
            self.db,
            "SELECT * FROM orders WHERE buyer_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (buyer_id, limit, offset),
        )

    async def update_status(
        self,
        order_id: str,
        old_status: OrderStatus,
        new_status: OrderStatus,
        actor_user_id: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update order status and append audit event."""

        now = iso_now()
        columns = ["status = ?", "updated_at = ?"]
        values: list[Any] = [new_status.value, now]
        timestamp_columns = {
            OrderStatus.QUEUED: "queued_at",
            OrderStatus.ASSIGNED: "assigned_at",
            OrderStatus.PROCESSING: "processing_at",
            OrderStatus.COMPLETED: "completed_at",
            OrderStatus.PAID: "paid_at",
        }
        if new_status in timestamp_columns:
            columns.append(f"{timestamp_columns[new_status]} = ?")
            values.append(now)
        values.append(order_id)
        await self.db.execute(
            f"UPDATE orders SET {', '.join(columns)} WHERE id = ?",  # noqa: S608
            tuple(values),
        )
        await self.add_event(
            order_id,
            "status_changed",
            actor_user_id,
            old_status.value,
            new_status.value,
            payload or {},
        )
        return await self.get(order_id) or {}

    async def add_event(
        self,
        order_id: str,
        event_type: str,
        actor_user_id: int | None,
        old_status: str | None,
        new_status: str | None,
        payload: dict[str, Any],
    ) -> None:
        """Append an order event."""

        await self.db.execute(
            """
            INSERT INTO order_events
                (order_id, actor_user_id, event_type, old_status, new_status, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                actor_user_id,
                event_type,
                old_status,
                new_status,
                orjson.dumps(payload).decode(),
                iso_now(),
            ),
        )

    async def set_screen(self, order_id: str, chat_id: int, message_id: int) -> None:
        """Persist active screen message."""

        await self.db.execute(
            "UPDATE orders SET screen_chat_id = ?, screen_message_id = ?, updated_at = ? WHERE id = ?",
            (chat_id, message_id, iso_now(), order_id),
        )

    async def assign_atomic(self, order_id: str, manager_user_id: int) -> dict[str, Any] | None:
        """Atomically assign one queued order to one manager."""

        now = iso_now()
        cursor = await self.db.execute(
            """
            UPDATE orders
            SET status = 'ASSIGNED',
                assigned_manager_id = ?,
                assigned_at = ?,
                updated_at = ?
            WHERE id = ?
              AND status = 'QUEUED'
              AND assigned_manager_id IS NULL
            RETURNING *
            """,
            (manager_user_id, now, now, order_id),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        await self.add_event(
            order_id,
            "order_assigned",
            manager_user_id,
            OrderStatus.QUEUED.value,
            OrderStatus.ASSIGNED.value,
            {},
        )
        return dict(row)

    async def queue(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return queued orders."""

        return await fetch_all(
            self.db,
            "SELECT * FROM orders WHERE status = 'QUEUED' ORDER BY queued_at LIMIT ?",
            (limit,),
        )
