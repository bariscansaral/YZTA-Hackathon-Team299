from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.stock_risk import (
    StockRiskRequest,
    StockRiskByProductRequest,
    StockRiskResponse,
)
from app.services.stock_risk_agent import (
    analyze_stock_risk,
    build_stock_risk_request_from_product_id,
)

router = APIRouter(prefix="/stock-risk", tags=["Stock Risk Agent"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/analyze", response_model=StockRiskResponse)
def analyze_stock(payload: StockRiskRequest):
    return analyze_stock_risk(payload, source="manual_input")


@router.post("/analyze/by-product", response_model=StockRiskResponse)
def analyze_stock_by_product(
    payload: StockRiskByProductRequest,
    db: Session = Depends(get_db),
):
    try:
        stock_payload = build_stock_risk_request_from_product_id(db, payload.product_id)
        return analyze_stock_risk(stock_payload, source="db_plus_oracle")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
