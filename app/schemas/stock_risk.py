from pydantic import BaseModel
from typing import List


class StockRiskRequest(BaseModel):
    product_id: str
    product_name: str
    current_stock: int
    predicted_demand: int
    recent_sales_7d: int
    recent_sales_30d: int


class StockRiskByProductRequest(BaseModel):
    product_id: int


class StockRiskResponse(BaseModel):
    product_id: str
    product_name: str
    current_stock: int
    predicted_demand: int
    risk_level: str
    risk_score: float
    stock_coverage_ratio: float
    stock_status: str
    restock_recommended: bool
    recommended_restock_quantity: int
    explanation: str
    next_actions: List[str]
    source: str
