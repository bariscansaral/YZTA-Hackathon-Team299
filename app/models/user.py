from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id=Column(Integer, primary_key=True, index=True)
    name=Column(String, nullable=False)
    surname=Column(String, nullable=False)
    email=Column(String, nullable=False, unique=True)
    password=Column(String, nullable=False)
    role= Column(String, default="user") #admin/user
    last_order_date = Column(DateTime, nullable=True)