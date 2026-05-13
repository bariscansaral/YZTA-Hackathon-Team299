from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime, date, timedelta
import re

from app import auth
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem

from app.agents.marketing_agent import marketing_crew
from app.agents.oracle_agent import oracle_crew
from app.agents.fraud_crew_agent import fraud_crew
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


app.include_router(campaign_router, prefix="/campaign", dependencies=[Depends(auth.admin_only)])
app.include_router(stock_risk_router, prefix="/stock-risk", dependencies=[Depends(auth.admin_only)])
app.include_router(fraud_router, prefix="/fraud", dependencies=[Depends(auth.admin_only)])

app.include_router(retention_router)

class ChatRequest(BaseModel):
    product_name: str = Field(default="Tuzlu Tereyağı", description="Tahmin edilecek ürün adı")
    target_date: str = Field(
        default=date.today().isoformat(),
        description="Tahmin hedef tarihi (Format: YYYY-MM-DD)",
        example="2026-06-01"
    )

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


@app.post("/login", tags=["Login"])
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


@app.post("/chat/support", tags=["Chatbot"])
async def chat_support(current_user: User = Depends(auth.get_current_user)):
    agent_inputs = {
        'user_name': f"{current_user.name} {current_user.surname}",
        'user_email': current_user.email
    }
    result = gatekeeper_crew.kickoff(inputs=agent_inputs)
    return {"ai_chat_reply": result.raw if hasattr(result, 'raw') else str(result)}


@app.post("/chat/forecast", tags=["Chatbot"], dependencies=[Depends(auth.admin_only)])
async def chat_forecast(request: ChatRequest, db: Session = Depends(get_db)):
    raw_text = request.product_name.strip()
    lower_text = raw_text.lower()
    numbers = re.findall(r'\d+', lower_text)
    threshold = int(numbers[0]) if numbers else None
    if any(word in lower_text for word in ["stok", "fazla", "listele", "limit"]):
        if threshold is not None:
            products = db.query(Product).filter(Product.stock >= threshold).all()
            print(f"DİNAMİK FİLTRE: {threshold} ve üzeri stoklar aranıyor...")
        else:
            products = db.query(Product).filter(Product.stock >= 50).all()

        if products:
            product_list_str = "\n".join([f"- {p.name}: {p.stock} adet" for p in products])
            inputs = {
                'product': f"Şu kriterdeki ürünlerin listesi: {product_list_str}",
                'current_stock': f"{threshold if threshold else 50} limitine göre filtrelendi.",
                'date': request.target_date or date.today().isoformat()
            }
            result = oracle_crew.kickoff(inputs=inputs)
            return {"ai_chat_reply": result.raw if hasattr(result, 'raw') else str(result)}
        else:
            return {"ai_chat_reply": f"{threshold} stok miktarının üzerinde hiçbir ürün bulunamadı."}
    product_obj = db.query(Product).filter(
        func.lower(Product.name).like(f"%{lower_text}%")
    ).first()

    if not product_obj:
        return {"ai_chat_reply": f"'{raw_text}' için bir ürün veya geçerli bir stok limiti bulamadım."}

    inputs = {
        'product': product_obj.name,
        'current_stock': int(product_obj.stock),
        'date': request.target_date or date.today().isoformat()
    }
    result = oracle_crew.kickoff(inputs=inputs)
    return {"ai_chat_reply": result.raw if hasattr(result, 'raw') else str(result)}



@app.post("/chat/marketing", tags=["Chatbot"], dependencies=[Depends(auth.admin_only)])
async def chat_marketing(request: ChatRequest, db: Session = Depends(get_db)):
    product_obj = db.query(Product).filter(
        func.lower(Product.name).like(f"%{request.product_name.lower()}%")
    ).first()

    if not product_obj:
        return {"ai_chat_reply": f"Üzgünüm, '{request.product_name}' isimli ürün envanterde bulunamadı. Lütfen listeden geçerli bir ürün seçin."}

    now = datetime.now()
    sales_30d = db.query(OrderItem).join(Order).filter(
        OrderItem.product_id == product_obj.id,
        Order.created_at >= (now - timedelta(days=30))
    ).with_entities(func.sum(OrderItem.quantity)).scalar() or 0

    inputs = {
        'product_id': str(product_obj.id),
        'product_name': product_obj.name,
        'current_stock': int(product_obj.stock),
        'current_price': float(getattr(product_obj, 'price', 150.0)),
        'recent_sales_30d': int(sales_30d),
        'date': request.target_date or date.today().isoformat()
    }

    try:
        result = marketing_crew.kickoff(inputs=inputs)
        return {"ai_chat_reply": result.raw if hasattr(result, 'raw') else str(result)}
    except Exception as e:
        return {"ai_chat_reply": "Analiz sırasında bir teknik aksaklık oluştu, ancak stok verilerine göre strateji hazır."}


@app.post("/chat/fraud", tags=["Chatbot"], dependencies=[Depends(auth.admin_only)])
async def chat_fraud(db: Session = Depends(get_db)):

    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(20).all()
    agent_inputs = {
        'analysis_scope': "Tüm sistem ve son 24 saatlik işlemler",
        'total_orders_to_check': len(recent_orders),
        'timestamp': datetime.now().isoformat()
    }
    result = fraud_crew.kickoff(inputs=agent_inputs)
    return {"ai_chat_reply": result.raw if hasattr(result, 'raw') else str(result)}



@app.get("/")
def root():
    return {
        "message": "YZTA Smart Retail API running",
        "docs": "/docs",
        "campaign_agent": "/campaign/recommend",
        "stock_risk_agent": "/stock-risk/analyze",
        "fraud_agent": "/fraud/analyze"
    }

@app.get("/orders/my-orders", tags=["Siparişler"])
async def get_user_orders(
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "admin":
        return db.query(Order).all()
    return db.query(Order).filter(Order.user_id == current_user.id).all()

@app.get("/inventory", tags=["Envanter"], dependencies=[Depends(auth.admin_only)])
async def get_all_inventory(db: Session = Depends(get_db)):
    return db.query(Product).all()


@app.get("/orders", tags=["Siparişler"], dependencies=[Depends(auth.admin_only)])
async def get_all_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@app.get("/orders/pending", tags=["Siparişler"], dependencies=[Depends(auth.admin_only)])
async def get_pending_orders(db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.status == "Beklemede").all()


@app.post("/orders/create", tags=["Siparişler"])
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db),current_user: User = Depends(auth.get_current_user)):
    if current_user.role != "admin" and current_user.id != order_data.user_id:
        raise HTTPException(status_code=403, detail="Sadece kendi adınıza sipariş oluşturabilirsiniz.")

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