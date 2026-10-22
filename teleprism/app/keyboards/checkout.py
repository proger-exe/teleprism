"""Checkout inline keyboards."""

from aiogram.types import InlineKeyboardMarkup

from teleprism.app.utils.callbacks import cb
from teleprism.app.utils.telegram import button


def recipient_choice(has_username: bool) -> InlineKeyboardMarkup:
    """Build recipient choice keyboard."""

    rows = []
    if has_username:
        rows.append([button("Мне", callback_data=cb("buy", "me"), icon_env="PREMIUM_EMOJI_STAR_ID", style="primary")])
    rows.append([button("Другому пользователю", callback_data=cb("buy", "other"))])
    rows.append([button("Главное меню", callback_data=cb("home"))])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def recipient_confirm() -> InlineKeyboardMarkup:
    """Build recipient confirmation keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "Да, продолжить",
                    callback_data=cb("buy", "stars"),
                    icon_env="PREMIUM_EMOJI_SUCCESS_ID",
                    style="success",
                )
            ],
            [button("Указать другой", callback_data=cb("buy", "other"))],
            [button("Назад", callback_data=cb("buy", "start"))],
        ]
    )


def packages(packages_rows: list[dict[str, object]]) -> InlineKeyboardMarkup:
    """Build package selection keyboard."""

    buttons = [
        button(
            f"{row['stars_count']} Stars",
            callback_data=cb("buy", "pkg", row["stars_count"]),
            icon_env="PREMIUM_EMOJI_STAR_ID",
        )
        for row in packages_rows
    ]
    rows = [buttons[index : index + 2] for index in range(0, len(buttons), 2)]
    rows.append([button("Другое количество", callback_data=cb("buy", "custom"))])
    rows.append([button("Назад", callback_data=cb("buy", "start"))])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def order_confirm(order_id: str) -> InlineKeyboardMarkup:
    """Build order confirmation keyboard."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "Подтвердить заказ",
                    callback_data=cb("order", "confirm", order_id),
                    icon_env="PREMIUM_EMOJI_SUCCESS_ID",
                    style="success",
                )
            ],
            [button("Изменить количество", callback_data=cb("buy", "stars"))],
            [button("Изменить получателя", callback_data=cb("buy", "start"))],
            [
                button(
                    "Отменить",
                    callback_data=cb("order", "cancel", order_id),
                    icon_env="PREMIUM_EMOJI_WARNING_ID",
                    style="danger",
                )
            ],
        ]
    )
