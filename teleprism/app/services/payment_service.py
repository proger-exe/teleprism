"""Payment polling service."""

from decimal import Decimal
from typing import Any

from teleprism.app.config import Settings
from teleprism.app.core.enums import OrderStatus, PaymentStatus
from teleprism.app.core.money import money, quantize_usdt
from teleprism.app.core.time import iso_after, parse_iso, utcnow
from teleprism.app.integrations.base import PaymentProvider
from teleprism.app.repositories.payments import PaymentRepository
from teleprism.app.services.order_service import OrderService


class PaymentService:
    """Poll CryptAPI logs and update payment/order state."""

    def __init__(
        self,
        payments: PaymentRepository,
        orders: OrderService,
        provider: PaymentProvider,
        settings: Settings,
    ) -> None:
        """Store dependencies."""

        self.payments = payments
        self.orders = orders
        self.provider = provider
        self.settings = settings

    def next_poll_at(self, payment: dict[str, Any]) -> str:
        """Compute next polling timestamp."""

        now = utcnow()
        created = parse_iso(str(payment["created_at"]))
        expires = parse_iso(str(payment["expires_at"]))
        if now > expires:
            return iso_after(seconds=self.settings.payment_poll_expired_interval)
        if (now - created).total_seconds() <= 300:
            return iso_after(seconds=self.settings.payment_poll_initial_interval)
        return iso_after(seconds=self.settings.payment_poll_normal_interval)

    async def poll_payment(self, payment: dict[str, Any]) -> None:
        """Poll one payment and store every transaction once."""

        try:
            logs = await self.provider.logs(str(payment["callback_url"]))
        except Exception:
            await self.payments.mark_failure(str(payment["id"]), self.next_poll_at(payment))
            return
        for item in logs.callbacks:
            await self.payments.add_or_update_transaction(
                str(payment["id"]),
                str(payment["ticker"]),
                item.model_dump() | item.raw,
            )
        transactions = await self.payments.transactions(str(payment["id"]))
        confirmed = sum((money(tx["value_coin"]) for tx in transactions if tx["is_confirmed"]), Decimal("0"))
        pending = sum((money(tx["value_coin"]) for tx in transactions if not tx["is_confirmed"]), Decimal("0"))
        expected = money(payment["expected_amount"])
        overpaid = max(Decimal("0"), confirmed - expected)
        status = self._status_for(payment, confirmed, pending)
        await self.payments.update_amounts(
            str(payment["id"]),
            str(quantize_usdt(confirmed)),
            str(quantize_usdt(pending)),
            str(quantize_usdt(overpaid)),
            status.value,
            self.next_poll_at(payment),
        )
        await self._sync_order(str(payment["order_id"]), payment, status)

    def _status_for(self, payment: dict[str, Any], confirmed: Decimal, pending: Decimal) -> PaymentStatus:
        """Derive payment status from totals."""

        expected = money(payment["expected_amount"])
        expired = utcnow() > parse_iso(str(payment["expires_at"]))
        if confirmed >= expected and expired:
            return PaymentStatus.LATE_PAID
        if confirmed > expected:
            return PaymentStatus.OVERPAID
        if confirmed >= expected:
            return PaymentStatus.CONFIRMED
        if confirmed > 0:
            return PaymentStatus.PARTIALLY_PAID
        if pending > 0:
            return PaymentStatus.DETECTED
        if expired:
            return PaymentStatus.EXPIRED
        return PaymentStatus.WAITING

    async def _sync_order(self, order_id: str, payment: dict[str, Any], status: PaymentStatus) -> None:
        """Sync order status from payment status."""

        if status in {PaymentStatus.CONFIRMED, PaymentStatus.OVERPAID}:
            await self.orders.mark_paid_and_queue(order_id)
        elif status == PaymentStatus.LATE_PAID:
            await self.orders.transition(order_id, OrderStatus.ISSUE)
        elif status == PaymentStatus.PARTIALLY_PAID:
            await self.orders.transition(order_id, OrderStatus.PARTIALLY_PAID)
        elif status == PaymentStatus.DETECTED:
            await self.orders.transition(order_id, OrderStatus.PAYMENT_DETECTED)
        elif status == PaymentStatus.EXPIRED and str(payment["status"]) != PaymentStatus.EXPIRED.value:
            await self.orders.transition(order_id, OrderStatus.EXPIRED)
