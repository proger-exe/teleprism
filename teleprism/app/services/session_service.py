"""Session service."""

from typing import Any

from teleprism.app.repositories.sessions import SessionRepository


class SessionService:
    """Wrap persistent session operations."""

    def __init__(self, sessions: SessionRepository) -> None:
        """Store repository."""

        self.sessions = sessions

    async def get(self, user_id: int) -> dict[str, Any]:
        """Return session."""

        return await self.sessions.get(user_id)

    async def set(self, user_id: int, state: str | None, data: dict[str, Any]) -> None:
        """Set session."""

        await self.sessions.set(user_id, state, data)

    async def clear(self, user_id: int) -> None:
        """Clear session."""

        await self.sessions.clear(user_id)
