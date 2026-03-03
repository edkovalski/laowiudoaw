from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_admin_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Управление ценами", callback_data="admin_price_management")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_statistics")],
        [InlineKeyboardButton(text="💬 Сообщения пользователям", callback_data="admin_messaging")],
        [InlineKeyboardButton(text="📋 Заказы", callback_data="admin_orders")],
        [InlineKeyboardButton(text="❌ Выход", callback_data="admin_exit")]
    ])
    return keyboard

def get_price_management_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить цену", callback_data="admin_edit_price")],
        [InlineKeyboardButton(text="📝 Изменить название", callback_data="admin_edit_name")],
        [InlineKeyboardButton(text="🖼️ Изменить фото", callback_data="admin_edit_image")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])
    return keyboard

def get_products_keyboard(products):
    buttons = []
    for product in products:
        status = "✅" if product.is_active else "❌"
        text = f"{status} {product.name} - {product.price} сомони"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"select_product_{product.id}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_product_actions_keyboard(product_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Изменить цену", callback_data=f"change_price_{product_id}")],
        [InlineKeyboardButton(text="📝 Изменить название", callback_data=f"change_name_{product_id}")],
        [InlineKeyboardButton(text="🖼️ Изменить фото", callback_data=f"change_image_{product_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_price_management")]
    ])
    return keyboard

def get_statistics_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Общая статистика", callback_data="admin_general_stats")],
        [InlineKeyboardButton(text="📈 Статистика заказов", callback_data="admin_order_stats")],
        [InlineKeyboardButton(text="👥 Активные пользователи", callback_data="admin_active_users")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])
    return keyboard

def get_messaging_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Найти пользователя", callback_data="admin_search_user")],
        [InlineKeyboardButton(text="📨 История сообщений", callback_data="admin_message_history")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])
    return keyboard

def get_orders_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏳ В обработке", callback_data="admin_orders_pending")],
        [InlineKeyboardButton(text="✅ Выполненные", callback_data="admin_orders_completed")],
        [InlineKeyboardButton(text="❌ Отклоненные", callback_data="admin_orders_rejected")],
        [InlineKeyboardButton(text="📋 Все заказы", callback_data="admin_orders_all")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])
    return keyboard

def get_confirmation_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="admin_confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
    ])
    return keyboard

def get_back_keyboard(back_callback):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback)]
    ])
    return keyboard
