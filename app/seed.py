import random
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from datetime import datetime, timedelta
from sqlalchemy import func

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


            if prefix == "PEY":
                stock = random.randint(2, 10)
                price = random.randint(250, 600)

            elif prefix == "YAG":
                stock = random.randint(600, 1000)
                price = random.randint(150, 400)

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
    now = datetime.now()

    # 1. Senaryo: Son 7 günde yoğun satış (Trend analizi için)
    for i in range(10):
        o = Order(user_id=random.randint(3, 7), status="Tamamlandı",
                  created_at=now - timedelta(days=random.randint(1, 6)))
        db.add(o)
        db.flush()
        db.add(OrderItem(order_id=o.id, product_id=random.randint(1, 5), quantity=random.randint(1, 3)))

    # 2. Senaryo: 15-30 gün önce arası satışlar (30 günlük farkı görmek için)
    for i in range(5):
        o = Order(user_id=random.randint(3, 7), status="Tamamlandı",
                  created_at=now - timedelta(days=random.randint(15, 25)))
        db.add(o)
        db.flush()
        db.add(OrderItem(order_id=o.id, product_id=random.randint(1, 5), quantity=random.randint(2, 5)))

    # 3. Senaryo: Kargo/Destek Botu Testi için "Beklemede" siparişler
    o_pending = Order(user_id=2, status="Beklemede", created_at=now - timedelta(hours=5))
    db.add(o_pending)
    db.flush()
    db.add(OrderItem(order_id=o_pending.id, product_id=10, quantity=1))

    # 4. Senaryo: Fraud Botu Testi için anormal büyük sipariş
    o_fraud = Order(user_id=3, status="Hazırlanıyor", created_at=now)
    db.add(o_fraud)
    db.flush()
    db.add(OrderItem(order_id=o_fraud.id, product_id=12, quantity=100))


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