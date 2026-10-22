"""Notification outbox repository."""

from typing import Any

import aiosqlite
import orjson

from teleprism.app.core.time import iso_now
from teleprism.app.repositories.base import fetch_all


class OutboxRepository:
    """Persist outgoing Telegram notifications."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Store database connection."""

        self.db = db

    async def enqueue(self, chat_id: int, message_type: str, payload: dict[str, Any]) -> None:
        """Add an outbox message."""

        await self.db.execute(
            """
            INSERT INTO outbox_messages
                (chat_id, message_type, payload, next_attempt_at, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (chat_id, message_type, orjson.dumps(payload).decode(), iso_now(), iso_now()),
        )

    async def due(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return due outbox messages."""

        return await fetch_all(
            self.db,
            """
            SELECT * FROM outbox_messages
            WHERE status = 'PENDING' AND next_attempt_at <= ?
            ORDER BY created_at
            LIMIT ?
            """,
            (iso_now(), limit),
        )

    async def mark_sent(self, message_id: int) -> None:
        """Mark message as sent."""

        await self.db.execute(
            "UPDATE outbox_messages SET status = 'SENT', sent_at = ? WHERE id = ?",
            (iso_now(), message_id),
        )

    async def mark_failed(self, message_id: int, error: str, next_attempt_at: str) -> None:
        """Mark message attempt as failed."""

        await self.db.execute(
            """
            UPDATE outbox_messages
            SET attempts = attempts + 1, last_error = ?, next_attempt_at = ?
            WHERE id = ?
            """,
            (error[:500], next_attempt_at, message_id),
        )
