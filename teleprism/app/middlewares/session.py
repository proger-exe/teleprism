"""Session middleware placeholder."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class SessionMiddleware(BaseMiddleware):
    """Reserve middleware slot for persistent SQLite FSM data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Pass through with service-backed sessions available."""

        return await handler(event, data)
