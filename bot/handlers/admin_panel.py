from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from fsm.admin_states import AdminPanelStates
from keyboards.admin_keyboards import (
    get_admin_main_keyboard, get_price_management_keyboard, 
    get_products_keyboard, get_product_actions_keyboard,
    get_statistics_keyboard, get_messaging_keyboard,
    get_orders_keyboard, get_confirmation_keyboard, get_back_keyboard
)
from services.admin_service import admin_service
from config import ADMIN_ID, BOT_TOKEN

router = Router()

@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен")
        return
    
    await state.clear()
    await state.set_state(AdminPanelStates.main_menu)
    
    await message.answer(
        "🛠️ **Админ панель**\n\n"
        "Выберите действие:",
        reply_markup=get_admin_main_keyboard()
    )

@router.callback_query(F.data == "admin_main_menu")
async def admin_main_menu_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await state.set_state(AdminPanelStates.main_menu)
    await callback.message.edit_text(
        "🛠️ **Админ панель**\n\n"
        "Выберите действие:",
        reply_markup=get_admin_main_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin_price_management")
async def admin_price_management_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await state.set_state(AdminPanelStates.price_management)
    
    products = await admin_service.get_all_products()
    await callback.message.edit_text(
        "💰 **Управление ценами**\n\n"
        "Выберите продукт для редактирования:",
        reply_markup=get_products_keyboard(products)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("select_product_"))
async def select_product_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[2])
    
    await state.update_data(product_id=product_id)
    await callback.message.edit_text(
        f"📦 **Управление продуктом #{product_id}**\n\n"
        "Выберите действие:",
        reply_markup=get_product_actions_keyboard(product_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("change_price_"))
async def change_price_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id, action="change_price")
    await state.set_state(AdminPanelStates.edit_product)
    
    await callback.message.edit_text(
        "💰 **Изменение цены**\n\n"
        "Введите новую цену (в сомони):"
    )
    await callback.answer()

@router.message(AdminPanelStates.edit_product)
async def edit_product_message(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    action = data.get('action')
    product_id = data.get('product_id')
    
    if not product_id or not action:
        await message.answer("❌ Ошибка: данные не найдены")
        await state.clear()
        return
    
    try:
        if action == "change_price":
            new_price = float(message.text)
            await admin_service.update_product_price(product_id, int(new_price))
            await admin_service.log_admin_action(
                message.from_user.id, 
                "price_change", 
                f"Product #{product_id} price changed to {new_price}"
            )
            await message.answer(
                f"✅ Цена успешно изменена на {new_price} сомони",
                reply_markup=get_back_keyboard("admin_price_management")
            )
        
        elif action == "change_name":
            new_name = message.text
            await admin_service.update_product_name(product_id, new_name)
            await admin_service.log_admin_action(
                message.from_user.id,
                "name_change",
                f"Product #{product_id} name changed to {new_name}"
            )
            await message.answer(
                f"✅ Название успешно изменено на {new_name}",
                reply_markup=get_back_keyboard("admin_price_management")
            )
        
        await state.set_state(AdminPanelStates.price_management)
        
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число.")

@router.callback_query(F.data.startswith("change_name_"))
async def change_name_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id, action="change_name")
    await state.set_state(AdminPanelStates.edit_product)
    
    await callback.message.edit_text(
        "📝 **Изменение названия**\n\n"
        "Введите новое название:"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_statistics")
async def admin_statistics_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await state.set_state(AdminPanelStates.statistics)
    
    stats = await admin_service.get_user_statistics()
    
    text = f"""📊 **Статистика**

👥 Всего пользователей: {stats['total_users']}
🛒 Пользователей с заказами: {stats['users_with_orders']}
📦 Заказов за 7 дней: {stats['recent_orders']}

📈 Статус заказов:"""
    
    for status, count in stats['order_stats'].items():
        emoji = {"pending": "⏳", "completed": "✅", "rejected": "❌"}.get(status, "❓")
        text += f"\n{emoji} {status}: {count}"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_statistics_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin_messaging")
async def admin_messaging_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await state.set_state(AdminPanelStates.user_messaging)
    await callback.message.edit_text(
        "💬 **Сообщения пользователям**\n\n"
        "Выберите действие:",
        reply_markup=get_messaging_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin_search_user")
async def admin_search_user_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await state.set_state(AdminPanelStates.search_user)
    await callback.message.edit_text(
        "🔍 **Поиск пользователя**\n\n"
        "Введите ID пользователя или username:",
        reply_markup=get_back_keyboard("admin_messaging")
    )
    await callback.answer()

@router.message(AdminPanelStates.search_user)
async def search_user_message(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    query = message.text.strip()
    users = await admin_service.search_users(query)
    
    if not users:
        await message.answer(
            "❌ Пользователи не найдены\n\n"
            "Попробуйте другой запрос:",
            reply_markup=get_back_keyboard("admin_messaging")
        )
        return
    
    text = "👥 **Найденные пользователи:**\n\n"
    for user in users:
        username = f"(@{user.username})" if user.username else ""
        text += f"👤 ID: {user.user_id} {username}\n"
        text += f"📝 Имя: {user.first_name}\n"
        text += f"📅 Регистрация: {user.created_at.strftime('%Y-%m-%d')}\n"
        text += f"🛒 Заказов: {user.total_orders}\n\n"
    
    await message.answer(text, reply_markup=get_back_keyboard("admin_messaging"))
    await state.set_state(AdminPanelStates.user_messaging)

@router.callback_query(F.data == "admin_exit")
async def admin_exit_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await state.clear()
    await callback.message.edit_text("👋 Выход из админ панели")
    await callback.answer()
