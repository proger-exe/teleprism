"""Admin keyboards."""

from aiogram.types import InlineKeyboardMarkup

from teleprism.app.utils.callbacks import cb
from teleprism.app.utils.telegram import button


def admin_menu() -> InlineKeyboardMarkup:
    """Build admin dashboard keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button("Заказы", callback_data=cb("admin", "orders"), icon_env="PREMIUM_EMOJI_ORDER_ID"),
                button("Платежи", callback_data=cb("admin", "payments"), icon_env="PREMIUM_EMOJI_PRISM_ID"),
            ],
            [
                button("Тарифы", callback_data=cb("admin", "packages"), icon_env="PREMIUM_EMOJI_STAR_ID"),
                button("Менеджеры", callback_data=cb("admin", "managers"), icon_env="PREMIUM_EMOJI_ORDER_ID"),
            ],
            [
                button("Пользователи", callback_data=cb("admin", "users")),
                button("Статистика", callback_data=cb("admin", "stats")),
            ],
            [
                button("Настройки", callback_data=cb("admin", "settings")),
                button("Журнал", callback_data=cb("admin", "log")),
            ],
        ]
    )
