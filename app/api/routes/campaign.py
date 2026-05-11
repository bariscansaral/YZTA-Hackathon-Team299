from fastapi import APIRouter
from app.schemas.campaign import CampaignRequest, CampaignResponse
from app.services.campaign_agent import generate_campaign_recommendation

router = APIRouter(prefix="/campaign", tags=["Campaign Agent"])


@router.post("/recommend", response_model=CampaignResponse)
def recommend_campaign(payload: CampaignRequest):
    return generate_campaign_recommendation(payload)