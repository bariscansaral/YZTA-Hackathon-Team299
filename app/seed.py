"""
SEED SCRIPT

EN:
This script initializes the database and fills it with sample data.
It supports two modes:
- CLEAN mode: valid and consistent data
- DIRTY mode: intentionally corrupted data for AI agent testing

TR:
Bu script veritabanını oluşturur ve örnek verilerle doldurur.
İki mod destekler:
- CLEAN: düzgün ve tutarlı veriler
- DIRTY: AI agent testleri için bozuk/veri hatalı kayıtlar
"""

import random
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem

MODE="MANUAL" #dirty & clean

def seed_users(db):
    users = [
        User(name="Admin", surname="System", email="admin@test.com", password="1234", role="admin"),
        User(name="Barışcan", surname="Saral", email="bariscan@test.com", password="yzta55123", role="admin"),
        User(name="Ali", surname="Veli", email="ali@test.com", password="4321", role="user"),
        User(name="Ayse",surname="Yilmaz", email="ayse@test.com", password="1234", role="user"),
        User(name="Mehmet",surname="Kaya", email="mehmet@test.com", password="4321", role="user"),
    ]

    db.add_all(users)

"""def seed_products(db):
    products = []
    for i in range(1,31):
        if MODE=="DIRTY":
            products.append(Product(
                name="UNKNOWN" if random.random() < 0.3 else f"Product {i}",
                sku=None if random.random() < 0.5 else f"prd-{i}",
                stock=-10 if random.random() < 0.4 else None,
                price=None if random.random() < 0.5 else random.randint(10, 2000)
            ))
        else:
            products.append(Product(
                name=f"Product {i}",
                sku=f"PRD-{i:04d}",
                stock=random.randint(1,100),
                price=random.randint(1,100)
            ))
    db.add_all(products)"""


def seed_products(db):
    products = [
        Product(name="Anzer Balı", sku="BAL-001", stock=50, price=1200),
        Product(name="Kars Kaşarı", sku="PEY-002", stock=30, price=450),
        Product(name="Siyez Unu", sku="TAH-003", stock=100, price=80),
        Product(name="Erzincan Tulumu", sku="PEY-004", stock=25, price=380),
        Product(name="Rize Çayı", sku="CAY-005", stock=200, price=150),
        Product(name="Afyon Sucuğu", sku="ET-006", stock=40, price=650),
        Product(name="Gemlik Zeytini", sku="ZEY-007", stock=120, price=220),
        Product(name="Datça Bademi", sku="KUR-008", stock=60, price=550),
        Product(name="Isparta Gül Reçeli", sku="REC-009", stock=45, price=120),
        Product(name="Maraş Tarhanası", sku="COR-010", stock=85, price=180),
    ]
    for i in range(11, 41):
        products.append(Product(
            name=f"Yerel Kooperatif Ürünü {i}",
            sku=f"KOP-{i:03d}",
            stock=random.randint(20, 150),
            price=random.randint(40, 900)
        ))

    db.add_all(products)
    db.flush()


def seed_orders(db):
    o1 = Order(user_id=2, status="Beklemede")
    db.add(o1)
    db.flush()
    db.add_all([
        OrderItem(order_id=o1.id, product_id=1, quantity=1),  # Anzer Balı
        OrderItem(order_id=o1.id, product_id=5, quantity=2)  # Rize Çayı
    ])

    o2 = Order(user_id=3, status="Hazırlanıyor")
    db.add(o2)
    db.flush()
    db.add_all([
        OrderItem(order_id=o2.id, product_id=6, quantity=1),  # Sucuk
        OrderItem(order_id=o2.id, product_id=2, quantity=1)  # Kaşar
    ])

    o3 = Order(user_id=4, status="Tamamlandı")
    db.add(o3)
    db.flush()
    db.add_all([
        OrderItem(order_id=o3.id, product_id=3, quantity=5)  # Siyez Unu
    ])

    o4 = Order(user_id=2, status="Beklemede")
    db.add(o4)
    db.flush()
    db.add_all([
        OrderItem(order_id=o4.id, product_id=4, quantity=20)  # 25 stoktan 20'sini çekiyor
    ])


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(Product).delete()
        db.query(User).delete()

        seed_users(db)
        seed_products(db)
        seed_orders(db)

        db.commit()
        print(f" MANUAL Mod: Veritabanı temizlendi ve 40 ürün + 4 farklı tipte siparişle dolduruldu.")
    except Exception as e:
        db.rollback()
        print(f"Hata: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()