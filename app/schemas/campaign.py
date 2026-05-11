from pydantic import BaseModel
from typing import List


class CampaignRequest(BaseModel):
    product_id: str
    product_name: str
    current_stock: int
    predicted_demand: int
    recent_sales_7d: int
    recent_sales_30d: int
    current_price: float


class CampaignByProductRequest(BaseModel):
    product_id: int


class CampaignResponse(BaseModel):
    product_id: str
    product_name: str
    action: str
    suggested_discount_percent: int
    suggested_price: float
    priority: str
    risk_level: str
    confidence_score: float
    reason_code: str
    explanation: str
    restock_recommended: bool
    campaign_type: str
    next_actions: List[str]
    predicted_demand: int
    recent_sales_7d: int
    recent_sales_30d: int
    stock_coverage_days: float
    sales_velocity_score: float
    source: str