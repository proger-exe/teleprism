"""Manager execution handlers."""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from teleprism.app.container import Services
from teleprism.app.core.enums import OrderStatus
from teleprism.app.handlers.manager.queue import is_manager
from teleprism.app.keyboards import manager as manager_kb
from teleprism.app.presenters import manager as manager_view
from teleprism.app.utils.callbacks import parse_cb

router = Router(name="manager_execution")


@router.callback_query(F.data.startswith("mgr:start:"))
async def start_processing(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Start order processing."""

    if not is_manager(user):
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    order_id = parse_cb(callback.data or "")[2]
    order = await services.managers.start_processing(order_id, int(user["id"]))
    if callback.message:
        await callback.message.edit_text(
            manager_view.processing(order),
            reply_markup=manager_kb.processing(order_id, str(order["recipient_username"])),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("mgr:done:"))
async def done_prompt(callback: CallbackQuery, services: Services) -> None:
    """Ask manager to confirm completion."""

    order_id = parse_cb(callback.data or "")[2]
    order = await services.order_repo.get(order_id)
    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
    if callback.message:
        await callback.message.edit_text(
            manager_view.confirm_done(order), reply_markup=manager_kb.confirm_done(order_id)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("mgr:confirm_done:"))
async def confirm_done(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Complete order after manager confirmation."""

    if not is_manager(user):
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    order_id = parse_cb(callback.data or "")[2]
    order = await services.managers.complete(order_id, int(user["id"]))
    buyer = await services.user_repo.get_by_id(int(order["buyer_id"]))
    if buyer:
        await services.notifications.message(
            int(buyer["telegram_id"]),
            (
                f"<b>✓ Заказ выполнен</b>\n\nЗаказ: #{order['number']}\n"
                f"Получатель: @{order['recipient_username']}\n"
                f"Отправлено: {order['stars_count']} Stars"
            ),
        )
    if callback.message:
        await callback.message.edit_text(f"<b>✓ Заказ #{order['number']} выполнен.</b>")
    await callback.answer("Выполнено.")


@router.callback_query(F.data.startswith("mgr:issue:"))
async def issue(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Mark manager issue."""

    if not is_manager(user):
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    order_id = parse_cb(callback.data or "")[2]
    await services.orders.transition(order_id, OrderStatus.ISSUE, actor_user_id=int(user["id"]))
    if callback.message:
        await callback.message.edit_text(
            "<b>⚠ Заказ помечен проблемным.</b>\n\nАдминистратор получил событие в журнале."
        )
    await callback.answer()
