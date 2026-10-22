"""CryptAPI Logs parser."""

from teleprism.app.integrations.cryptapi.schemas import LogsResponse, TransactionItem


def parse_logs(payload: dict[str, object]) -> LogsResponse:
    """Parse a CryptAPI logs payload defensively."""

    raw_items = payload.get("callbacks") or payload.get("callback_logs") or []
    items: list[TransactionItem] = []
    if isinstance(raw_items, list):
        for raw_item in raw_items:
            if not isinstance(raw_item, dict) or not raw_item.get("txid_in"):
                continue
            item = TransactionItem(
                txid_in=str(raw_item["txid_in"]),
                txid_out=str(raw_item["txid_out"]) if raw_item.get("txid_out") else None,
                value_coin=str(raw_item.get("value_coin", "0")),
                value_forwarded_coin=(
                    str(raw_item["value_forwarded_coin"]) if raw_item.get("value_forwarded_coin") is not None else None
                ),
                fee_coin=(str(raw_item["fee_coin"]) if raw_item.get("fee_coin") is not None else None),
                confirmations=int(raw_item.get("confirmations", 0)),
                pending=bool(raw_item.get("pending", False)),
                confirmed=bool(raw_item.get("confirmed", False)) or str(raw_item.get("result", "")).lower() == "sent",
                raw=raw_item,
            )
            items.append(item)
    return LogsResponse(callbacks=items)
