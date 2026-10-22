"""Order presenters."""

from teleprism.app.core.money import format_usdt
from teleprism.app.utils.telegram import h, heading

STATUS_LABELS = {
    "AWAITING_PAYMENT": "⏳ Ожидает оплаты",
    "PAYMENT_DETECTED": "◌ Оплата обнаружена",
    "PARTIALLY_PAID": "◒ Оплачен частично",
    "PAID": "✓ Оплачен",
    "QUEUED": "◆ В очереди",
    "ASSIGNED": "◆ Выполняется",
    "PROCESSING": "◆ Выполняется",
    "COMPLETED": "✓ Выполнен",
    "CANCELED": "× Отменён",
    "EXPIRED": "⌛ Истёк",
    "ISSUE": "⚠ Проблема",
}


def order_card(order: dict[str, object]) -> str:
    """Render one order."""

    title = heading("◆", f"Заказ #{order['number']}", "PREMIUM_EMOJI_ORDER_ID")
    return (
        f"{title}\n\n"
        f"Статус: {STATUS_LABELS.get(str(order['status']), str(order['status']))}\n"
        f"Получатель: @{h(order['recipient_username'])}\n"
        f"Количество: {order['stars_count']} Stars\n"
        f"Стоимость: {format_usdt(str(order['total_amount'] or '0'))} USDT"
    )


def history() -> str:
    """Render user orders screen without listing order history."""

    return (
        f"{heading('◆', 'Мои заказы', 'PREMIUM_EMOJI_ORDER_ID')}\n\n"
        "История заказов скрыта.\n"
        "Актуальный статус приходит в карточке заказа после покупки."
    )


def completed(order: dict[str, object]) -> str:
    """Render completed order."""

    return (
        f"{heading('✓', 'Заказ выполнен', 'PREMIUM_EMOJI_SUCCESS_ID')}\n\n"
        f"Заказ: #{order['number']}\n"
        f"Получатель: @{h(order['recipient_username'])}\n"
        f"Отправлено: {order['stars_count']} Stars\n\n"
        "Проверьте баланс Telegram Stars."
    )
