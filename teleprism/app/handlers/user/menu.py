"""User menu handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from teleprism.app.keyboards.common import main_menu
from teleprism.app.presenters import home

router = Router(name="user_menu")


@router.callback_query(F.data == "home")
async def home_callback(callback: CallbackQuery) -> None:
    """Return to home screen."""

    if callback.message:
        await callback.message.edit_text(home.welcome(), reply_markup=main_menu())
    await callback.answer()


@router.message(Command("cancel"))
async def cancel(message: Message) -> None:
    """Cancel current interaction."""

    await message.answer(home.welcome(), reply_markup=main_menu())
