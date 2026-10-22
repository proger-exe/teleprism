"""Maintenance middleware placeholder."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class MaintenanceMiddleware(BaseMiddleware):
    """Leave paid/manager flows available while blocking new checkouts when enabled."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Pass through; handlers check maintenance where it changes behavior."""

        return await handler(event, data)
