"""Callback-data constants and helpers."""


def cb(*parts: object) -> str:
    """Build compact callback data."""

    return ":".join(str(part) for part in parts)


def parse_cb(data: str) -> list[str]:
    """Split callback data."""

    return data.split(":")
