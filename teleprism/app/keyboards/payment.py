"""Payment keyboards."""

from aiogram.types import CopyTextButton, InlineKeyboardMarkup

from teleprism.app.utils.callbacks import cb
from teleprism.app.utils.telegram import button


def payment(order_id: str, address: str, amount: str) -> InlineKeyboardMarkup:
    """Build payment keyboard with copy buttons."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [button("Скопировать адрес", copy_text=CopyTextButton(text=address))],
            [button("Скопировать сумму", copy_text=CopyTextButton(text=amount))],
            [
                button(
                    "Проверить оплату",
                    callback_data=cb("pay", "check", order_id),
                    icon_env="PREMIUM_EMOJI_WAIT_ID",
                    style="primary",
                )
            ],
            [
                button(
                    "Отменить заказ",
                    callback_data=cb("order", "cancel", order_id),
                    icon_env="PREMIUM_EMOJI_WARNING_ID",
                    style="danger",
                )
            ],
        ]
    )


def paid(order_id: str) -> InlineKeyboardMarkup:
    """Build paid order keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "Открыть заказ",
                    callback_data=cb("order", "open", order_id),
                    icon_env="PREMIUM_EMOJI_ORDER_ID",
                    style="primary",
                )
            ],
            [button("Мои заказы", callback_data=cb("orders", "list", 0), icon_env="PREMIUM_EMOJI_ORDER_ID")],
            [button("Поддержка", callback_data=cb("support"), icon_env="PREMIUM_EMOJI_WARNING_ID")],
        ]
    )
