"""Settings repository."""

import aiosqlite

from teleprism.app.core.time import iso_now
from teleprism.app.repositories.base import fetch_one


class SettingsRepository:
    """Persist editable settings."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Store database connection."""

        self.db = db

    async def get(self, key: str, default: str | None = None) -> str | None:
        """Return setting value."""

        row = await fetch_one(self.db, "SELECT value FROM settings WHERE key = ?", (key,))
        return str(row["value"]) if row else default

    async def set(self, key: str, value: str, updated_by: int | None = None) -> None:
        """Set setting value."""

        await self.db.execute(
            """
            INSERT INTO settings (key, value, updated_by, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_by = excluded.updated_by,
                updated_at = excluded.updated_at
            """,
            (key, value, updated_by, iso_now()),
        )
