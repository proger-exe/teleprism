"""Checkout orchestration service."""

from typing import Any

from teleprism.app.config import Settings
from teleprism.app.core.enums import OrderStatus, PaymentStatus
from teleprism.app.core.errors import PaymentProviderError
from teleprism.app.core.ids import new_uuid
from teleprism.app.core.time import iso_after, iso_now
from teleprism.app.integrations.base import PaymentProvider
from teleprism.app.repositories.orders import OrderRepository
from teleprism.app.repositories.payments import PaymentRepository
from teleprism.app.services.order_service import OrderService
from teleprism.app.services.pricing_service import PricingService


class CheckoutService:
    """Create orders and provider payments."""

    def __init__(
        self,
        orders: OrderRepository,
        payments: PaymentRepository,
        pricing: PricingService,
        order_service: OrderService,
        provider: PaymentProvider,
        settings: Settings,
    ) -> None:
        """Store dependencies."""

        self.orders = orders
        self.payments = payments
        self.pricing = pricing
        self.order_service = order_service
        self.provider = provider
        self.settings = settings

    async def create_order(self, buyer_id: int, recipient_username: str, stars_count: int) -> dict[str, Any]:
        """Create a draft order with fixed price."""

        price = await self.pricing.price_for_stars(stars_count)
        now = iso_now()
        order_id = new_uuid()
        order = await self.orders.create(
            {
                "id": order_id,
                "number": await self.orders.next_number(),
                "buyer_id": buyer_id,
                "recipient_username": recipient_username,
                "stars_count": stars_count,
                "package_id": price["package_id"],
                "unit_price": price["unit_price"],
                "base_amount": price["base_amount"],
                "fixed_fee": price["fixed_fee"],
                "total_amount": price["total_amount"],
                "status": OrderStatus.DRAFT.value,
                "created_at": now,
                "updated_at": now,
                "expires_at": iso_after(minutes=self.settings.payment_ttl_minutes),
            }
        )
        await self.orders.add_event(order_id, "order_created", buyer_id, None, OrderStatus.DRAFT.value, {})
        return order

    async def confirm_order(self, order_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
        """Create CryptAPI address and switch order to awaiting payment."""

        order = await self.orders.get(order_id)
        if order is None:
            raise ValueError("Order not found.")
        payment = await self._get_or_create_payment(order)
        if payment.get("address_in"):
            return order, payment
        payment_id = str(payment["id"])
        callback_url = str(payment["callback_url"])
        try:
            response = await self.provider.create_address(callback_url, str(payment["expected_amount"]))
        except Exception as error:
            await self.payments.mark_create_failed(payment_id, str(error))
            raise PaymentProviderError(str(error)) from error
        await self.payments.update_address(payment_id, response.model_dump())
        await self.order_service.transition(order_id, OrderStatus.AWAITING_PAYMENT, order["buyer_id"])
        return (
            await self.orders.get(order_id) or order,
            await self.payments.get(payment_id) or payment,
        )

    async def _get_or_create_payment(self, order: dict[str, Any]) -> dict[str, Any]:
        """Return existing reusable payment row or create a new one."""

        existing = await self.payments.by_order(str(order["id"]))
        if existing is not None:
            return existing
        payment_id = new_uuid()
        callback_url, nonce = self.provider.callback_url(payment_id)
        return await self.payments.create(
            {
                "id": payment_id,
                "order_id": order["id"],
                "ticker": self.settings.cryptapi_ticker,
                "network": "TRC20",
                "expected_amount": order["total_amount"],
                "callback_url": callback_url,
                "callback_nonce": nonce,
                "status": PaymentStatus.CREATING.value,
                "next_poll_at": iso_now(),
                "created_at": iso_now(),
                "expires_at": order["expires_at"],
                "grace_expires_at": iso_after(hours=self.settings.payment_grace_period_hours),
            }
        )
