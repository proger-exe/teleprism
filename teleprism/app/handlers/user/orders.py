"""User order history handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from teleprism.app.keyboards import user as user_kb
from teleprism.app.presenters import order as order_view

router = Router(name="user_orders")


@router.message(Command("orders"))
async def orders_message(message: Message) -> None:
    """Show user orders placeholder without listing history."""

    await message.answer(order_view.history(), reply_markup=user_kb.orders_menu())


@router.callback_query(F.data.startswith("orders:list:"))
async def orders_callback(callback: CallbackQuery) -> None:
    """Show user orders placeholder without listing history."""

    if callback.message:
        await callback.message.edit_text(order_view.history(), reply_markup=user_kb.orders_menu())
    await callback.answer()
