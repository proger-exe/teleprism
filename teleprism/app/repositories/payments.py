"""Payment repository."""

from typing import Any

import aiosqlite
import orjson

from teleprism.app.core.time import iso_now
from teleprism.app.repositories.base import fetch_all, fetch_one


class PaymentRepository:
    """Persist payments and transactions."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Store database connection."""

        self.db = db

    async def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Insert payment row."""

        keys = ", ".join(payload)
        placeholders = ", ".join("?" for _ in payload)
        await self.db.execute(
            f"INSERT INTO payments ({keys}) VALUES ({placeholders})",  # noqa: S608
            tuple(payload.values()),
        )
        return await self.get(payload["id"]) or {}

    async def get(self, payment_id: str) -> dict[str, Any] | None:
        """Return payment by ID."""

        return await fetch_one(self.db, "SELECT * FROM payments WHERE id = ?", (payment_id,))

    async def by_order(self, order_id: str) -> dict[str, Any] | None:
        """Return payment by order."""

        return await fetch_one(self.db, "SELECT * FROM payments WHERE order_id = ?", (order_id,))

    async def due_for_poll(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return payments due for polling."""

        return await fetch_all(
            self.db,
            """
            SELECT * FROM payments
            WHERE status IN ('WAITING', 'DETECTED', 'PARTIALLY_PAID', 'EXPIRED')
              AND next_poll_at <= ?
              AND grace_expires_at > ?
            ORDER BY next_poll_at
            LIMIT ?
            """,
            (iso_now(), iso_now(), limit),
        )

    async def update_address(self, payment_id: str, payload: dict[str, Any]) -> None:
        """Store provider address response."""

        await self.db.execute(
            """
            UPDATE payments
            SET address_in = ?, address_out = ?, callback_url = ?, minimum_transaction = ?,
                status = 'WAITING', raw_create_response = ?
            WHERE id = ?
            """,
            (
                payload.get("address_in"),
                payload.get("address_out"),
                payload.get("callback_url"),
                str(payload.get("minimum_transaction_coin", "")),
                orjson.dumps(payload).decode(),
                payment_id,
            ),
        )

    async def mark_create_failed(self, payment_id: str, error: str) -> None:
        """Mark address creation as failed so checkout can retry."""

        await self.db.execute(
            """
            UPDATE payments
            SET status = 'FAILED',
                poll_failures = poll_failures + 1,
                last_polled_at = ?,
                raw_create_response = ?
            WHERE id = ?
            """,
            (iso_now(), orjson.dumps({"error": error[:500]}).decode(), payment_id),
        )

    async def add_or_update_transaction(self, payment_id: str, ticker: str, tx: dict[str, Any]) -> None:
        """Insert or update a transaction by unique txid."""

        now = iso_now()
        await self.db.execute(
            """
            INSERT INTO payment_transactions
                (payment_id, ticker, txid_in, txid_out, value_coin, value_forwarded_coin,
                 fee_coin, confirmations, is_pending, is_confirmed, first_seen_at, updated_at, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, txid_in) DO UPDATE SET
                txid_out = excluded.txid_out,
                confirmations = excluded.confirmations,
                is_pending = excluded.is_pending,
                is_confirmed = excluded.is_confirmed,
                updated_at = excluded.updated_at,
                raw_data = excluded.raw_data
            """,
            (
                payment_id,
                ticker,
                tx["txid_in"],
                tx.get("txid_out"),
                str(tx.get("value_coin", "0")),
                str(tx.get("value_forwarded_coin", "")),
                str(tx.get("fee_coin", "")),
                int(tx.get("confirmations", 0)),
                int(bool(tx.get("pending", False))),
                int(bool(tx.get("confirmed", False))),
                now,
                now,
                orjson.dumps(tx).decode(),
            ),
        )

    async def transactions(self, payment_id: str) -> list[dict[str, Any]]:
        """Return payment transactions."""

        return await fetch_all(
            self.db,
            "SELECT * FROM payment_transactions WHERE payment_id = ?",
            (payment_id,),
        )

    async def update_amounts(
        self,
        payment_id: str,
        confirmed: str,
        pending: str,
        overpaid: str,
        status: str,
        next_poll_at: str,
    ) -> None:
        """Update payment totals and status."""

        await self.db.execute(
            """
            UPDATE payments
            SET confirmed_amount = ?, pending_amount = ?, overpaid_amount = ?,
                status = ?, last_polled_at = ?, next_poll_at = ?
            WHERE id = ?
            """,
            (confirmed, pending, overpaid, status, iso_now(), next_poll_at, payment_id),
        )

    async def mark_failure(self, payment_id: str, next_poll_at: str) -> None:
        """Record a polling failure."""

        await self.db.execute(
            """
            UPDATE payments
            SET poll_failures = poll_failures + 1, last_polled_at = ?, next_poll_at = ?
            WHERE id = ?
            """,
            (iso_now(), next_poll_at, payment_id),
        )
