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
from datetime import datetime, timedelta

MODE="MANUAL" #dirty & clean

def seed_users(db):
    now = datetime.now()
    users = [
        User(name="Admin", surname="System", email="admin@test.com", password="1234", role="admin"),
        User(name="Barışcan", surname="Saral", email="bariscan@test.com", password="yzta55123", role="admin",last_order_date=now),
        User(name="Ali", surname="Veli", email="ali@test.com", password="4321", role="user",last_order_date=now - timedelta(hours=2)),
        User(name="Ayse",surname="Yilmaz", email="ayse@test.com", password="1234", role="user",last_order_date=now - timedelta(days=120)),
        User(name="Mehmet",surname="Kaya", email="mehmet@test.com", password="4321", role="user",last_order_date=None),
        User(name="Can",surname="Aksoy",email="can@test.com", password="1234", role="user",last_order_date=datetime(2026, 1, 15, 14, 30)),
        User(name="Zeynep",surname="Yılmaz",email="zeynep@test.com",password="1234", role="user",last_order_date=datetime(2025, 11, 20, 10, 0)),
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

    categories = {
        "PEY": ["Kars Kaşarı", "Erzincan Tulumu", "İzmir Tulumu", "Çeçil Peyniri", "Lor Peyniri", "Köy Peyniri",
                "Süzme Peynir", "Çökelek"],
        "YOG": ["Süzme Yoğurt", "Manda Yoğurdu", "Meyveli Yoğurt", "Keçi Yoğurdu"],
        "SUT": ["Tam Yağlı Süt", "Yarım Yağlı Süt", "Laktozsuz Süt", "Süt Yağı"],
        "YAG": ["Yayık Tereyağı", "Vakfıkebir Tereyağı", "Köy Tereyağı", "Tuzlu Tereyağı", "Sade Yağ"],
        "DON": ["Maraş Dondurması", "Vanilyalı Dondurma", "Kakaolu Dondurma"],
        "AYR": ["Naneli Ayran", "Sade Ayran", "Fesleğenli Ayran", "Pastörize Ayran"],
        "DRK": ["Kefir", "Kımız"]  # İçecek/Diğer grubu
    }

    products = []

    for prefix, names in categories.items():
        for i, name in enumerate(names, start=1):

            sku_code = f"{prefix}-{i:03d}"

            # TEST SENARYOLARI (Stock Risk ve Campaign Agentları için)
            # Peynirleri (PEY) Kritik Stok yapalım (Düşük Stok)
            if prefix == "PEY":
                stock = random.randint(2, 10)
                price = random.randint(250, 600)
            # Yağları (YAG) Overstock yapalım (Yüksek Stok)
            elif prefix == "YAG":
                stock = random.randint(600, 1000)
                price = random.randint(150, 400)
            # Geri kalanlar normal/dengeli
            else:
                stock = random.randint(40, 150)
                price = random.randint(40, 200)

            products.append(Product(
                name=name,
                sku=sku_code,
                stock=stock,
                price=price
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
        print(f" MANUAL Mod: Veritabanı temizlendi farklı tipte siparişler dolduruldu.")
    except Exception as e:
        db.rollback()
        print(f"Hata: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()