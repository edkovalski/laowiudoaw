import asyncio
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, BigInteger, Boolean, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from config import DATABASE_PATH

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(50))
    first_name = Column(String(100))
    last_activity = Column(DateTime, default=datetime.utcnow)
    total_orders = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="user")

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(20), nullable=False)
    package_key = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    diamonds = Column(Integer, default=0)
    price = Column(Integer, nullable=False)
    image_url = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = relationship("Order", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    player_id = Column(String(12))
    diamonds_amount = Column(Integer)
    amount = Column(Integer)
    category = Column(String(20), default='diamonds')
    package_name = Column(String(100))
    status = Column(String(20), default='pending')
    payment_proof = Column(Text)
    rejection_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")

class AdminLog(Base):
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserMessage(Base):
    __tablename__ = 'user_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger, nullable=False)
    receiver_id = Column(BigInteger, nullable=False)
    message_text = Column(Text, nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'))
    is_from_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self):
        self.engine = create_async_engine(f'sqlite+aiosqlite:///{DATABASE_PATH}')
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
    
    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # Инициализация продуктов из config
            await self._init_products()
    
    async def _init_products(self):
        """Инициализация продуктов из конфигурации"""
        from config import DIAMONDS_PACKAGES, VOUCHER_PACKAGES, EVO_PACKAGES
        
        async with self.async_session() as session:
            from sqlalchemy import select
            
            # Проверяем, есть ли уже продукты
            result = await session.execute(select(Product))
            if result.scalar():
                return
            
            # Добавляем алмазы
            for key, data in DIAMONDS_PACKAGES.items():
                product = Product(
                    category='diamonds',
                    package_key=key,
                    name=data['name'],
                    diamonds=data['diamonds'],
                    price=int(data['price'])
                )
                session.add(product)
            
            # Добавляем ваучеры
            for key, data in VOUCHER_PACKAGES.items():
                product = Product(
                    category='vouchers',
                    package_key=key,
                    name=data['name'],
                    diamonds=data['diamonds'],
                    price=int(data['price'])
                )
                session.add(product)
            
            # Добавляем EVO пропуски
            for key, data in EVO_PACKAGES.items():
                product = Product(
                    category='evo',
                    package_key=key,
                    name=data['name'],
                    diamonds=data['diamonds'],
                    price=int(data['price'])
                )
                session.add(product)
            
            await session.commit()
    
    async def get_session(self):
        return self.async_session()
    
    async def create_user(self, user_id: int, username: str = None, first_name: str = None):
        async with self.async_session() as session:
            user = User(user_id=user_id, username=username, first_name=first_name)
            session.add(user)
            await session.commit()
    
    async def create_order(self, user_id: int, player_id: str, diamonds_amount: int, amount: int, category: str = 'diamonds', package_name: str = None, product_id: int = None):
        async with self.async_session() as session:
            order = Order(
                user_id=user_id,
                product_id=product_id,
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
    
    async def update_order_status(self, order_id: int, status: str, rejection_reason: str = None):
        async with self.async_session() as session:
            from sqlalchemy import update
            stmt = update(Order).where(Order.id == order_id).values(
                status=status,
                rejection_reason=rejection_reason,
                updated_at=datetime.utcnow()
            )
            await session.execute(stmt)
            await session.commit()
            
            order = await session.get(Order, order_id)
            return order
    
    async def update_order_with_payment(self, order_id: int, payment_proof: str):
        async with self.async_session() as session:
            from sqlalchemy import update
            stmt = update(Order).where(Order.id == order_id).values(
                payment_proof=payment_proof
            )
            await session.execute(stmt)
            await session.commit()
    
    async def get_order(self, order_id: int):
        async with self.async_session() as session:
            return await session.get(Order, order_id)
    
    async def get_user_orders(self, user_id: int):
        async with self.async_session() as session:
            from sqlalchemy import select
            stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def get_pending_orders(self):
        async with self.async_session() as session:
            from sqlalchemy import select
            stmt = select(Order).where(Order.status == 'pending').order_by(Order.created_at.desc())
            result = await session.execute(stmt)
            return result.scalars().all()

db = Database()
