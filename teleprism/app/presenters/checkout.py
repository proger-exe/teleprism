"""Checkout presenters."""

from teleprism.app.core.money import format_usdt
from teleprism.app.utils.telegram import h, heading


def recipient_start(has_username: bool) -> str:
    """Render recipient choice."""

    text = f"{heading('✦', 'Покупка Stars', 'PREMIUM_EMOJI_STAR_ID')}\n\nКому нужно отправить Stars?"
    if not has_username:
        text += "\n\nУ вашего аккаунта нет публичного username.\nУкажите username получателя вручную."
    return text


def recipient_confirm(username: str) -> str:
    """Render recipient confirmation."""

    return f"Получатель: @{h(username)}\n\nПроверьте написание.\nПосле оплаты получателя изменить нельзя."


def package_choice() -> str:
    """Render package choice."""

    title = heading("✦", "Выберите количество", "PREMIUM_EMOJI_STAR_ID")
    return f"{title}\n\nЧем больше пакет, тем ниже цена за одну Star."


def custom_stars(min_stars: int, max_stars: int) -> str:
    """Render custom Stars prompt."""

    return f"Введите количество Stars числом.\n\nМинимум: {min_stars}\nМаксимум: {max_stars}"


def order_summary(order: dict[str, object]) -> str:
    """Render order summary."""

    return (
        f"{heading('◆', 'Новый заказ', 'PREMIUM_EMOJI_ORDER_ID')}\n\n"
        f"Получатель: @{h(order['recipient_username'])}\n"
        f"Количество: {order['stars_count']} Stars\n"
        f"Стоимость: {format_usdt(str(order['total_amount']))} USDT\n"
        "Сеть оплаты: TRC20\n"
        "Срок оплаты: 30 минут\n"
        "Обычное выполнение: до 15 минут после оплаты\n\n"
        "Проверьте данные перед созданием счёта."
    )
