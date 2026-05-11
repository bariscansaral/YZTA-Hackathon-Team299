from sqlalchemy import Column, Integer, String,Float
from app.database import Base

class Product(Base):
    __tablename__ = 'products'

    id=Column(Integer, primary_key=True, index=True)
    name=Column(String, nullable=False)
    sku=Column(String, unique=True)
    stock=Column(Integer, default=0)
    price=Column(Float, default=0.0)