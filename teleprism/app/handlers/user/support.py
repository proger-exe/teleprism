"""User support handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from teleprism.app.container import Services

router = Router(name="user_support")


@router.message(Command("support"))
@router.message(F.text == "Поддержка")
async def support(message: Message, services: Services, user: dict[str, object]) -> None:
    """Create a generic support ticket."""

    ticket_id = await services.support.open_ticket(int(user["id"]), "GENERAL")
    await message.answer(f"<b>⚠ Поддержка</b>\n\nОбращение #{ticket_id} создано. Менеджер ответит в этом чате.")


@router.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Create support ticket from inline menu."""

    ticket_id = await services.support.open_ticket(int(user["id"]), "GENERAL")
    if callback.message:
        await callback.message.edit_text(
            f"<b>⚠ Поддержка</b>\n\nОбращение #{ticket_id} создано. Менеджер ответит в этом чате."
        )
    await callback.answer()
