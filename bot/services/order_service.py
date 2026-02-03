from database import db
from config import PAYMENT_DETAILS

class OrderService:
    @staticmethod
    async def create_user_if_not_exists(user_id: int, username: str = None, first_name: str = None):
        try:
            await db.create_user(user_id, username, first_name)
        except Exception:
            pass
    
    @staticmethod
    async def create_order(user_id: int, player_id: str, diamonds_amount: int, amount: int):
        return await db.create_order(user_id, player_id, diamonds_amount, amount)
    
    @staticmethod
    async def update_order_with_payment(order_id: int, payment_proof: str):
        async with await db.get_session() as session:
            from sqlalchemy import update
            from database import Order
            
            stmt = update(Order).where(Order.id == order_id).values(
                payment_proof=payment_proof
            )
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    async def approve_order(order_id: int):
        return await db.update_order_status(order_id, 'completed')
    
    @staticmethod
    async def reject_order(order_id: int, reason: str = None):
        return await db.update_order_status(order_id, 'rejected', reason)
    
    @staticmethod
    async def get_user_orders(user_id: int):
        return await db.get_user_orders(user_id)
    
    @staticmethod
    async def get_order_detail(order_id: int):
        return await db.get_order(order_id)
    
    @staticmethod
    def format_payment_message(amount: int, diamonds: int, player_id: str):
        return PAYMENT_DETAILS.replace("[сумма]", f"{amount}₽").replace("[реквизиты]", "1234 5678 9012 3456")
    
    @staticmethod
    def format_order_summary(diamonds: int, amount: int, player_id: str):
        return f"""
📋 **Детали заказа:**

💎 Алмазы: {diamonds}
💰 Сумма: {amount}₽
🎮 ID игрока: {player_id}

{PAYMENT_DETAILS.replace("[сумма]", f"{amount}₽").replace("[реквизиты]", "1234 5678 9012 3456")}
        """

order_service = OrderService()
