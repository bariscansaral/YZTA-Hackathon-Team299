from app.database import Base, engine
from app.models.user import User
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

if __name__ == '__main__':
    init_db()