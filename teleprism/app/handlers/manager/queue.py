"""Manager queue handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from teleprism.app.container import Services
from teleprism.app.core.enums import UserRole
from teleprism.app.keyboards import manager as manager_kb
from teleprism.app.presenters import manager as manager_view
from teleprism.app.utils.callbacks import parse_cb

router = Router(name="manager_queue")


def is_manager(user: dict[str, object]) -> bool:
    """Return whether user can access manager area."""

    return str(user.get("role")) in {
        UserRole.MANAGER.value,
        UserRole.ADMIN.value,
        UserRole.OWNER.value,
    }


@router.message(Command("manager", "queue", "my_orders"))
async def queue(message: Message, services: Services, user: dict[str, object]) -> None:
    """Show manager queue."""

    if not is_manager(user):
        await message.answer("Недостаточно прав.")
        return
    orders = await services.order_repo.queue()
    if not orders:
        await message.answer("<b>◆ Очередь</b>\n\nОплаченных заказов в очереди нет.")
        return
    for order in orders:
        await message.answer(manager_view.queue_card(order), reply_markup=manager_kb.queue_card(str(order["id"])))


@router.callback_query(F.data.startswith("mgr:open:"))
async def open_order(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Open manager order card."""

    if not is_manager(user):
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    order_id = parse_cb(callback.data or "")[2]
    order = await services.order_repo.get(order_id)
    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
    if callback.message:
        await callback.message.edit_text(manager_view.queue_card(order), reply_markup=manager_kb.queue_card(order_id))
    await callback.answer()
