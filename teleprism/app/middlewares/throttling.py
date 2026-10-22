"""Small in-memory throttling middleware."""

from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from time import monotonic
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    """Limit noisy users without Redis."""

    def __init__(self, limit: int = 60, window: float = 60.0) -> None:
        """Store rate limit settings."""

        self.limit = limit
        self.window = window
        self.events: dict[int, deque[float]] = defaultdict(deque)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Drop updates over the rate limit."""

        user_id = self._user_id(event)
        if user_id is None:
            return await handler(event, data)
        now = monotonic()
        queue = self.events[user_id]
        while queue and queue[0] < now - self.window:
            queue.popleft()
        if len(queue) >= self.limit:
            if isinstance(event, CallbackQuery):
                await event.answer("Слишком часто. Попробуйте позже.", show_alert=False)
            elif isinstance(event, Message):
                await event.answer("Слишком часто. Попробуйте позже.")
            return None
        queue.append(now)
        return await handler(event, data)

    def _user_id(self, event: TelegramObject) -> int | None:
        """Extract Telegram user ID."""

        if isinstance(event, Message) and event.from_user:
            return event.from_user.id
        if isinstance(event, CallbackQuery):
            return event.from_user.id
        return None
