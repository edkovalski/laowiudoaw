from database import db, Order
from config import PAYMENT_DETAILS

class OrderService:
    @staticmethod
    async def create_user_if_not_exists(user_id: int, username: str = None, first_name: str = None):
        try:
            await db.create_user(user_id, username, first_name)
        except Exception:
            pass
    
    @staticmethod
    async def create_order(user_id: int, player_id: str, diamonds_amount: int, amount: int, category: str = 'diamonds', package_name: str = None):
        # Находим продукт в БД
        async with await db.get_session() as session:
            from sqlalchemy import select
            from database import Product
            
            # Ищем продукт по категории и package_key
            package_key = None
            if category == 'diamonds':
                for key in ['100', '310', '520', '1060', '2180']:
                    if package_name and str(key) in package_name:
                        package_key = key
                        break
            elif category == 'vouchers':
                package_key = 'weekly' if 'неделю' in package_name else 'monthly'
            elif category == 'evo':
                if '3 дня' in package_name:
                    package_key = '3days'
                elif '7 дней' in package_name:
                    package_key = '7days'
                else:
                    package_key = '30days'
            
            result = await session.execute(
                select(Product).where(
                    Product.category == category,
                    Product.package_key == package_key
                )
            )
            product = result.scalar_one_or_none()
            
            if not product:
                # Fallback - создаем заказ без product_id
                return await db.create_order(user_id, player_id, diamonds_amount, amount, category, package_name)
            
            # Создаем заказ с product_id
            order = Order(
                user_id=user_id,
                product_id=product.id,
                player_id=player_id,
                diamonds_amount=diamonds_amount,
                amount=amount,
                category=category,
                package_name=package_name
            )
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order
    
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
        return PAYMENT_DETAILS.replace("[сумма]", f"{amount} сомони")
    
    @staticmethod
    def format_order_summary(package_name: str, amount: int, player_id: str, category: str = 'diamonds'):
        if category == 'diamonds':
            emoji = "💎"
        elif category == 'vouchers':
            emoji = "🎫"
        elif category == 'evo':
            emoji = "🎮"
        else:
            emoji = "📦"
            
        return f"""📋 Детали заказа:

{emoji} {package_name}
💰 Сумма: {amount} сомони
🎮 ID игрока: {player_id}

{PAYMENT_DETAILS.replace("[сумма]", f"{amount} сомони")}
        """

order_service = OrderService()
