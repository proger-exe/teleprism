"""Admin manager role handlers."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from teleprism.app.container import Services
from teleprism.app.core.enums import UserRole
from teleprism.app.handlers.admin.dashboard import is_admin

router = Router(name="admin_managers")


@router.message(Command("managers"))
async def managers(message: Message, user: dict[str, object]) -> None:
    """Show manager role commands."""

    if not is_admin(user):
        await message.answer("Недостаточно прав.")
        return
    await message.answer(
        "<b>◈ Менеджеры</b>\n\n"
        "Добавить: /manager_add 123456789\n"
        "Выключить: /manager_off 123456789\n"
        "Сделать админом: /manager_admin 123456789"
    )


@router.message(Command("manager_add"))
async def manager_add(message: Message, services: Services, user: dict[str, object]) -> None:
    """Grant manager role."""

    await set_role_from_command(message, services, user, UserRole.MANAGER)


@router.message(Command("manager_off"))
async def manager_off(message: Message, services: Services, user: dict[str, object]) -> None:
    """Remove elevated role."""

    await set_role_from_command(message, services, user, UserRole.USER)


@router.message(Command("manager_admin"))
async def manager_admin(message: Message, services: Services, user: dict[str, object]) -> None:
    """Grant admin role."""

    await set_role_from_command(message, services, user, UserRole.ADMIN)


async def set_role_from_command(message: Message, services: Services, user: dict[str, object], role: UserRole) -> None:
    """Parse command and set target user role."""

    if not is_admin(user):
        await message.answer("Недостаточно прав.")
        return
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("Формат: /manager_add 123456789")
        return
    telegram_id = int(parts[1])
    await services.user_repo.set_role(telegram_id, role)
    await message.answer(f"<b>✓ Роль обновлена</b>\n\n{telegram_id} → {role.value}")
