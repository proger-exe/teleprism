"""Notification service."""

from typing import Any

from teleprism.app.repositories.outbox import OutboxRepository


class NotificationService:
    """Enqueue Telegram notifications before sending."""

    def __init__(self, outbox: OutboxRepository) -> None:
        """Store repository."""

        self.outbox = outbox

    async def message(self, chat_id: int, text: str, **extra: Any) -> None:
        """Enqueue a text notification."""

        await self.outbox.enqueue(chat_id, "text", {"text": text, **extra})
