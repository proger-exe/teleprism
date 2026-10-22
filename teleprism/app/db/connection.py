"""SQLite connection management."""

import asyncio
import sqlite3
from collections.abc import AsyncIterator, Callable, Sequence
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, TypeVar, cast

T = TypeVar("T")


class AsyncCursor:
    """Tiny awaitable cursor facade for sqlite3."""

    def __init__(self, cursor: sqlite3.Cursor) -> None:
        """Store sqlite cursor."""

        self.cursor = cursor
        self.lastrowid = cursor.lastrowid

    async def fetchone(self) -> sqlite3.Row | None:
        """Fetch one row."""

        return cast(sqlite3.Row | None, self.cursor.fetchone())

    async def fetchall(self) -> list[sqlite3.Row]:
        """Fetch all rows."""

        return self.cursor.fetchall()


class AsyncSqliteConnection:
    """Async-shaped sqlite3 connection used by repositories."""

    def __init__(self, path: Path) -> None:
        """Open sqlite3 connection."""

        self.raw = sqlite3.connect(path, isolation_level=None, timeout=30)
        self.raw.row_factory = sqlite3.Row

    async def execute(self, query: str, params: Sequence[Any] = ()) -> AsyncCursor:
        """Execute one SQL statement."""

        return await self._run_locked(lambda: AsyncCursor(self.raw.execute(query, params)))

    async def executemany(self, query: str, params: Sequence[Sequence[Any]]) -> AsyncCursor:
        """Execute one SQL statement for many parameter sets."""

        return await self._run_locked(lambda: AsyncCursor(self.raw.executemany(query, params)))

    async def executescript(self, script: str) -> AsyncCursor:
        """Execute a SQL script."""

        return await self._run_locked(lambda: AsyncCursor(self.raw.executescript(script)))

    async def commit(self) -> None:
        """Commit transaction."""

        self.raw.commit()

    async def rollback(self) -> None:
        """Rollback transaction."""

        self.raw.rollback()

    async def close(self) -> None:
        """Close connection."""

        self.raw.close()

    async def _run_locked(self, operation: Callable[[], T]) -> T:
        """Retry briefly when SQLite reports a transient lock."""

        delay = 0.05
        for attempt in range(6):
            try:
                return operation()
            except sqlite3.OperationalError as error:
                if "database is locked" not in str(error).lower() or attempt == 5:
                    raise
                await asyncio.sleep(delay)
                delay *= 2
        raise RuntimeError("unreachable")


class Database:
    """Small SQLite connection factory."""

    def __init__(self, path: Path) -> None:
        """Store database path."""

        self.path = path

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncSqliteConnection]:
        """Open a configured SQLite connection."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        db = AsyncSqliteConnection(self.path)
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("PRAGMA busy_timeout = 30000")
        await db.execute("PRAGMA synchronous = NORMAL")
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()
