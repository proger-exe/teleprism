"""Admin dashboard handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from teleprism.app.container import Services
from teleprism.app.core.enums import UserRole
from teleprism.app.keyboards.admin import admin_menu
from teleprism.app.presenters.admin import dashboard

router = Router(name="admin_dashboard")


def is_admin(user: dict[str, object]) -> bool:
    """Return whether user can access admin area."""

    return str(user.get("role")) in {UserRole.ADMIN.value, UserRole.OWNER.value}


@router.message(Command("admin"))
async def admin(message: Message, services: Services, user: dict[str, object]) -> None:
    """Show admin dashboard."""

    if not is_admin(user):
        await message.answer("Недостаточно прав.")
        return
    await message.answer(dashboard(await stats(services)), reply_markup=admin_menu())


@router.callback_query(F.data.startswith("admin:"))
async def admin_callback(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Show placeholder admin section."""

    if not is_admin(user):
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    section = (callback.data or "").split(":", maxsplit=1)[1]
    if callback.message:
        await callback.message.edit_text(
            f"<b>◈ TelePrism Admin</b>\n\nРаздел: {section}\n\nБазовое управление доступно через сервисы и SQLite.",
            reply_markup=admin_menu(),
        )
    await callback.answer()


async def stats(services: Services) -> dict[str, object]:
    """Compute small admin stats."""

    rows = await services.order_repo.queue(limit=1000)
    return {
        "queued": len(rows),
        "today": 0,
        "paid": 0,
        "processing": 0,
        "issue": 0,
        "revenue": "0.00",
    }
