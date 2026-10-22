"""Order lifecycle service."""

from typing import Any

from teleprism.app.core.enums import OrderStatus
from teleprism.app.core.errors import NotFoundError, TransitionError
from teleprism.app.repositories.orders import OrderRepository

ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.DRAFT: {OrderStatus.AWAITING_PAYMENT, OrderStatus.CANCELED},
    OrderStatus.AWAITING_PAYMENT: {
        OrderStatus.PAYMENT_DETECTED,
        OrderStatus.PARTIALLY_PAID,
        OrderStatus.PAID,
        OrderStatus.CANCELED,
        OrderStatus.EXPIRED,
    },
    OrderStatus.PAYMENT_DETECTED: {
        OrderStatus.PARTIALLY_PAID,
        OrderStatus.PAID,
        OrderStatus.ISSUE,
        OrderStatus.EXPIRED,
    },
    OrderStatus.PARTIALLY_PAID: {OrderStatus.PAID, OrderStatus.ISSUE, OrderStatus.EXPIRED},
    OrderStatus.PAID: {OrderStatus.QUEUED},
    OrderStatus.QUEUED: {OrderStatus.ASSIGNED, OrderStatus.ISSUE},
    OrderStatus.ASSIGNED: {OrderStatus.PROCESSING, OrderStatus.QUEUED, OrderStatus.ISSUE},
    OrderStatus.PROCESSING: {OrderStatus.COMPLETED, OrderStatus.ISSUE},
    OrderStatus.ISSUE: {
        OrderStatus.QUEUED,
        OrderStatus.PROCESSING,
        OrderStatus.REFUND_REQUIRED,
        OrderStatus.CANCELED,
    },
}


class OrderService:
    """Validate and record order transitions."""

    def __init__(self, orders: OrderRepository) -> None:
        """Store repository."""

        self.orders = orders

    async def transition(
        self,
        order_id: str,
        new_status: OrderStatus,
        actor_user_id: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Move order to a new status if allowed."""

        order = await self.orders.get(order_id)
        if order is None:
            raise NotFoundError("Заказ не найден.")
        old_status = OrderStatus(str(order["status"]))
        if new_status == old_status:
            return order
        if new_status not in ALLOWED_TRANSITIONS.get(old_status, set()):
            raise TransitionError(f"Переход {old_status.value} → {new_status.value} запрещён.")
        return await self.orders.update_status(order_id, old_status, new_status, actor_user_id, payload)

    async def mark_paid_and_queue(self, order_id: str) -> dict[str, Any]:
        """Move paid order through PAID into QUEUED."""

        paid = await self.transition(order_id, OrderStatus.PAID)
        if paid["status"] == OrderStatus.PAID.value:
            return await self.transition(order_id, OrderStatus.QUEUED)
        return paid
