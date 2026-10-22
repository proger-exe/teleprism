"""Manager order service."""

from typing import Any

from teleprism.app.core.enums import OrderStatus
from teleprism.app.core.errors import TransitionError
from teleprism.app.db.transaction import immediate
from teleprism.app.repositories.orders import OrderRepository
from teleprism.app.services.order_service import OrderService


class ManagerService:
    """Handle manual fulfillment actions."""

    def __init__(self, orders: OrderRepository, order_service: OrderService) -> None:
        """Store dependencies."""

        self.orders = orders
        self.order_service = order_service

    async def take_order(self, order_id: str, manager_user_id: int) -> dict[str, Any] | None:
        """Atomically take a queued order."""

        await self.orders.db.commit()
        async with immediate(self.orders.db):
            return await self.orders.assign_atomic(order_id, manager_user_id)

    async def start_processing(self, order_id: str, manager_user_id: int) -> dict[str, Any]:
        """Start manual Stars fulfillment."""

        return await self.order_service.transition(order_id, OrderStatus.PROCESSING, manager_user_id)

    async def complete(self, order_id: str, manager_user_id: int, proof_file_id: str | None = None) -> dict[str, Any]:
        """Complete manual Stars fulfillment."""

        if proof_file_id:
            await self.orders.db.execute("UPDATE orders SET proof_file_id = ? WHERE id = ?", (proof_file_id, order_id))
        return await self.order_service.transition(order_id, OrderStatus.COMPLETED, manager_user_id)

    async def return_to_queue(self, order_id: str, manager_user_id: int) -> dict[str, Any]:
        """Return assigned order to queue."""

        order = await self.orders.get(order_id)
        if not order or order["status"] != OrderStatus.ASSIGNED.value:
            raise TransitionError("Вернуть можно только назначенный заказ.")
        await self.orders.db.execute("UPDATE orders SET assigned_manager_id = NULL WHERE id = ?", (order_id,))
        return await self.order_service.transition(order_id, OrderStatus.QUEUED, manager_user_id)
