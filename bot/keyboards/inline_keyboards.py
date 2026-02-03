from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import DIAMONDS_PACKAGES

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Сделать заказ", callback_data="make_order")],
        [InlineKeyboardButton(text="📜 История заказов", callback_data="order_history")],
        [InlineKeyboardButton(text="💬 Написать админу", callback_data="message_admin")]
    ])
    return keyboard

def get_packages_keyboard():
    buttons = []
    for package_key, package_data in DIAMONDS_PACKAGES.items():
        text = f"💎 {package_data['diamonds']} алмазов - {package_data['price']}₽"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"package_{package_key}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_confirmation_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order")]
    ])
    return keyboard

def get_admin_order_keyboard(order_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнено", callback_data=f"approve_order_{order_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_order_{order_id}")],
        [InlineKeyboardButton(text="💬 Ответить пользователю", callback_data=f"reply_user_{order_id}")]
    ])
    return keyboard

def get_order_history_keyboard(orders):
    buttons = []
    for order in orders:
        status_emoji = {"pending": "⏳", "completed": "✅", "rejected": "❌"}
        text = f"Заказ #{order.id} - {order.diamonds_amount}💎 - {status_emoji.get(order.status, '❓')}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"order_detail_{order.id}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_back_to_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_menu")]
    ])
    return keyboard
