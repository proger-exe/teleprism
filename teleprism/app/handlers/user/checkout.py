"""User checkout handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from teleprism.app.config import Settings
from teleprism.app.container import Services
from teleprism.app.core.enums import SessionState
from teleprism.app.core.errors import ValidationError
from teleprism.app.keyboards import checkout as checkout_kb
from teleprism.app.presenters import checkout as checkout_view
from teleprism.app.utils.callbacks import parse_cb
from teleprism.app.utils.usernames import normalize_username

router = Router(name="user_checkout")


@router.message(Command("buy"))
@router.message(F.text == "✦ Купить Stars")
async def buy_start_message(message: Message, services: Services, user: dict[str, object]) -> None:
    """Start checkout from message."""

    has_username = bool(message.from_user and message.from_user.username)
    await services.sessions.set(int(user["id"]), None, {})
    await message.answer(
        checkout_view.recipient_start(has_username),
        reply_markup=checkout_kb.recipient_choice(has_username),
    )


@router.callback_query(F.data == "buy:start")
async def buy_start_callback(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Start checkout from callback."""

    has_username = bool(callback.from_user.username)
    await services.sessions.set(int(user["id"]), None, {})
    if callback.message:
        await callback.message.edit_text(
            checkout_view.recipient_start(has_username),
            reply_markup=checkout_kb.recipient_choice(has_username),
        )
    await callback.answer()


@router.callback_query(F.data == "buy:me")
async def buy_me(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Use buyer username as recipient."""

    if not callback.from_user.username:
        await callback.answer("У аккаунта нет username.", show_alert=True)
        return
    username = normalize_username(callback.from_user.username)
    await services.sessions.set(int(user["id"]), None, {"recipient_username": username})
    if callback.message:
        await callback.message.edit_text(
            checkout_view.recipient_confirm(username),
            reply_markup=checkout_kb.recipient_confirm(),
        )
    await callback.answer()


@router.callback_query(F.data == "buy:other")
async def buy_other(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Ask for another recipient username."""

    await services.sessions.set(int(user["id"]), SessionState.WAITING_RECIPIENT.value, {})
    if callback.message:
        await callback.message.edit_text("<b>✦ Покупка Stars</b>\n\nОтправьте username получателя.")
    await callback.answer()


@router.message()
async def state_text(message: Message, services: Services, user: dict[str, object], settings: Settings) -> None:
    """Handle text while waiting for session input."""

    session = await services.sessions.get(int(user["id"]))
    state = session["state"]
    if state == SessionState.WAITING_RECIPIENT.value:
        await handle_recipient_text(message, services, int(user["id"]))
        return
    if state == SessionState.WAITING_CUSTOM_STARS.value:
        await handle_custom_stars(message, services, int(user["id"]), settings)


async def handle_recipient_text(message: Message, services: Services, user_id: int) -> None:
    """Save manually entered username."""

    try:
        username = normalize_username(message.text or "")
    except ValidationError as error:
        await message.answer(str(error))
        return
    await services.sessions.set(user_id, None, {"recipient_username": username})
    await message.answer(checkout_view.recipient_confirm(username), reply_markup=checkout_kb.recipient_confirm())


@router.callback_query(F.data == "buy:stars")
async def buy_stars(callback: CallbackQuery, services: Services) -> None:
    """Show package selector."""

    packages = await services.package_repo.active()
    if callback.message:
        await callback.message.edit_text(
            checkout_view.package_choice(),
            reply_markup=checkout_kb.packages(packages),
        )
    await callback.answer()


@router.callback_query(F.data == "buy:custom")
async def buy_custom(callback: CallbackQuery, services: Services, user: dict[str, object], settings: Settings) -> None:
    """Ask for a custom Stars count."""

    await services.sessions.set(int(user["id"]), SessionState.WAITING_CUSTOM_STARS.value, {})
    if callback.message:
        await callback.message.edit_text(checkout_view.custom_stars(settings.min_stars, settings.max_stars))
    await callback.answer()


@router.callback_query(F.data.startswith("buy:pkg:"))
async def buy_package(callback: CallbackQuery, services: Services, user: dict[str, object]) -> None:
    """Create draft order for selected package."""

    parts = parse_cb(callback.data or "")
    await create_summary(callback, services, int(user["id"]), int(parts[2]))


async def handle_custom_stars(message: Message, services: Services, user_id: int, settings: Settings) -> None:
    """Create draft order for custom Stars count."""

    try:
        stars_count = int((message.text or "").replace(" ", ""))
        await services.pricing.validate_stars(stars_count)
    except (ValueError, ValidationError) as error:
        await message.answer(str(error) if str(error) else "Введите количество числом.")
        return
    session = await services.sessions.get(user_id)
    await services.sessions.set(user_id, None, session["data"])
    order = await create_order_from_session(services, user_id, stars_count)
    await message.answer(checkout_view.order_summary(order), reply_markup=checkout_kb.order_confirm(str(order["id"])))


async def create_summary(callback: CallbackQuery, services: Services, user_id: int, stars_count: int) -> None:
    """Create draft order and render summary."""

    order = await create_order_from_session(services, user_id, stars_count)
    if callback.message:
        await callback.message.edit_text(
            checkout_view.order_summary(order),
            reply_markup=checkout_kb.order_confirm(str(order["id"])),
        )
    await callback.answer()


async def create_order_from_session(services: Services, user_id: int, stars_count: int) -> dict[str, object]:
    """Create an order from persisted checkout session."""

    session = await services.sessions.get(user_id)
    recipient = session["data"].get("recipient_username")
    if not recipient:
        raise ValidationError("Не указан получатель.")
    return await services.checkout.create_order(user_id, str(recipient), stars_count)
