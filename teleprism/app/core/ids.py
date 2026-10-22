"""Identifier helpers."""

from secrets import token_urlsafe
from uuid import uuid4


def new_uuid() -> str:
    """Return a UUID string."""

    return str(uuid4())


def new_nonce() -> str:
    """Return callback nonce."""

    return token_urlsafe(18)
