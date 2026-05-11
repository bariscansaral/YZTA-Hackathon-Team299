from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.campaign import (
    CampaignRequest,
    CampaignResponse,
    CampaignByProductRequest,
)
from app.services.campaign_agent import (
    generate_campaign_recommendation,
    build_campaign_request_from_product_id,
)

router = APIRouter(prefix="/campaign", tags=["Campaign Agent"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/recommend", response_model=CampaignResponse)
def recommend_campaign(payload: CampaignRequest):
    return generate_campaign_recommendation(payload, source="manual_input")


@router.post("/recommend/by-product", response_model=CampaignResponse)
def recommend_campaign_by_product(
    payload: CampaignByProductRequest,
    db: Session = Depends(get_db),
):
    try:
        campaign_payload = build_campaign_request_from_product_id(db, payload.product_id)
        return generate_campaign_recommendation(campaign_payload, source="db_plus_oracle")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))