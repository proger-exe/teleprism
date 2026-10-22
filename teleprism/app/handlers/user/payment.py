"""User payment handlers."""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from teleprism.app.container import Services
from teleprism.app.core.errors import PaymentProviderError
from teleprism.app.keyboards import checkout as checkout_kb
from teleprism.app.keyboards import payment as payment_kb
from teleprism.app.presenters import payment as payment_view
from teleprism.app.utils.callbacks import parse_cb
from teleprism.app.utils.qr import make_qr_file

router = Router(name="user_payment")


@router.callback_query(F.data.startswith("order:confirm:"))
async def confirm_order(callback: CallbackQuery, services: Services) -> None:
    """Create provider payment address and show QR."""

    order_id = parse_cb(callback.data or "")[2]
    await callback.answer("Создаю счёт...")
    try:
        order, payment = await services.checkout.confirm_order(order_id)
    except PaymentProviderError as error:
        await callback.answer("Счёт не создан. Ошибка показана в карточке.", show_alert=True)
        if callback.message:
            await callback.message.edit_text(
                "<b>⚠ Счёт не создан</b>\n\n"
                "Платёжный провайдер не вернул адрес.\n"
                f"Причина: {error}\n\n"
                "Можно повторить создание счёта после проверки настроек.",
                reply_markup=checkout_kb.order_confirm(order_id),
            )
        return
    if callback.message:
        await callback.message.delete()
        sent = await callback.message.answer_photo(
            make_qr_file(str(payment["address_in"])),
            caption=payment_view.payment_caption(order, payment),
            reply_markup=payment_kb.payment(order_id, str(payment["address_in"]), str(payment["expected_amount"])),
        )
        await services.order_repo.set_screen(order_id, sent.chat.id, sent.message_id)


@router.callback_query(F.data.startswith("pay:check:"))
async def check_payment(callback: CallbackQuery, services: Services) -> None:
    """Poll payment immediately when user asks."""

    order_id = parse_cb(callback.data or "")[2]
    payment = await services.payment_repo.by_order(order_id)
    order = await services.order_repo.get(order_id)
    if payment is None or order is None:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
    await services.payments.poll_payment(payment)
    refreshed_payment = await services.payment_repo.by_order(order_id)
    refreshed_order = await services.order_repo.get(order_id)
    if callback.message and refreshed_payment and refreshed_order:
        await callback.message.edit_caption(
            caption=payment_view.payment_caption(refreshed_order, refreshed_payment),
            reply_markup=payment_kb.payment(
                order_id,
                str(refreshed_payment["address_in"]),
                str(refreshed_payment["expected_amount"]),
            ),
        )
    await callback.answer("Статус обновлён.")
