"""User service."""

from typing import Any

from teleprism.app.config import Settings
from teleprism.app.repositories.users import UserRepository


class UserService:
    """Create and update Telegram users."""

    def __init__(self, users: UserRepository, settings: Settings) -> None:
        """Store dependencies."""

        self.users = users
        self.settings = settings

    async def touch(self, telegram_user: Any) -> dict[str, Any]:
        """Upsert a Telegram user."""

        return await self.users.upsert_user(telegram_user, self.settings.owner_ids)
