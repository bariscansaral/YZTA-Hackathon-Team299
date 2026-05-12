from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime, date

from app import auth
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem

from app.agents.main_crew import integrated_crew
from app.agents.gatekeeper_agent import gatekeeper_crew

from app.api.routes.campaign import router as campaign_router
from app.api.routes.stock_risk import router as stock_risk_router
from app.api.routes.fraud import router as fraud_router

from app.api.routes.retention import router as retention_router


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

app.include_router(retention_router)

class ChatRequest(BaseModel):
    product_name: str = "Tuzlu Tereyağı"

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


@app.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print(f"--- LOGIN DENEMESİ: {form_data.username} ---")

    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        print(f"Kullanıcı bulundu mu: {user is not None}")

        if not user or not auth.verify_password(form_data.password, user.password):
            print("Şifre hatalı veya kullanıcı yok")
            raise HTTPException(status_code=401, detail="Hatalı e-posta veya şifre")

        print(f"Token oluşturuluyor... Role: {user.role}")
        access_token = auth.create_access_token(
            data={"sub": user.email, "role": user.role}
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print(f"HATA ÇIKTI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", tags=["Chatbot"])
async def chat_with_agents(
        request: ChatRequest,
        current_user: User = Depends(auth.get_current_user),
        db: Session = Depends(get_db)
):
    try:
        product_obj = db.query(Product).filter(Product.name == request.product_name).first()
        stock_val = product_obj.stock if product_obj else "Bilgi yok"

        if not product_obj and current_user.role == "admin":
            raise HTTPException(status_code=404, detail="Admin işlemleri için geçerli ürün şart.")
        display_name = f"{current_user.name} {current_user.surname}"
        inputs = {
            'user_name': current_user.name,
            'user_email': current_user.email,
            'user_role': current_user.role,
            'product': request.product_name,
            'product_name': request.product_name,
            'current_stock': stock_val,
            'date': date.today().isoformat(),
        }

        if current_user.role == "user":
            result =gatekeeper_crew.kickoff(inputs=inputs)
        else:
            result = integrated_crew.kickoff(inputs=inputs)

        return {
            "status": "Success",
            "meta_data": {
                "user": current_user.email,
                "role": current_user.role
            },
            "ai_chat_reply": result.raw if hasattr(result, 'raw') else str(result)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {
        "message": "YZTA Smart Retail API running",
        "docs": "/docs",
        "campaign_agent": "/campaign/recommend",
        "stock_risk_agent": "/stock-risk/analyze",
        "fraud_agent": "/fraud/analyze"
    }


@app.get("/inventory", tags=["Envanter"])
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
    user.last_order_date = datetime.now()

    db.commit()
    db.refresh(new_order)
    return {"message": f"Sipariş oluşturuldu. Sipariş no: {new_order.id}"}