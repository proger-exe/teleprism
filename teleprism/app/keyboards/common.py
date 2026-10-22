"""Common Telegram keyboards."""

from aiogram.types import InlineKeyboardMarkup

from teleprism.app.utils.callbacks import cb
from teleprism.app.utils.telegram import button


def main_menu() -> InlineKeyboardMarkup:
    """Build inline main menu keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "Купить Stars",
                    callback_data=cb("buy", "start"),
                    icon_env="PREMIUM_EMOJI_STAR_ID",
                    style="primary",
                )
            ],
            [
                button("Мои заказы", callback_data=cb("orders", "list", 0), icon_env="PREMIUM_EMOJI_ORDER_ID"),
                button("Прайс", callback_data=cb("price"), icon_env="PREMIUM_EMOJI_PRISM_ID"),
            ],
            [
                button("Поддержка", callback_data=cb("support"), icon_env="PREMIUM_EMOJI_WARNING_ID"),
                button("Информация", callback_data=cb("info"), icon_env="PREMIUM_EMOJI_PRISM_ID"),
            ],
        ],
    )
