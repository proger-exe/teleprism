"""Star package repository."""

from typing import Any

import aiosqlite

from teleprism.app.core.time import iso_now
from teleprism.app.repositories.base import fetch_all, fetch_one


class PackageRepository:
    """Persist star packages."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Store database connection."""

        self.db = db

    async def active(self) -> list[dict[str, Any]]:
        """Return active packages."""

        return await fetch_all(
            self.db,
            "SELECT * FROM star_packages WHERE is_active = 1 ORDER BY sort_order, stars_count",
        )

    async def find_by_stars(self, stars_count: int) -> dict[str, Any] | None:
        """Return package by Stars count."""

        return await fetch_one(
            self.db,
            "SELECT * FROM star_packages WHERE stars_count = ? AND is_active = 1",
            (stars_count,),
        )

    async def upsert(self, stars_count: int, price_usdt: str, is_active: bool = True) -> None:
        """Create or update a package."""

        now = iso_now()
        existing = await fetch_one(self.db, "SELECT id FROM star_packages WHERE stars_count = ?", (stars_count,))
        if existing:
            await self.db.execute(
                """
                UPDATE star_packages
                SET price_usdt = ?, is_active = ?, updated_at = ?
                WHERE stars_count = ?
                """,
                (price_usdt, int(is_active), now, stars_count),
            )
            return
        await self.db.execute(
            """
            INSERT INTO star_packages (stars_count, price_usdt, sort_order, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (stars_count, price_usdt, stars_count, int(is_active), now, now),
        )
