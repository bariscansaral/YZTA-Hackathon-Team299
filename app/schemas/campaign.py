from pydantic import BaseModel


class CampaignRequest(BaseModel):
    product_id: str
    product_name: str
    current_stock: int
    predicted_demand: int
    recent_sales_7d: int
    recent_sales_30d: int
    current_price: float


class CampaignResponse(BaseModel):
    product_id: str
    product_name: str
    action: str
    suggested_discount_percent: int
    suggested_price: float
    priority: str
    reason_code: str
    explanation: str
    restock_recommended: bool