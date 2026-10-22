"""Support ticket repository."""

import aiosqlite

from teleprism.app.core.time import iso_now


class TicketRepository:
    """Persist support tickets."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Store database connection."""

        self.db = db

    async def create(self, user_id: int, category: str, message: str | None = None, order_id: str | None = None) -> int:
        """Create a support ticket."""

        cursor = await self.db.execute(
            """
            INSERT INTO support_tickets (user_id, order_id, category, message, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, order_id, category, message, iso_now(), iso_now()),
        )
        if cursor.lastrowid is None:
            raise RuntimeError("Could not create support ticket.")
        return int(cursor.lastrowid)
