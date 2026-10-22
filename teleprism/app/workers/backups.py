"""Database backup worker."""

import asyncio

from teleprism.app.config import Settings
from teleprism.app.db.backup import backup_database


class BackupWorker:
    """Create daily SQLite backups."""

    def __init__(self, settings: Settings) -> None:
        """Store settings."""

        self.settings = settings

    async def run(self) -> None:
        """Run forever until cancelled."""

        await asyncio.sleep(300)
        while True:
            await backup_database(
                self.settings.database_path,
                self.settings.backup_directory,
                self.settings.backup_retention_days,
            )
            await asyncio.sleep(86_400)
