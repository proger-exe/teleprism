"""Order expiration worker."""

import asyncio

from teleprism.app.config import Settings
from teleprism.app.container import build_services
from teleprism.app.core.enums import OrderStatus
from teleprism.app.core.time import iso_now
from teleprism.app.db.connection import Database
from teleprism.app.repositories.base import fetch_all


class OrderExpirationWorker:
    """Expire unpaid orders while grace polling continues."""

    def __init__(self, database: Database, settings: Settings) -> None:
        """Store dependencies."""

        self.database = database
        self.settings = settings

    async def run(self) -> None:
        """Run forever until cancelled."""

        while True:
            await self.tick()
            await asyncio.sleep(60)

    async def tick(self) -> None:
        """Expire due unpaid orders once."""

        async with self.database.connect() as db:
            services = build_services(db, self.settings)
            rows = await fetch_all(
                db,
                """
                SELECT * FROM orders
                WHERE status IN ('DRAFT', 'AWAITING_PAYMENT', 'PAYMENT_DETECTED', 'PARTIALLY_PAID')
                  AND expires_at <= ?
                """,
                (iso_now(),),
            )
            for row in rows:
                await services.orders.transition(str(row["id"]), OrderStatus.EXPIRED)
