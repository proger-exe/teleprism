"""Admin presenters."""

from teleprism.app.utils.telegram import heading


def dashboard(stats: dict[str, object]) -> str:
    """Render admin dashboard."""

    return (
        f"{heading('◈', 'TelePrism Admin', 'PREMIUM_EMOJI_PRISM_ID')}\n\n"
        f"Заказов сегодня: {stats.get('today', 0)}\n"
        f"Оплачено: {stats.get('paid', 0)}\n"
        f"В очереди: {stats.get('queued', 0)}\n"
        f"В работе: {stats.get('processing', 0)}\n"
        f"Проблемных: {stats.get('issue', 0)}\n"
        f"Выручка: {stats.get('revenue', '0.00')} USDT"
    )
