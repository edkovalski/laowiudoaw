from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    package_selection = State()
    player_id = State()
    order_confirmation = State()
    payment_proof = State()
    message_to_admin = State()

class AdminStates(StatesGroup):
    rejection_reason = State()
    reply_to_user = State()
