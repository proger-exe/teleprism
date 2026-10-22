"""Database dependency middleware."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from teleprism.app.config import Settings
from teleprism.app.container import build_services
from teleprism.app.db.connection import Database


class DatabaseMiddleware(BaseMiddleware):
    """Open one SQLite connection for one Telegram update."""

    def __init__(self, database: Database, settings: Settings) -> None:
        """Store dependencies."""

        self.database = database
        self.settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Inject services into aiogram handler data."""

        async with self.database.connect() as db:
            data["db"] = db
            data["services"] = build_services(db, self.settings)
            data["settings"] = self.settings
            return await handler(event, data)
