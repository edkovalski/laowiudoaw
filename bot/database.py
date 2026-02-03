import asyncio
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import DATABASE_PATH

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(50))
    first_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    player_id = Column(String(12))
    diamonds_amount = Column(Integer)
    amount = Column(Integer)
    status = Column(String(20), default='pending')
    payment_proof = Column(Text)
    rejection_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Database:
    def __init__(self):
        self.engine = create_async_engine(f'sqlite+aiosqlite:///{DATABASE_PATH}')
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
    
    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self):
        return self.async_session()
    
    async def create_user(self, user_id: int, username: str = None, first_name: str = None):
        async with self.async_session() as session:
            user = User(user_id=user_id, username=username, first_name=first_name)
            session.add(user)
            await session.commit()
    
    async def create_order(self, user_id: int, player_id: str, diamonds_amount: int, amount: int, payment_proof: str = None):
        async with self.async_session() as session:
            order = Order(
                user_id=user_id,
                player_id=player_id,
                diamonds_amount=diamonds_amount,
                amount=amount,
                payment_proof=payment_proof
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
