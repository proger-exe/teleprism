"""Manager presenters."""

from teleprism.app.core.money import format_usdt
from teleprism.app.utils.telegram import h, heading


def queue_card(order: dict[str, object], buyer: dict[str, object] | None = None) -> str:
    """Render manager queue card."""

    buyer_name = f"@{buyer['username']}" if buyer and buyer.get("username") else str(order["buyer_id"])
    title = heading("◆", f"Новый оплаченный заказ #{order['number']}", "PREMIUM_EMOJI_ORDER_ID")
    return (
        f"{title}\n\n"
        f"Stars: {order['stars_count']}\n"
        f"Получатель: @{h(order['recipient_username'])}\n"
        f"Покупатель: {h(buyer_name)}\n"
        f"Оплачено: {format_usdt(str(order['total_amount'] or '0'))} USDT"
    )


def assigned(order: dict[str, object], manager_username: str | None) -> str:
    """Render assigned manager card."""

    manager = f"@{manager_username}" if manager_username else str(order["assigned_manager_id"])
    title = heading("◆", f"Заказ #{order['number']}", "PREMIUM_EMOJI_ORDER_ID")
    return (
        f"{title}\n\n"
        "Статус: взят в работу\n"
        f"Менеджер: {h(manager)}\n"
        f"Stars: {order['stars_count']}\n"
        f"Получатель: @{h(order['recipient_username'])}"
    )


def processing(order: dict[str, object]) -> str:
    """Render processing instructions."""

    title = heading("◆", f"Заказ #{order['number']}", "PREMIUM_EMOJI_ORDER_ID")
    return (
        f"{title}\n\n"
        f"Получатель: @{h(order['recipient_username'])}\n"
        f"Количество: {order['stars_count']} Stars\n\n"
        "Откройте профиль получателя и выполните отправку через официальный Telegram-клиент или Fragment."
    )


def confirm_done(order: dict[str, object]) -> str:
    """Render final confirmation."""

    return (
        f"{heading('✓', 'Подтвердите выполнение', 'PREMIUM_EMOJI_SUCCESS_ID')}\n\n"
        f"Получатель: @{h(order['recipient_username'])}\n"
        f"Количество: {order['stars_count']} Stars\n\n"
        "Отменить это действие сможет только администратор."
    )
