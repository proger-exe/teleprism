"""Repository helpers."""

from typing import Any


async def fetch_one(db: Any, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    """Fetch one row as a dictionary."""

    cursor = await db.execute(query, params)
    row = await cursor.fetchone()
    return dict(row) if row else None


async def fetch_all(db: Any, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Fetch all rows as dictionaries."""

    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]
