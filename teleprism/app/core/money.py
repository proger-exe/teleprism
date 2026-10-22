"""Decimal money helpers."""

from decimal import ROUND_HALF_UP, Decimal

USDT_QUANT = Decimal("0.000001")
DISPLAY_QUANT = Decimal("0.01")


def money(value: str | int | Decimal) -> Decimal:
    """Normalize a money value to Decimal."""

    return Decimal(str(value))


def quantize_usdt(value: Decimal) -> Decimal:
    """Quantize an internal USDT value."""

    return value.quantize(USDT_QUANT, rounding=ROUND_HALF_UP)


def format_usdt(value: Decimal | str) -> str:
    """Format USDT for Telegram messages."""

    amount = money(value) if not isinstance(value, Decimal) else value
    return f"{amount.quantize(DISPLAY_QUANT, rounding=ROUND_HALF_UP)}"
