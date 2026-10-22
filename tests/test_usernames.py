"""Username normalization tests."""

import pytest

from teleprism.app.core.errors import ValidationError
from teleprism.app.utils.usernames import normalize_username


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("@shelby_dev", "shelby_dev"),
        ("shelby123", "shelby123"),
        ("https://t.me/shelby_dev", "shelby_dev"),
        ("t.me/shelby_dev", "shelby_dev"),
    ],
)
def test_normalize_username_accepts_supported_forms(raw: str, expected: str) -> None:
    """Supported username forms normalize to username only."""

    assert normalize_username(raw) == expected


@pytest.mark.parametrize("raw", ["abc", "bad name", "t.me/+invite", "joinchat/test", "userbot"])
def test_normalize_username_rejects_invalid_values(raw: str) -> None:
    """Invalid usernames raise validation errors."""

    with pytest.raises(ValidationError):
        normalize_username(raw)
