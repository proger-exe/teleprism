"""User start/help handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from teleprism.app.container import Services
from teleprism.app.core.money import format_usdt
from teleprism.app.keyboards.common import main_menu
from teleprism.app.presenters import home

router = Router(name="user_start")


@router.message(Command("start", "help"))
async def start(message: Message, services: Services) -> None:
    """Create user and show the main menu."""

    user = await services.users.touch(message.from_user)
    await services.sessions.clear(int(user["id"]))
    await message.answer(home.welcome(), reply_markup=main_menu())


@router.message(lambda message: message.text == "Информация")
async def info(message: Message) -> None:
    """Show project information."""

    await message.answer(home.info(), reply_markup=main_menu())


@router.callback_query(F.data == "info")
async def info_callback(callback: CallbackQuery) -> None:
    """Show project information from inline menu."""

    if callback.message:
        await callback.message.edit_text(home.info(), reply_markup=main_menu())
    await callback.answer()


@router.message(Command("price"))
@router.message(lambda message: message.text == "◈ Прайс")
async def price(message: Message, services: Services) -> None:
    """Show active Stars packages."""

    await message.answer(await price_text(services), reply_markup=main_menu())


@router.callback_query(F.data == "price")
async def price_callback(callback: CallbackQuery, services: Services) -> None:
    """Show active Stars packages from inline menu."""

    if callback.message:
        await callback.message.edit_text(await price_text(services), reply_markup=main_menu())
    await callback.answer()


async def price_text(services: Services) -> str:
    """Render active Stars packages."""

    packages = await services.package_repo.active()
    if not packages:
        return "<b>◈ Прайс</b>\n\nАктивных тарифов пока нет."
    lines = ["<b>◈ Прайс</b>"]
    for package in packages:
        lines.append(f"{package['stars_count']} Stars — {format_usdt(str(package['price_usdt']))} USDT")
    return "\n".join(lines)
