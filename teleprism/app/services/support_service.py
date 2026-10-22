"""Support ticket service."""

from teleprism.app.repositories.tickets import TicketRepository


class SupportService:
    """Create support tickets."""

    def __init__(self, tickets: TicketRepository) -> None:
        """Store repository."""

        self.tickets = tickets

    async def open_ticket(
        self, user_id: int, category: str, message: str | None = None, order_id: str | None = None
    ) -> int:
        """Open a support ticket."""

        return await self.tickets.create(user_id, category, message, order_id)
