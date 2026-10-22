"""Persistent session repository."""

from typing import Any

import aiosqlite
import orjson

from teleprism.app.core.time import iso_now
from teleprism.app.repositories.base import fetch_one


class SessionRepository:
    """Persist user conversation state."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Store database connection."""

        self.db = db

    async def get(self, user_id: int) -> dict[str, Any]:
        """Return session data."""

        row = await fetch_one(self.db, "SELECT * FROM user_sessions WHERE user_id = ?", (user_id,))
        if row is None:
            return {"state": None, "data": {}}
        return {"state": row["state"], "data": orjson.loads(row["data"])}

    async def set(self, user_id: int, state: str | None, data: dict[str, Any]) -> None:
        """Store session data."""

        await self.db.execute(
            """
            INSERT INTO user_sessions (user_id, state, data, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                state = excluded.state,
                data = excluded.data,
                updated_at = excluded.updated_at
            """,
            (user_id, state, orjson.dumps(data).decode(), iso_now()),
        )

    async def clear(self, user_id: int) -> None:
        """Clear session state."""

        await self.set(user_id, None, {})
