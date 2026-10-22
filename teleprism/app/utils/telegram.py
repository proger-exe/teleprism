"""Telegram rendering helpers."""

import html
import os

from aiogram.types import InlineKeyboardButton

DEFAULT_PREMIUM_EMOJI_IDS = {
    "PREMIUM_EMOJI_PRISM_ID": "5359719332542718652",
    "PREMIUM_EMOJI_STAR_ID": "5258165702707125574",
    "PREMIUM_EMOJI_ORDER_ID": "5253959125838090076",
    "PREMIUM_EMOJI_SUCCESS_ID": "5260416304224936047",
    "PREMIUM_EMOJI_WAIT_ID": "5258258882022612173",
    "PREMIUM_EMOJI_WARNING_ID": "5260249440450520061",
}

PREMIUM_EMOJI_PLACEHOLDERS = {
    "PREMIUM_EMOJI_PRISM_ID": "💎",
    "PREMIUM_EMOJI_STAR_ID": "⭐",
    "PREMIUM_EMOJI_ORDER_ID": "📦",
    "PREMIUM_EMOJI_SUCCESS_ID": "✅",
    "PREMIUM_EMOJI_WAIT_ID": "⏳",
    "PREMIUM_EMOJI_WARNING_ID": "⚠️",
}


def h(value: object) -> str:
    """Escape user-provided text for HTML parse mode."""

    return html.escape(str(value), quote=False)


def premium(symbol: str, env_name: str) -> str:
    """Render a Telegram Premium emoji when a custom emoji ID is configured."""

    emoji_id = premium_emoji_id(env_name)
    if not emoji_id:
        return symbol
    placeholder = PREMIUM_EMOJI_PLACEHOLDERS.get(env_name, "⭐")
    return f'<tg-emoji emoji-id="{h(emoji_id)}">{placeholder}</tg-emoji>'


def premium_emoji_id(env_name: str) -> str:
    """Resolve premium emoji ID from env or built-in defaults."""

    return os.getenv(env_name, DEFAULT_PREMIUM_EMOJI_IDS.get(env_name, "")).strip()


def heading(symbol: str, text: str, env_name: str) -> str:
    """Render a bold message heading with optional Premium emoji."""

    return f"<b>{premium(symbol, env_name)} {h(text)}</b>"


def button(
    text: str,
    *,
    callback_data: str | None = None,
    url: str | None = None,
    copy_text: object | None = None,
    icon_env: str | None = None,
    style: str | None = None,
) -> InlineKeyboardButton:
    """Build an inline button with optional premium emoji icon and Bot API style."""

    kwargs: dict[str, object] = {"text": text}
    if callback_data is not None:
        kwargs["callback_data"] = callback_data
    if url is not None:
        kwargs["url"] = url
    if copy_text is not None:
        kwargs["copy_text"] = copy_text
    if icon_env is not None:
        emoji_id = premium_emoji_id(icon_env)
        if emoji_id:
            kwargs["icon_custom_emoji_id"] = emoji_id
    if style is not None:
        kwargs["style"] = style
    return InlineKeyboardButton.model_validate(kwargs)
