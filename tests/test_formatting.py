"""Telegram formatting tests."""

from pytest import MonkeyPatch

from teleprism.app.keyboards.common import main_menu
from teleprism.app.presenters.home import welcome
from teleprism.app.presenters.order import history
from teleprism.app.utils.telegram import button, heading


def test_heading_is_bold_html() -> None:
    """Message heading is bold HTML."""

    assert heading("◈", "TelePrism", "MISSING_ID") == "<b>◈ TelePrism</b>"


def test_heading_custom_emoji_uses_valid_placeholder(monkeypatch: MonkeyPatch) -> None:
    """Telegram custom emoji entity uses emoji placeholder text."""

    monkeypatch.setenv("PREMIUM_EMOJI_PRISM_ID", "5359719332542718652")
    assert (
        heading("◈", "TelePrism", "PREMIUM_EMOJI_PRISM_ID")
        == '<b><tg-emoji emoji-id="5359719332542718652">💎</tg-emoji> TelePrism</b>'
    )


def test_welcome_heading_is_bold() -> None:
    """Welcome starts with a bold heading."""

    assert welcome().startswith("<b>")


def test_order_history_has_no_listing() -> None:
    """User order screen does not render order rows."""

    result = history()
    assert result.startswith("<b>")
    assert "#" not in result
    assert "История заказов скрыта." in result


def test_main_menu_is_inline() -> None:
    """Main menu uses inline buttons only."""

    markup = main_menu()
    assert markup.inline_keyboard


def test_button_uses_custom_emoji_attribute(monkeypatch: MonkeyPatch) -> None:
    """Button premium emoji is sent through icon_custom_emoji_id."""

    monkeypatch.setenv("PREMIUM_EMOJI_STAR_ID", "5258165702707125574")
    result = button("Купить Stars", callback_data="buy:start", icon_env="PREMIUM_EMOJI_STAR_ID", style="primary")
    assert result.text == "Купить Stars"
    assert result.icon_custom_emoji_id == "5258165702707125574"
    assert result.style == "primary"


def test_button_uses_builtin_custom_emoji_default(monkeypatch: MonkeyPatch) -> None:
    """Button premium emoji works even when .env values are not exported."""

    monkeypatch.delenv("PREMIUM_EMOJI_STAR_ID", raising=False)
    result = button("Купить Stars", callback_data="buy:start", icon_env="PREMIUM_EMOJI_STAR_ID")
    assert result.icon_custom_emoji_id == "5258165702707125574"
