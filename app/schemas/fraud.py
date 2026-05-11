from pydantic import BaseModel
from typing import List


class FraudRequest(BaseModel):
    order_id: str
    user_id: str
    user_order_count: int
    order_total: float
    item_count: int
    unique_product_count: int
    contains_high_value_item: bool
    repeated_failed_orders: int
    unusual_quantity: bool


class FraudByOrderRequest(BaseModel):
    order_id: int


class FraudResponse(BaseModel):
    order_id: str
    user_id: str
    fraud_risk_level: str
    fraud_score: float
    decision: str
    reason_codes: List[str]
    explanation: str
    recommended_actions: List[str]
    source: str
