"""Application bootstrap."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from teleprism.app.config import Settings
from teleprism.app.db.connection import Database
from teleprism.app.db.migrations import migrate
from teleprism.app.handlers.admin import dashboard as admin_dashboard
from teleprism.app.handlers.admin import managers as admin_managers
from teleprism.app.handlers.admin import orders as admin_orders
from teleprism.app.handlers.admin import payments as admin_payments
from teleprism.app.handlers.admin import pricing as admin_pricing
from teleprism.app.handlers.admin import settings as admin_settings
from teleprism.app.handlers.admin import users as admin_users
from teleprism.app.handlers.manager import assignment, execution, history, queue
from teleprism.app.handlers.user import checkout, menu, orders, payment, start, support
from teleprism.app.middlewares.database import DatabaseMiddleware
from teleprism.app.middlewares.maintenance import MaintenanceMiddleware
from teleprism.app.middlewares.session import SessionMiddleware
from teleprism.app.middlewares.throttling import ThrottlingMiddleware
from teleprism.app.middlewares.user import UserMiddleware
from teleprism.app.workers.backups import BackupWorker
from teleprism.app.workers.manager_reminders import ManagerReminderWorker
from teleprism.app.workers.notification_outbox import NotificationOutboxWorker
from teleprism.app.workers.order_expiration import OrderExpirationWorker
from teleprism.app.workers.payment_poller import PaymentPoller
from teleprism.app.workers.runner import WorkerRunner


async def create_dispatcher(settings: Settings, database: Database) -> Dispatcher:
    """Create configured aiogram dispatcher."""

    async with database.connect() as db:
        await migrate(db)
    dispatcher = Dispatcher()
    database_middleware = DatabaseMiddleware(database, settings)
    for observer in (dispatcher.message, dispatcher.callback_query):
        observer.middleware(database_middleware)
        observer.middleware(UserMiddleware())
        observer.middleware(SessionMiddleware())
        observer.middleware(MaintenanceMiddleware())
        observer.middleware(ThrottlingMiddleware())
    for router in (
        start.router,
        menu.router,
        payment.router,
        orders.router,
        support.router,
        queue.router,
        assignment.router,
        execution.router,
        history.router,
        admin_dashboard.router,
        admin_orders.router,
        admin_payments.router,
        admin_pricing.router,
        admin_managers.router,
        admin_users.router,
        admin_settings.router,
        checkout.router,
    ):
        dispatcher.include_router(router)
    return dispatcher


def create_bot(settings: Settings) -> Bot:
    """Create aiogram bot."""

    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def start_workers(settings: Settings, database: Database, bot: Bot) -> WorkerRunner:
    """Start background workers."""

    runner = WorkerRunner()
    runner.add(PaymentPoller(database, settings).run)
    runner.add(OrderExpirationWorker(database, settings).run)
    runner.add(ManagerReminderWorker(database, settings).run)
    runner.add(NotificationOutboxWorker(database, settings, bot).run)
    runner.add(BackupWorker(settings).run)
    return runner
