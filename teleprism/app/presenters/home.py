"""Home screen presenters."""

from teleprism.app.utils.telegram import heading


def welcome() -> str:
    """Render welcome screen."""

    return (
        f"{heading('◈', 'TelePrism', 'PREMIUM_EMOJI_PRISM_ID')}\n\n"
        "Покупка Telegram Stars с оплатой в криптовалюте.\n\n"
        "Выберите количество Stars, оплатите заказ и дождитесь выполнения менеджером."
    )


def info() -> str:
    """Render information screen."""

    return (
        f"{heading('◈', 'TelePrism', 'PREMIUM_EMOJI_PRISM_ID')}\n\n"
        "Бот принимает оплату USDT TRC20 и передаёт оплаченные заказы менеджерам.\n"
        "Stars отправляются вручную через официальный Telegram flow."
    )
