"""User touch middleware."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from teleprism.app.container import Services


class UserMiddleware(BaseMiddleware):
    """Persist Telegram user metadata on every user update."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Add current user row to handler data."""

        from_user = None
        if isinstance(event, Message):
            from_user = event.from_user
        if isinstance(event, CallbackQuery):
            from_user = event.from_user
        if from_user is not None:
            services: Services = data["services"]
            data["user"] = await services.users.touch(from_user)
        return await handler(event, data)
