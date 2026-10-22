"""Manager reminder worker."""

import asyncio

from teleprism.app.config import Settings
from teleprism.app.db.connection import Database


class ManagerReminderWorker:
    """Reserve SLA reminder loop for manager queue notifications."""

    def __init__(self, database: Database, settings: Settings) -> None:
        """Store dependencies."""

        self.database = database
        self.settings = settings

    async def run(self) -> None:
        """Run forever until cancelled."""

        while True:
            await asyncio.sleep(60)
