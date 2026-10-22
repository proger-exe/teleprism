"""User order keyboards."""

from aiogram.types import InlineKeyboardMarkup

from teleprism.app.utils.callbacks import cb
from teleprism.app.utils.telegram import button


def orders_menu() -> InlineKeyboardMarkup:
    """Build user orders menu keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [button("Главное меню", callback_data=cb("home"))],
        ]
    )


def completed_order(order_id: str) -> InlineKeyboardMarkup:
    """Build completed order keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "Stars получены",
                    callback_data=cb("order", "received", order_id),
                    icon_env="PREMIUM_EMOJI_SUCCESS_ID",
                    style="success",
                )
            ],
            [
                button(
                    "Есть проблема",
                    callback_data=cb("order", "issue", order_id),
                    icon_env="PREMIUM_EMOJI_WARNING_ID",
                    style="danger",
                )
            ],
            [
                button(
                    "Купить ещё",
                    callback_data=cb("buy", "start"),
                    icon_env="PREMIUM_EMOJI_STAR_ID",
                    style="primary",
                )
            ],
        ]
    )
