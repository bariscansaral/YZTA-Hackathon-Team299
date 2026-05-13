from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from app.database import Base
from sqlalchemy.sql import func

class Order(Base):
    __tablename__ = 'orders'

    id=Column(Integer, primary_key=True, index=True)
    user_id=Column(Integer, ForeignKey('users.id'))
    status=Column(String, default='Beklemede')
    created_at = Column(DateTime, default=func.now())