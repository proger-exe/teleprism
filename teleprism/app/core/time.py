"""Time helpers."""

from datetime import UTC, datetime, timedelta


def utcnow() -> datetime:
    """Return current UTC datetime."""

    return datetime.now(UTC)


def iso_now() -> str:
    """Return current UTC time as ISO string."""

    return utcnow().isoformat()


def iso_after(**kwargs: float) -> str:
    """Return UTC ISO timestamp after a timedelta."""

    return (utcnow() + timedelta(**kwargs)).isoformat()


def parse_iso(value: str) -> datetime:
    """Parse ISO timestamp into datetime."""

    return datetime.fromisoformat(value)
