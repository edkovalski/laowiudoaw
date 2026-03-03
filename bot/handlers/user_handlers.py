import re
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from fsm.states import OrderStates
from keyboards.inline_keyboards import get_start_keyboard, get_diamonds_keyboard, get_vouchers_keyboard, get_evo_keyboard, get_confirmation_keyboard, get_order_history_keyboard, get_back_to_menu_keyboard
from services.order_service import order_service
from config import DIAMONDS_PACKAGES, VOUCHER_PACKAGES, EVO_PACKAGES, ADMIN_ID
from database import db

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await order_service.create_user_if_not_exists(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name
    )
    
    # Проверяем, является ли пользователь админом
    if message.from_user.id == ADMIN_ID:
        from handlers.admin_panel import admin_command
        await admin_command(message, state)
        return
    
    await message.answer(
        "👋 Добро пожаловать в бот пополнения алмазов Free Fire!\n\n"
        "Здесь вы можете быстро и безопасно пополнить баланс алмазов в игре.\n\n"
        "Выберите действие ниже:",
        reply_markup=get_start_keyboard()
    )

@router.callback_query(F.data.startswith("category_"))
async def category_selected_callback(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    
    await state.update_data(category=category)
    
    if category == "diamonds":
        await callback.message.edit_text(
            "💎 Выберите пакет алмазов:",
            reply_markup=get_diamonds_keyboard()
        )
    elif category == "vouchers":
        await callback.message.edit_text(
            "🎫 Выберите ваучер:",
            reply_markup=get_vouchers_keyboard()
        )
    elif category == "evo":
        await callback.message.edit_text(
            "🎮 Выберите EVO пропуск:",
            reply_markup=get_evo_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("package_"))
async def package_selected_callback(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    category = parts[1]
    package_key = parts[2]
    
    if category == "diamonds":
        package_data = DIAMONDS_PACKAGES[package_key]
    elif category == "vouchers":
        package_data = VOUCHER_PACKAGES[package_key]
    elif category == "evo":
        package_data = EVO_PACKAGES[package_key]
    else:
        return
    
    await state.update_data(
        category=category,
        package_key=package_key,
        package_name=package_data['name'],
        diamonds=package_data['diamonds'],
        amount=package_data['price']
    )
    
    await state.set_state(OrderStates.player_id)
    await callback.message.edit_text(
        f"Вы выбрали: {package_data['name']} за {package_data['price']} сомони\n\n"
        "🎮 Введите ваш ID игрока Free Fire (8-12 цифр):"
    )
    await callback.answer()

@router.message(OrderStates.player_id)
async def player_id_entered(message: Message, state: FSMContext):
    player_id = message.text.strip()
    
    if not re.match(r'^\d{8,12}$', player_id):
        await message.answer(
            "❌ Неверный формат ID! ID должен содержать от 8 до 12 цифр.\n"
            "Попробуйте еще раз:"
        )
        return
    
    data = await state.get_data()
    package_name = data['package_name']
    amount = data['amount']
    category = data['category']
    
    # Сохраняем все данные включая player_id
    await state.update_data(
        player_id=player_id,
        package_name=package_name,
        amount=amount,
        category=category
    )
    
    # Проверяем, что данные сохранились
    updated_data = await state.get_data()
    print(f"DEBUG: Updated state data: {updated_data}")  # Отладочная информация
    
    summary = order_service.format_order_summary(package_name, amount, player_id, category)
    
    await state.set_state(OrderStates.order_confirmation)
    await message.answer(
        f"{summary}\n\n"
        "Проверьте данные и подтвердите заказ:",
        reply_markup=get_confirmation_keyboard()
    )

@router.callback_query(F.data == "confirm_order")
async def confirm_order_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(f"DEBUG: State data: {data}")  # Отладочная информация
    
    if 'player_id' not in data:
        await callback.answer("❌ Ошибка: ID игрока не найден. Попробуйте заново.", show_alert=True)
        await state.clear()
        await callback.message.edit_text(
            "❌ Произошла ошибка. Начните заново с команды /start",
            reply_markup=get_start_keyboard()
        )
        return
    
    order = await order_service.create_order(
        user_id=callback.from_user.id,
        player_id=data['player_id'],
        diamonds_amount=data['diamonds'],
        amount=data['amount'],
        category=data['category'],
        package_name=data['package_name']
    )
    
    await state.update_data(order_id=order.id)
    await state.set_state(OrderStates.payment_proof)
    
    await callback.message.edit_text(
        f"✅ Заказ #{order.id} создан!\n\n"
        f"💰 Сумма к оплате: {data['amount']} сомони\n"
        f"🎮 ID игрока: {data['player_id']}\n\n"
        "📸 Отправьте скриншот оплаты для подтверждения заказа:"
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_order")
async def cancel_order_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Заказ отменен.\n\n"
        "Чтобы создать новый заказ, нажмите /start",
        reply_markup=get_start_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "order_history")
async def order_history_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    orders = await order_service.get_user_orders(callback.from_user.id)
    
    if not orders:
        await callback.message.edit_text(
            "📜 У вас пока нет заказов\n\n"
            "Сделайте первый заказ, нажав кнопку ниже:",
            reply_markup=get_start_keyboard()
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        f"📜 **Ваши заказы ({len(orders)}):**\n\n"
        "Выберите заказ для просмотра деталей:",
        reply_markup=get_order_history_keyboard(orders)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("order_detail_"))
async def order_detail_callback(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[2])
    order = await order_service.get_order_detail(order_id)
    
    if not order or order.user_id != callback.from_user.id:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return
    
    status_emoji = {"pending": "⏳", "completed": "✅", "rejected": "❌"}
    status_text = {"pending": "В обработке", "completed": "Выполнен", "rejected": "Отклонен"}
    
    detail_text = f"""📋 Заказ #{order.id}

{order.package_name}
💰 Сумма: {order.amount} сомони
🎮 ID игрока: {order.player_id}
📅 Дата: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}
📊 Статус: {status_emoji.get(order.status, '❓')} {status_text.get(order.status, 'Неизвестно')}"""
    
    if order.status == 'rejected' and order.rejection_reason:
        detail_text += f"\n\n📝 Причина отклонения: {order.rejection_reason}"
    
    detail_text += "\n\n🔙 В главное меню"
    
    await callback.message.edit_text(
        detail_text,
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "message_admin")
async def message_admin_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.message_to_admin)
    await callback.message.edit_text(
        "💬 Напишите сообщение администратору:\n\n"
        "Вы можете задать вопрос или сообщить о проблеме.",
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()

@router.message(OrderStates.message_to_admin)
async def admin_message_sent(message: Message, state: FSMContext):
    user_text = message.text
    
    await message.answer(
        "✅ Ваше сообщение отправлено администратору!\n\n"
        "Мы постараемся ответить как можно скорее.",
        reply_markup=get_start_keyboard()
    )
    
    await notify_admin_about_user_message(message.from_user, user_text)
    await state.clear()

@router.callback_query(F.data.startswith("reply_to_admin_"))
async def reply_to_admin_callback(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[3])
    
    await state.update_data(order_id=order_id)
    await state.set_state(OrderStates.reply_to_admin)
    
    await callback.message.edit_text(
        "� Напишите ответ администратору:\n\n"
        "Вы можете ответить на сообщение по вашему заказу.",
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()

@router.message(OrderStates.reply_to_admin)
async def reply_to_admin_sent(message: Message, state: FSMContext):
    reply_text = message.text
    data = await state.get_data()
    order_id = data.get('order_id', 0)
    
    await message.answer(
        "✅ Ваш ответ отправлен администратору!\n\n"
        "Мы постараемся ответить как можно скорее.",
        reply_markup=get_start_keyboard()
    )
    
    await notify_admin_about_user_reply(message.from_user, reply_text, order_id)
    await state.clear()

async def notify_admin_about_user_reply(user, reply_text: str, order_id: int):
    from aiogram import Bot
    from config import BOT_TOKEN
    
    bot = Bot(token=BOT_TOKEN)
    
    admin_message = (
        f"💬 **Ответ пользователя на сообщение по заказу #{order_id}**\n\n"
        f"👤 ID: {user.id}\n"
        f"👤 Имя: {user.first_name}"
    )
    
    if user.username:
        admin_message += f" (@{user.username})"
    
    admin_message += f"\n\n💬 Ответ:\n{reply_text}"
    
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "👋 Добро пожаловать в бот пополнения алмазов Free Fire!\n\n"
        "Здесь вы можете быстро и безопасно пополнить баланс алмазов в игре.\n\n"
        "Выберите действие ниже:",
        reply_markup=get_start_keyboard()
    )
    await callback.answer()

@router.message(OrderStates.payment_proof, F.photo)
async def payment_proof_received(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data['order_id']
    
    file_id = message.photo[-1].file_id
    await order_service.update_order_with_payment(order_id, file_id)
    
    await message.answer(
        "✅ Спасибо! Ваш скриншот получен.\n\n"
        "📋 Ваш заказ находится в обработке.\n"
        "Вы получите уведомление о статусе заказа в ближайшее время.\n\n"
        "Для создания нового заказа нажмите /start"
    )
    
    await state.clear()
    
    await notify_admin_about_new_order(order_id)

@router.message(OrderStates.payment_proof)
async def invalid_payment_proof(message: Message, state: FSMContext):
    await message.answer(
        "❌ Пожалуйста, отправьте скриншот оплаты (фото).\n"
        "Текстовые сообщения не принимаются."
    )

async def notify_admin_about_new_order(order_id: int):
    order = await db.get_order(order_id)
    if not order:
        return
    
    from aiogram import Bot
    from config import BOT_TOKEN
    
    bot = Bot(token=BOT_TOKEN)
    
    message_text = (
        f"🆕 Новый заказ #{order.id}\n\n"
        f"👤 Пользователь: {order.user_id}\n"
        f"🎮 ID игрока: {order.player_id}\n"
        f"📦 Товар: {order.package_name}\n"
        f"💰 Сумма: {order.amount} сомони\n"
        f"📅 Дата: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    from keyboards.inline_keyboards import get_admin_order_keyboard
    
    if order.payment_proof:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=order.payment_proof,
            caption=message_text,
            reply_markup=get_admin_order_keyboard(order.id)
        )
    else:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=message_text,
            reply_markup=get_admin_order_keyboard(order.id)
        )

async def notify_admin_about_user_message(user, message_text: str):
    from aiogram import Bot
    from config import BOT_TOKEN
    
    bot = Bot(token=BOT_TOKEN)
    
    admin_message = (
        f"💬 Новое сообщение от пользователя\n\n"
        f"👤 ID: {user.id}\n"
        f"👤 Имя: {user.first_name}"
    )
    
    if user.username:
        admin_message += f" (@{user.username})"
    
    admin_message += f"\n\n💬 Сообщение:\n{message_text}"
    
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message
    )
