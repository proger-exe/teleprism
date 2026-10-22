"""Admin pricing handlers."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from teleprism.app.container import Services
from teleprism.app.core.money import format_usdt
from teleprism.app.handlers.admin.dashboard import is_admin

router = Router(name="admin_pricing")


@router.message(Command("packages"))
async def packages(message: Message, services: Services, user: dict[str, object]) -> None:
    """List active packages for admins."""

    if not is_admin(user):
        await message.answer("Недостаточно прав.")
        return
    rows = await services.package_repo.active()
    lines = ["<b>◈ Тарифы</b>", "", "Изменить: /package_set 500 9.80", "Выключить: /package_off 500", ""]
    lines.extend(f"{row['stars_count']} Stars — {format_usdt(str(row['price_usdt']))} USDT" for row in rows)
    await message.answer("\n".join(lines))


@router.message(Command("package_set"))
async def package_set(message: Message, services: Services, user: dict[str, object]) -> None:
    """Create or update a Stars package."""

    if not is_admin(user):
        await message.answer("Недостаточно прав.")
        return
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("Формат: /package_set 500 9.80")
        return
    stars_count = int(parts[1])
    price = parts[2]
    await services.pricing.validate_stars(stars_count)
    await services.package_repo.upsert(stars_count, price, is_active=True)
    await message.answer(f"<b>✓ Тариф сохранён</b>\n\n{stars_count} Stars — {format_usdt(price)} USDT")


@router.message(Command("package_off"))
async def package_off(message: Message, services: Services, user: dict[str, object]) -> None:
    """Disable a Stars package."""

    if not is_admin(user):
        await message.answer("Недостаточно прав.")
        return
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("Формат: /package_off 500")
        return
    await services.package_repo.upsert(int(parts[1]), "0", is_active=False)
    await message.answer(f"<b>✓ Тариф выключен</b>\n\n{parts[1]} Stars")
