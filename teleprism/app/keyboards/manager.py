"""Manager keyboards."""

from aiogram.types import InlineKeyboardMarkup

from teleprism.app.utils.callbacks import cb
from teleprism.app.utils.telegram import button


def queue_card(order_id: str) -> InlineKeyboardMarkup:
    """Build manager queue card keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "Взять заказ",
                    callback_data=cb("mgr", "take", order_id),
                    icon_env="PREMIUM_EMOJI_ORDER_ID",
                    style="primary",
                )
            ],
            [button("Открыть детали", callback_data=cb("mgr", "open", order_id))],
        ]
    )


def assigned(order_id: str) -> InlineKeyboardMarkup:
    """Build assigned order keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "Начать выполнение",
                    callback_data=cb("mgr", "start", order_id),
                    icon_env="PREMIUM_EMOJI_SUCCESS_ID",
                    style="success",
                )
            ],
            [button("Вернуть в очередь", callback_data=cb("mgr", "return", order_id))],
            [
                button(
                    "Проблема",
                    callback_data=cb("mgr", "issue", order_id),
                    icon_env="PREMIUM_EMOJI_WARNING_ID",
                    style="danger",
                )
            ],
        ]
    )


def processing(order_id: str, username: str) -> InlineKeyboardMarkup:
    """Build processing order keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [button(f"Открыть @{username}", url=f"https://t.me/{username}")],
            [
                button(
                    "Stars отправлены",
                    callback_data=cb("mgr", "done", order_id),
                    icon_env="PREMIUM_EMOJI_SUCCESS_ID",
                    style="success",
                )
            ],
            [
                button(
                    "Возникла проблема",
                    callback_data=cb("mgr", "issue", order_id),
                    icon_env="PREMIUM_EMOJI_WARNING_ID",
                    style="danger",
                )
            ],
        ]
    )


def confirm_done(order_id: str) -> InlineKeyboardMarkup:
    """Build completion confirmation keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "Подтвердить выполнение",
                    callback_data=cb("mgr", "confirm_done", order_id),
                    icon_env="PREMIUM_EMOJI_SUCCESS_ID",
                    style="success",
                )
            ],
            [button("Назад", callback_data=cb("mgr", "open", order_id))],
        ]
    )
