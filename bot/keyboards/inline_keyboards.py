from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import DIAMONDS_PACKAGES, VOUCHER_PACKAGES, EVO_PACKAGES

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="� Алмазы", callback_data="category_diamonds")],
        [InlineKeyboardButton(text="🎫 Ваучеры", callback_data="category_vouchers")],
        [InlineKeyboardButton(text="🎮 EVO пропуски", callback_data="category_evo")],
        [InlineKeyboardButton(text="📜 История заказов", callback_data="order_history")],
        [InlineKeyboardButton(text="💬 Написать админу", callback_data="message_admin")]
    ])
    return keyboard

def get_diamonds_keyboard():
    buttons = []
    for package_key, package_data in DIAMONDS_PACKAGES.items():
        text = f"💎 {package_data['name']} - {package_data['price']} сомони"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"package_diamonds_{package_key}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_vouchers_keyboard():
    buttons = []
    for package_key, package_data in VOUCHER_PACKAGES.items():
        text = f"🎫 {package_data['name']} - {package_data['price']} сомони"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"package_vouchers_{package_key}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_evo_keyboard():
    buttons = []
    for package_key, package_data in EVO_PACKAGES.items():
        text = f"🎮 {package_data['name']} - {package_data['price']} сомони"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"package_evo_{package_key}")])
    
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

def get_reply_keyboard(order_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"reply_to_admin_{order_id}")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_menu")]
    ])
    return keyboard
