"""SQLite transaction helpers."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any


@asynccontextmanager
async def immediate(db: Any) -> AsyncIterator[None]:
    """Run a block inside BEGIN IMMEDIATE."""

    await db.execute("BEGIN IMMEDIATE")
    try:
        yield
        await db.commit()
    except Exception:
        await db.rollback()
        raise
