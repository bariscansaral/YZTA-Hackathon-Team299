from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem

from app.api.routes.campaign import router as campaign_router
from app.api.routes.stock_risk import router as stock_risk_router
from app.api.routes.fraud import router as fraud_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="YZTA Smart Retail API",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.include_router(campaign_router)
app.include_router(stock_risk_router)
app.include_router(fraud_router)


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


@app.get("/")
def root():
    return {
        "message": "YZTA Smart Retail API running",
        "docs": "/docs",
        "campaign_agent": "/campaign/recommend",
        "stock_risk_agent": "/stock-risk/analyze",
        "fraud_agent": "/fraud/analyze"
    }


@app.get("/inventory/", tags=["Envanter"])
async def get_all_inventory(db: Session = Depends(get_db)):
    return db.query(Product).all()


@app.get("/orders", tags=["Siparişler"])
async def get_all_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@app.get("/orders/pending", tags=["Siparişler"])
async def get_pending_orders(db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.status == "Beklemede").all()


@app.post("/orders/create", tags=["Siparişler"])
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == order_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    new_order = Order(user_id=order_data.user_id, status="Beklemede")
    db.add(new_order)
    db.flush()

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            db.rollback()
            raise HTTPException(status_code=404, detail="Ürün bulunamadı")

        if product.stock < item.quantity:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"{product.name} için yeterli stok yok!")

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        product.stock -= item.quantity
        db.add(order_item)

    db.commit()
    db.refresh(new_order)
    return {"message": f"Sipariş oluşturuldu. Sipariş no: {new_order.id}"}