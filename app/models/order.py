from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import Base

class Order(Base):
    __tablename__ = 'orders'

    id=Column(Integer, primary_key=True, index=True)
    user_id=Column(Integer, ForeignKey('users.id'))
    status=Column(String, default='Beklemede')