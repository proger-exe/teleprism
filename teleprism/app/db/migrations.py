"""Idempotent SQLite migrations."""

from typing import Any

from teleprism.app.core.time import iso_now

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language_code TEXT,
    role TEXT NOT NULL DEFAULT 'USER',
    is_blocked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    number INTEGER NOT NULL UNIQUE,
    buyer_id INTEGER NOT NULL,
    recipient_username TEXT,
    stars_count INTEGER,
    package_id INTEGER,
    unit_price TEXT,
    base_amount TEXT,
    fixed_fee TEXT,
    total_amount TEXT,
    currency TEXT NOT NULL DEFAULT 'USDT',
    status TEXT NOT NULL,
    assigned_manager_id INTEGER,
    manager_comment TEXT,
    proof_file_id TEXT,
    issue_reason TEXT,
    screen_chat_id INTEGER,
    screen_message_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    expires_at TEXT,
    paid_at TEXT,
    queued_at TEXT,
    assigned_at TEXT,
    processing_at TEXT,
    completed_at TEXT,
    customer_confirmed_at TEXT,
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (assigned_manager_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_orders_buyer ON orders(buyer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_queue ON orders(status, queued_at);
CREATE INDEX IF NOT EXISTS idx_orders_manager ON orders(assigned_manager_id, status);

CREATE TABLE IF NOT EXISTS star_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stars_count INTEGER NOT NULL,
    price_usdt TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    provider TEXT NOT NULL DEFAULT 'CRYPTAPI',
    ticker TEXT NOT NULL,
    network TEXT NOT NULL,
    expected_amount TEXT NOT NULL,
    confirmed_amount TEXT NOT NULL DEFAULT '0',
    pending_amount TEXT NOT NULL DEFAULT '0',
    overpaid_amount TEXT NOT NULL DEFAULT '0',
    address_in TEXT,
    address_out TEXT,
    callback_url TEXT,
    callback_nonce TEXT,
    minimum_transaction TEXT,
    status TEXT NOT NULL,
    poll_failures INTEGER NOT NULL DEFAULT 0,
    last_polled_at TEXT,
    next_poll_at TEXT,
    created_at TEXT NOT NULL,
    detected_at TEXT,
    confirmed_at TEXT,
    expires_at TEXT NOT NULL,
    grace_expires_at TEXT NOT NULL,
    raw_create_response TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS payment_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    txid_in TEXT NOT NULL,
    txid_out TEXT,
    value_coin TEXT NOT NULL,
    value_forwarded_coin TEXT,
    fee_coin TEXT,
    confirmations INTEGER NOT NULL DEFAULT 0,
    is_pending INTEGER NOT NULL,
    is_confirmed INTEGER NOT NULL,
    first_seen_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    raw_data TEXT,
    UNIQUE(ticker, txid_in),
    FOREIGN KEY (payment_id) REFERENCES payments(id)
);

CREATE TABLE IF NOT EXISTS order_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    actor_user_id INTEGER,
    event_type TEXT NOT NULL,
    old_status TEXT,
    new_status TEXT,
    payload TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (actor_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS support_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_id TEXT,
    category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN',
    message TEXT,
    assigned_admin_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    closed_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS outbox_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    message_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    attempts INTEGER NOT NULL DEFAULT 0,
    next_attempt_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    sent_at TEXT,
    last_error TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_by INTEGER,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_sessions (
    user_id INTEGER PRIMARY KEY,
    state TEXT,
    data TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    expires_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

DEFAULT_PACKAGES = ((50, "1.20"), (100, "2.20"), (250, "5.10"), (500, "9.80"), (1000, "18.90"))


async def migrate(db: Any) -> None:
    """Apply schema and seed default packages."""

    await db.execute("PRAGMA journal_mode = WAL")
    await db.execute("PRAGMA busy_timeout = 30000")
    await db.execute("PRAGMA foreign_keys = ON")
    await db.execute("PRAGMA synchronous = NORMAL")
    await db.executescript(SCHEMA)
    cursor = await db.execute("SELECT COUNT(*) AS count FROM star_packages")
    row = await cursor.fetchone()
    if row is None:
        raise RuntimeError("Could not inspect default packages.")
    if int(row["count"]) == 0:
        now = iso_now()
        await db.executemany(
            """
            INSERT INTO star_packages (stars_count, price_usdt, sort_order, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(stars, price, index, now, now) for index, (stars, price) in enumerate(DEFAULT_PACKAGES)],
        )
    await db.commit()
