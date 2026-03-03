from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from fsm.states import AdminStates
from database import db
from config import ADMIN_ID, BOT_TOKEN
from keyboards.inline_keyboards import get_reply_keyboard

router = Router()

@router.callback_query(F.data.startswith("approve_order_"))
async def approve_order_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    order = await db.update_order_status(order_id, 'completed')
    
    if order:
        bot = Bot(token=BOT_TOKEN)
        
        await bot.send_message(
            chat_id=order.user_id,
            text=f"✅ Ваш заказ #{order.id} исполнен! Алмазы уже на счету"
        )
        
        try:
            await callback.message.edit_text(
                f"✅ Заказ #{order_id} выполнен\n\n"
                f"Пользователь уведомлен об успешном пополнении."
            )
        except:
            await callback.message.answer(
                f"✅ Заказ #{order_id} выполнен\n\n"
                f"Пользователь уведомлен об успешном пополнении."
            )
        
        await callback.answer("Заказ выполнен")
    else:
        await callback.answer("❌ Заказ не найден", show_alert=True)

@router.callback_query(F.data.startswith("reject_order_"))
async def reject_order_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    
    await state.update_data(order_id=order_id)
    await state.set_state(AdminStates.rejection_reason)
    
    try:
        await callback.message.edit_text(
            f"📝 Введите причину отклонения заказа #{order_id}:"
        )
    except:
        await callback.message.answer(
            f"📝 Введите причину отклонения заказа #{order_id}:"
        )
    
    await callback.answer()

@router.message(AdminStates.rejection_reason)
async def rejection_reason_entered(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    order_id = data['order_id']
    reason = message.text
    
    order = await db.update_order_status(order_id, 'rejected', reason)
    
    if order:
        bot = Bot(token=BOT_TOKEN)
        
        await bot.send_message(
            chat_id=order.user_id,
            text=f"❌ Ваш заказ #{order.id} отклонен\n\n"
                 f"Причина: {reason}\n\n"
                 f"Если у вас есть вопросы, обратитесь в поддержку."
        )
        
        await message.answer(
            f"✅ Заказ #{order_id} отклонен\n\n"
            f"Причина отправлена пользователю: {reason}"
        )
    else:
        await message.answer("❌ Заказ не найден")
    
    await state.clear()

@router.callback_query(F.data.startswith("reply_user_"))
async def reply_user_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    
    await state.update_data(order_id=order_id, user_id=None)
    await state.set_state(AdminStates.reply_to_user)
    
    try:
        await callback.message.edit_text(
            f"💬 Введите ответ пользователю для заказа #{order_id}:"
        )
    except:
        await callback.message.answer(
            f"� Введите ответ пользователю для заказа #{order_id}:"
        )
    
    await callback.answer()

@router.message(AdminStates.reply_to_user)
async def reply_to_user_sent(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    order_id = data['order_id']
    reply_text = message.text
    
    order = await db.get_order(order_id)
    if order:
        bot = Bot(token=BOT_TOKEN)
        
        await bot.send_message(
            chat_id=order.user_id,
            text=f"💬 Сообщение от администратора по заказу #{order.id}:\n\n{reply_text}\n\nНажмите 'Ответить', чтобы ответить администратору:",
            reply_markup=get_reply_keyboard(order.id)
        )
        
        await message.answer(
            f"✅ Ответ отправлен пользователю по заказу #{order_id}"
        )
    else:
        await message.answer("❌ Заказ не найден")
    
    await state.clear()

@router.message(Command("admin"))
async def admin_command(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен")
        return
    
    # Перенаправляем на новую админ-панель
    from handlers.admin_panel import admin_command as admin_panel_command
    await admin_panel_command(message, None)
