"""Notification outbox worker."""

import asyncio

import orjson
from aiogram import Bot

from teleprism.app.config import Settings
from teleprism.app.container import build_services
from teleprism.app.core.time import iso_after
from teleprism.app.db.connection import Database


class NotificationOutboxWorker:
    """Send persisted Telegram notifications with retries."""

    def __init__(self, database: Database, settings: Settings, bot: Bot) -> None:
        """Store dependencies."""

        self.database = database
        self.settings = settings
        self.bot = bot

    async def run(self) -> None:
        """Run forever until cancelled."""

        while True:
            await self.tick()
            await asyncio.sleep(3)

    async def tick(self) -> None:
        """Send due outbox messages once."""

        async with self.database.connect() as db:
            services = build_services(db, self.settings)
            messages = await services.outbox_repo.due()
            for message in messages:
                try:
                    payload = orjson.loads(message["payload"])
                    await self.bot.send_message(int(message["chat_id"]), str(payload["text"]))
                    await services.outbox_repo.mark_sent(int(message["id"]))
                except Exception as error:
                    await services.outbox_repo.mark_failed(int(message["id"]), str(error), iso_after(seconds=30))
