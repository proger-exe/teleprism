"""Manager assignment handlers."""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from teleprism.app.container import Services
from teleprism.app.handlers.manager.queue import is_manager
from teleprism.app.keyboards import manager as manager_kb
from teleprism.app.presenters import manager as manager_view
from teleprism.app.utils.callbacks import parse_cb

router = Router(name="manager_assignment")


@router.callback_query(F.data.startswith("mgr:take:"))
async def take_order(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Atomically assign order to the current manager."""

    if not is_manager(user):
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    order_id = parse_cb(callback.data or "")[2]
    order = await services.managers.take_order(order_id, int(user["id"]))
    if order is None:
        await callback.answer("Заказ уже взят другим менеджером.", show_alert=True)
        return
    if callback.message:
        await callback.message.edit_text(
            manager_view.assigned(order, callback.from_user.username),
            reply_markup=manager_kb.assigned(order_id),
        )
    await callback.answer("Заказ назначен.")


@router.callback_query(F.data.startswith("mgr:return:"))
async def return_order(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Return order to queue."""

    if not is_manager(user):
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    order_id = parse_cb(callback.data or "")[2]
    order = await services.managers.return_to_queue(order_id, int(user["id"]))
    if callback.message:
        await callback.message.edit_text(manager_view.queue_card(order), reply_markup=manager_kb.queue_card(order_id))
    await callback.answer("Заказ возвращён.")
