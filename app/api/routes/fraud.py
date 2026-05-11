from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.fraud import FraudRequest, FraudByOrderRequest, FraudResponse
from app.services.fraud_agent import analyze_fraud_risk, build_fraud_request_from_order_id

router = APIRouter(prefix="/fraud", tags=["Fraud Agent"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/analyze", response_model=FraudResponse)
def analyze_fraud(payload: FraudRequest):
    return analyze_fraud_risk(payload, source="manual_input")


@router.post("/analyze/by-order", response_model=FraudResponse)
def analyze_fraud_by_order(
    payload: FraudByOrderRequest,
    db: Session = Depends(get_db),
):
    try:
        fraud_payload = build_fraud_request_from_order_id(db, payload.order_id)
        return analyze_fraud_risk(fraud_payload, source="db_order")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
