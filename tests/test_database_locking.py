"""SQLite lock resilience tests."""

import asyncio
from pathlib import Path

from teleprism.app.db.connection import Database
from teleprism.app.db.migrations import migrate
from teleprism.app.repositories.settings import SettingsRepository


async def test_parallel_short_writes_do_not_lock(tmp_path: Path) -> None:
    """Several short connections can write without permanent lock errors."""

    database = Database(tmp_path / "test.sqlite3")
    async with database.connect() as db:
        await migrate(db)

    async def write_value(index: int) -> None:
        async with database.connect() as db:
            await SettingsRepository(db).set(f"key_{index}", str(index), updated_by=None)

    await asyncio.gather(*(write_value(index) for index in range(25)))
