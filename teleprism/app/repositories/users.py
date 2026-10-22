"""User repository."""

from typing import Any

import aiosqlite

from teleprism.app.core.enums import UserRole
from teleprism.app.core.time import iso_now
from teleprism.app.repositories.base import fetch_one


class UserRepository:
    """Persist Telegram users."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Store database connection."""

        self.db = db

    async def upsert_user(self, telegram_user: Any, owner_ids: list[int]) -> dict[str, Any]:
        """Create or update a Telegram user."""

        now = iso_now()
        role = UserRole.OWNER if telegram_user.id in owner_ids else UserRole.USER
        await self.db.execute(
            """
            INSERT INTO users
                (telegram_id, username, first_name, last_name, language_code, role,
                 created_at, updated_at, last_seen_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                language_code = excluded.language_code,
                last_seen_at = excluded.last_seen_at,
                updated_at = excluded.updated_at
            """,
            (
                telegram_user.id,
                telegram_user.username,
                telegram_user.first_name,
                telegram_user.last_name,
                telegram_user.language_code,
                role.value,
                now,
                now,
                now,
            ),
        )
        return await self.get_by_telegram_id(telegram_user.id) or {}

    async def get_by_telegram_id(self, telegram_id: int) -> dict[str, Any] | None:
        """Return user by Telegram ID."""

        return await fetch_one(self.db, "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))

    async def get_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Return user by internal ID."""

        return await fetch_one(self.db, "SELECT * FROM users WHERE id = ?", (user_id,))

    async def set_role(self, telegram_id: int, role: UserRole) -> None:
        """Update user role."""

        await self.ensure_telegram_id(telegram_id)
        await self.db.execute(
            "UPDATE users SET role = ?, updated_at = ? WHERE telegram_id = ?",
            (role.value, iso_now(), telegram_id),
        )

    async def ensure_telegram_id(self, telegram_id: int) -> dict[str, Any]:
        """Create a minimal user row if Telegram user is not known yet."""

        existing = await self.get_by_telegram_id(telegram_id)
        if existing is not None:
            return existing
        now = iso_now()
        await self.db.execute(
            """
            INSERT INTO users (telegram_id, role, created_at, updated_at, last_seen_at)
            VALUES (?, 'USER', ?, ?, ?)
            """,
            (telegram_id, now, now, now),
        )
        return await self.get_by_telegram_id(telegram_id) or {}
