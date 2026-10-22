# TelePrism

Telegram shop bot with crypto checkout. The example catalogue sells Telegram Stars packages; the interesting part is the payment pipeline: USDT TRC20 deposits through CryptAPI, polled rather than webhooked, with partial / over / late payment handling, manager fulfilment queue with SLA timers, outbox notifications and SQLite backups.

Strict mypy, ruff, black, 28 tests. No HTTP server, no Redis, no Mini App: one long-polling process.

## Flow

```
/start → package or custom amount → order (DRAFT)
      → confirm → provider.create_address → AWAITING_PAYMENT, QR + address
      → poller: provider.logs every 10–120 s → WAITING / DETECTED / PARTIALLY_PAID / CONFIRMED / OVERPAID / LATE_PAID / EXPIRED
      → CONFIRMED → manager chat gets the order → manager marks delivered (proof optional) → buyer notified
```

## Payment providers

| `PAYMENTS_PROVIDER` | What happens |
|---|---|
| `cryptapi` | Real USDT TRC20 via [CryptAPI](https://cryptapi.io): set `CRYPTAPI_WALLET_ADDRESS` (your receiving wallet) |
| `mock` | Demo mode: a fake address is issued and every order is "paid" in full after `MOCK_CONFIRM_SECONDS`. Nothing touches a blockchain. |

Both implement `integrations/base.py:PaymentProvider` (`callback_url`, `create_address`, `logs`); services never import a concrete provider.

## Run

```bash
cp example.env .env      # BOT_TOKEN, OWNER_IDS, MANAGER_CHAT_ID, PAYMENTS_PROVIDER
uv sync
uv run teleprism
```

Docker: `docker compose up -d --build` (SQLite in `./data`, backups rotated by `BACKUP_RETENTION_DAYS`).

## Checks

```bash
uv run ruff check . && uv run black --check . && uv run mypy teleprism && uv run pytest
```

## Layout

```
teleprism/app/
  bot.py, bootstrap.py, container.py, config.py   entry point, wiring, DI, settings
  handlers/, keyboards/, presenters/  user, manager, owner flows (aiogram 3 + Raito hot reload)
  services/                           checkout, payment, pricing, order, manager, support, notifications, audit
  repositories/                       SQLite access
  integrations/base.py                PaymentProvider protocol
  integrations/cryptapi/              client, provider, typed schemas, log parser
  integrations/mock/                  demo provider
  workers/                            payment poller, outbox, backups
  db/                                 connection, migrations
docs/TECHTASK.md                      original spec (RU)
```

## License

MIT
