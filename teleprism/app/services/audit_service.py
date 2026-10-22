"""Audit service."""

from typing import Any

from teleprism.app.repositories.orders import OrderRepository


class AuditService:
    """Append order-related audit entries."""

    def __init__(self, orders: OrderRepository) -> None:
        """Store repository."""

        self.orders = orders

    async def record(self, order_id: str, actor_user_id: int | None, event_type: str, payload: dict[str, Any]) -> None:
        """Record an audit event."""

        await self.orders.add_event(order_id, event_type, actor_user_id, None, None, payload)
