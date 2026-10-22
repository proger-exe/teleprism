"""Typed row models."""

from dataclasses import dataclass


@dataclass(slots=True)
class User:
    """User row."""

    id: int
    telegram_id: int
    username: str | None
    role: str


@dataclass(slots=True)
class Order:
    """Order row."""

    id: str
    number: int
    buyer_id: int
    recipient_username: str | None
    stars_count: int | None
    total_amount: str | None
    status: str


@dataclass(slots=True)
class Payment:
    """Payment row."""

    id: str
    order_id: str
    expected_amount: str
    confirmed_amount: str
    pending_amount: str
    overpaid_amount: str
    status: str
    callback_url: str | None
