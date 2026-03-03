from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from database import db, User, Order, Product, AdminLog, UserMessage
from config import ADMIN_ID

class AdminService:
    @staticmethod
    async def log_admin_action(admin_id: int, action: str, details: str = None):
        """Логирование действий администратора"""
        async with await db.get_session() as session:
            log = AdminLog(
                admin_id=admin_id,
                action=action,
                details=details
            )
            session.add(log)
            await session.commit()
    
    @staticmethod
    async def get_user_statistics():
        """Получение статистики пользователей"""
        async with await db.get_session() as session:
            # Общее количество пользователей
            total_users = await session.scalar(select(func.count(User.user_id)))
            
            # Пользователи с заказами
            users_with_orders = await session.scalar(
                select(func.count(func.distinct(Order.user_id)))
            )
            
            # Статистика заказов по статусам
            order_stats = await session.execute(
                select(Order.status, func.count(Order.id))
                .group_by(Order.status)
            )
            order_stats = dict(order_stats.all())
            
            # Статистика за последние 7 дней
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_orders = await session.scalar(
                select(func.count(Order.id))
                .where(Order.created_at >= week_ago)
            )
            
            return {
                'total_users': total_users or 0,
                'users_with_orders': users_with_orders or 0,
                'order_stats': order_stats,
                'recent_orders': recent_orders or 0
            }
    
    @staticmethod
    async def get_all_products():
        """Получение всех продуктов"""
        async with await db.get_session() as session:
            result = await session.execute(
                select(Product).order_by(Product.category, Product.price)
            )
            return result.scalars().all()
    
    @staticmethod
    async def update_product_price(product_id: int, new_price: int):
        """Обновление цены продукта"""
        async with await db.get_session() as session:
            from sqlalchemy import update
            
            stmt = update(Product).where(Product.id == product_id).values(
                price=new_price,
                updated_at=datetime.utcnow()
            )
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    async def update_product_name(product_id: int, new_name: str):
        """Обновление названия продукта"""
        async with await db.get_session() as session:
            from sqlalchemy import update
            
            stmt = update(Product).where(Product.id == product_id).values(
                name=new_name,
                updated_at=datetime.utcnow()
            )
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    async def update_product_image(product_id: int, image_url: str):
        """Обновление изображения продукта"""
        async with await db.get_session() as session:
            from sqlalchemy import update
            
            stmt = update(Product).where(Product.id == product_id).values(
                image_url=image_url,
                updated_at=datetime.utcnow()
            )
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    async def search_users(query: str):
        """Поиск пользователей по ID или username"""
        async with await db.get_session() as session:
            try:
                # Попытка поиска по ID
                if query.isdigit():
                    user_id = int(query)
                    user = await session.get(User, user_id)
                    if user:
                        return [user]
                
                # Поиск по username
                users = await session.execute(
                    select(User).where(
                        or_(
                            User.username.ilike(f"%{query}%"),
                            User.first_name.ilike(f"%{query}%")
                        )
                    )
                )
                return users.scalars().all()
            except:
                return []
    
    @staticmethod
    async def send_message_to_user(sender_id: int, receiver_id: int, message_text: str, order_id: int = None):
        """Отправка сообщения пользователю"""
        async with await db.get_session() as session:
            message = UserMessage(
                sender_id=sender_id,
                receiver_id=receiver_id,
                message_text=message_text,
                order_id=order_id,
                is_from_admin=True
            )
            session.add(message)
            await session.commit()
    
    @staticmethod
    async def get_user_messages(user_id: int):
        """Получение сообщений пользователя"""
        async with await db.get_session() as session:
            messages = await session.execute(
                select(UserMessage)
                .where(
                    or_(
                        UserMessage.sender_id == user_id,
                        UserMessage.receiver_id == user_id
                    )
                )
                .order_by(UserMessage.created_at.desc())
            )
            return messages.scalars().all()
    
    @staticmethod
    async def get_orders_by_status(status: str = None, limit: int = 50):
        """Получение заказов с фильтрацией по статусу"""
        async with await db.get_session() as session:
            query = select(Order).order_by(Order.created_at.desc())
            
            if status:
                query = query.where(Order.status == status)
            
            query = query.limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()

admin_service = AdminService()
