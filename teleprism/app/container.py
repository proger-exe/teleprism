"""Application dependency container."""

from dataclasses import dataclass
from typing import Any

from teleprism.app.config import Settings
from teleprism.app.integrations.base import PaymentProvider
from teleprism.app.integrations.cryptapi.provider import CryptAPIProvider
from teleprism.app.integrations.mock.provider import MockPaymentProvider
from teleprism.app.repositories.orders import OrderRepository
from teleprism.app.repositories.outbox import OutboxRepository
from teleprism.app.repositories.packages import PackageRepository
from teleprism.app.repositories.payments import PaymentRepository
from teleprism.app.repositories.sessions import SessionRepository
from teleprism.app.repositories.settings import SettingsRepository
from teleprism.app.repositories.tickets import TicketRepository
from teleprism.app.repositories.users import UserRepository
from teleprism.app.services.audit_service import AuditService
from teleprism.app.services.checkout_service import CheckoutService
from teleprism.app.services.manager_service import ManagerService
from teleprism.app.services.notification_service import NotificationService
from teleprism.app.services.order_service import OrderService
from teleprism.app.services.payment_service import PaymentService
from teleprism.app.services.pricing_service import PricingService
from teleprism.app.services.session_service import SessionService
from teleprism.app.services.support_service import SupportService
from teleprism.app.services.user_service import UserService


@dataclass(slots=True)
class Services:
    """Per-connection service bundle."""

    users: UserService
    sessions: SessionService
    pricing: PricingService
    checkout: CheckoutService
    orders: OrderService
    payments: PaymentService
    managers: ManagerService
    support: SupportService
    notifications: NotificationService
    audit: AuditService
    order_repo: OrderRepository
    payment_repo: PaymentRepository
    package_repo: PackageRepository
    user_repo: UserRepository
    outbox_repo: OutboxRepository
    settings_repo: SettingsRepository


def build_services(db: Any, settings: Settings) -> Services:
    """Build repositories and services for a SQLite connection."""

    users = UserRepository(db)
    sessions = SessionRepository(db)
    orders = OrderRepository(db)
    payments = PaymentRepository(db)
    packages = PackageRepository(db)
    tickets = TicketRepository(db)
    outbox = OutboxRepository(db)
    settings_repo = SettingsRepository(db)
    provider: PaymentProvider = (
        MockPaymentProvider(settings) if settings.payments_provider == "mock" else CryptAPIProvider(settings)
    )
    order_service = OrderService(orders)
    pricing = PricingService(packages, settings)
    return Services(
        users=UserService(users, settings),
        sessions=SessionService(sessions),
        pricing=pricing,
        checkout=CheckoutService(orders, payments, pricing, order_service, provider, settings),
        orders=order_service,
        payments=PaymentService(payments, order_service, provider, settings),
        managers=ManagerService(orders, order_service),
        support=SupportService(tickets),
        notifications=NotificationService(outbox),
        audit=AuditService(orders),
        order_repo=orders,
        payment_repo=payments,
        package_repo=packages,
        user_repo=users,
        outbox_repo=outbox,
        settings_repo=settings_repo,
    )
