"""Payment presenters."""

from decimal import Decimal

from teleprism.app.core.money import format_usdt, money
from teleprism.app.utils.telegram import h, heading


def payment_caption(order: dict[str, object], payment: dict[str, object]) -> str:
    """Render payment QR caption."""

    title = heading("◆", f"Заказ #{order['number']}", "PREMIUM_EMOJI_ORDER_ID")
    return (
        f"{title}\n\n"
        "Отправьте ровно:\n\n"
        f"{format_usdt(str(payment['expected_amount']))} USDT\n\n"
        "Сеть: TRC20\n"
        f"Адрес:\n{h(payment['address_in'])}\n\n"
        "Не отправляйте токены другой сети.\n"
        "Комиссия вашей биржи не должна уменьшать сумму перевода."
    )


def detected(order: dict[str, object], payment: dict[str, object]) -> str:
    """Render detected payment status."""

    title = heading("◆", f"Заказ #{order['number']}", "PREMIUM_EMOJI_ORDER_ID")
    return (
        f"{title}\n\n"
        "Оплата обнаружена.\n"
        "Ожидаются подтверждения сети.\n\n"
        f"Получено: {format_usdt(str(payment['pending_amount']))} USDT"
    )


def partial(order: dict[str, object], payment: dict[str, object]) -> str:
    """Render partial payment status."""

    missing = money(str(payment["expected_amount"])) - money(str(payment["confirmed_amount"]))
    title = heading("◆", f"Заказ #{order['number']}", "PREMIUM_EMOJI_ORDER_ID")
    return (
        f"{title}\n\n"
        "Получена неполная оплата.\n\n"
        f"Получено: {format_usdt(str(payment['confirmed_amount']))} USDT\n"
        f"Не хватает: {format_usdt(max(missing, Decimal('0')))} USDT\n\n"
        "Отправьте недостающую сумму на тот же адрес."
    )


def paid(order: dict[str, object]) -> str:
    """Render confirmed payment status."""

    return (
        f"{heading('✓', 'Оплата подтверждена', 'PREMIUM_EMOJI_SUCCESS_ID')}\n\n"
        f"Заказ #{order['number']} передан менеджеру.\n\n"
        f"Получатель: @{h(order['recipient_username'])}\n"
        f"Количество: {order['stars_count']} Stars\n"
        "Ориентировочное выполнение: до 15 минут"
    )
