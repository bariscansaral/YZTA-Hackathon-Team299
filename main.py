from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem

app= FastAPI(title="YZTA-Hackathon Operasyon Merkezi")

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]




@app.get("/inventory/", tags=["Envanter"])
async def get_all_inventory(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/inventory/critical/", tags=["Envanter"])
async def get_critical_stock(threshold: int=10, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.stock <= threshold).all()

@app.patch("/inventory/{product_id}/update-stock", tags=["Envanter"])
async def update_stock(product_id: int, quantity: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id==product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün Bulunamadı")
    product.stock = quantity
    db.commit()
    return {"message":f"{product.name} stoğu {quantity} olarak güncellendi"}



@app.get("/orders/pending", tags=["Siparişler"])
async def get_pending_orders(db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.status=="Beklemede").all()

@app.get("/orders/{order_id}/items", tags=["Siparişler"])
async def get_order_items(order_id: int, db: Session = Depends(get_db)):
    items = db.query(OrderItem.order_id,OrderItem.quantity,Product.name.label("product_name")).join(Product, OrderItem.product_id == Product.id).filter(OrderItem.order_id == order_id).all()
    return [{"order_id": item.order_id, "quantity": item.quantity, "product_name": item.product_name} for item in items]

@app.patch("/orders/{order_id}/status", tags=["Siparişler"])
async def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order=db.query(Order).filter(Order.id==order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sipariş Bulunamadı!")
    order.status=status
    db.commit()
    return {"message":f"Sipariş {order_id} durumu {status} olarak güncellendi!"}

@app.get("/orders", tags=["Siparişler"])
async def get_all_orders(db: Session=Depends(get_db)):
    orders=db.query(Order.id,Order.status,User.name.label("user_name"),User.surname.label("user_surname")).join(User,Order.user_id == User.id).all()
    return [{"order_id":order.id,"durum":order.status,"müşteri": f"{order.user_name} {order.user_surname}"} for order in orders]




@app.get("/users/{user_id}/history",tags=["Müşteri"])
async def get_user_history(user_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id==user_id).all()

@app.get("/users/", tags=["Müşteri"])
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/orders/create", tags=["Siparişler"])
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == order_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Kullanıcı ID {order_data.user_id} bulunamadı")

    new_order=Order(user_id=order_data.user_id, status="Beklemede")
    db.add(new_order)
    db.flush()
    for item in order_data.items:
        product=db.query(Product).filter(Product.id==item.product_id).first()
        if not product:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Ürün ID {item.product_id} bulunamadı!")

        if product.stock<item.quantity:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"{product.name} için yeterli stok yok!")
        order_item=OrderItem(order_id=new_order.id, product_id=item.product_id, quantity=item.quantity)
        product.stock -= item.quantity
        db.add(order_item)
    db.commit()
    db.refresh(new_order)
    return {"message":f"Sipariş başarıyla oluşturuldu, Sipariş numaranız: {new_order.id}"}
