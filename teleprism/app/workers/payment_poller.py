"""CryptAPI payment polling worker."""

import asyncio

from teleprism.app.config import Settings
from teleprism.app.container import build_services
from teleprism.app.db.connection import Database


class PaymentPoller:
    """Poll active CryptAPI payments inside the bot process."""

    def __init__(self, database: Database, settings: Settings) -> None:
        """Store dependencies."""

        self.database = database
        self.settings = settings
        self.semaphore = asyncio.Semaphore(settings.payment_poll_concurrency)

    async def run(self) -> None:
        """Run forever until cancelled."""

        while True:
            await self.tick()
            await asyncio.sleep(5)

    async def tick(self) -> None:
        """Poll due payments once."""

        async with self.database.connect() as db:
            services = build_services(db, self.settings)
            payments = await services.payment_repo.due_for_poll()
        await asyncio.gather(*(self._poll_one(payment) for payment in payments))

    async def _poll_one(self, payment: dict[str, object]) -> None:
        """Poll one payment under concurrency limit."""

        async with self.semaphore, self.database.connect() as db:
            services = build_services(db, self.settings)
            await services.payments.poll_payment(payment)
