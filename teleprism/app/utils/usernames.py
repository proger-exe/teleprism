"""Telegram username parsing."""

import re

from teleprism.app.core.errors import ValidationError

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{5,32}$")
INVITE_RE = re.compile(r"(joinchat/|\+)", re.IGNORECASE)


def normalize_username(raw: str) -> str:
    """Normalize a Telegram username without claiming existence."""

    value = raw.strip()
    if not value:
        raise ValidationError("Введите username.")
    if INVITE_RE.search(value):
        raise ValidationError("Инвайт-ссылки не подходят. Нужен публичный username.")
    value = re.sub(r"^https?://", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^t\.me/", "", value, flags=re.IGNORECASE)
    value = value.removeprefix("@")
    if "/" in value or "?" in value:
        raise ValidationError("Укажите только username, без лишних частей ссылки.")
    if not USERNAME_RE.fullmatch(value):
        raise ValidationError("Username должен быть 5-32 символа: латиница, цифры, подчёркивание.")
    if value.lower().endswith("bot"):
        raise ValidationError("Укажите username получателя, не ссылку на бота.")
    return value
