from aiogram.fsm.state import State, StatesGroup

class AdminPanelStates(StatesGroup):
    main_menu = State()
    price_management = State()
    statistics = State()
    user_messaging = State()
    edit_product = State()
    search_user = State()
    send_message = State()
    confirm_action = State()
