from app.schemas.campaign import CampaignRequest, CampaignResponse
from app.services.forecast_adapter import predict_demand_with_oracle
from app.services.llm_explainer import generate_llm_explanation
from app.models.product import Product


def calculate_sales_velocity(recent_sales_7d: int, recent_sales_30d: int) -> float:
    weekly_avg = recent_sales_7d / 7 if recent_sales_7d > 0 else 0
    monthly_avg = recent_sales_30d / 30 if recent_sales_30d > 0 else 0
    return round((weekly_avg * 0.7) + (monthly_avg * 0.3), 2)


def calculate_stock_coverage(current_stock: int, predicted_demand: int) -> float:
    if predicted_demand <= 0:
        return 999.0
    return round(current_stock / predicted_demand, 2)


def build_campaign_request_from_product_id(db, product_id: int) -> CampaignRequest:
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise ValueError("Product not found")

    predicted_demand = predict_demand_with_oracle(
        product_name=product.name,
        recent_sales_7d=10,
        recent_sales_30d=40,
    )

    return CampaignRequest(
        product_id=str(product.id),
        product_name=product.name,
        current_stock=product.stock,
        predicted_demand=predicted_demand,
        recent_sales_7d=10,
        recent_sales_30d=40,
        current_price=product.price,
    )


def generate_campaign_recommendation(
    payload: CampaignRequest,
    source: str = "manual_input",
) -> CampaignResponse:
    sales_velocity = calculate_sales_velocity(
        payload.recent_sales_7d,
        payload.recent_sales_30d,
    )

    stock_coverage = calculate_stock_coverage(
        payload.current_stock,
        payload.predicted_demand,
    )

    risk_level = "low"
    confidence_score = 0.92
    suggested_discount = 0
    action = "hold_price"
    reason_code = "healthy_balance"
    priority = "medium"
    restock_recommended = False
    campaign_type = "none"
    next_actions = ["Monitor demand"]

    if payload.current_stock > payload.predicted_demand * 2:
        action = "discount_campaign"
        suggested_discount = 20
        reason_code = "overstock"
        priority = "high"
        risk_level = "medium"
        confidence_score = 0.89
        campaign_type = "clearance"
        next_actions = ["Launch campaign", "Monitor conversion"]

    elif payload.current_stock < payload.predicted_demand:
        action = "restock"
        suggested_discount = 0
        reason_code = "understock"
        priority = "critical"
        risk_level = "high"
        confidence_score = 0.95
        restock_recommended = True
        campaign_type = "inventory_recovery"
        next_actions = ["Replenish inventory", "Pause promotions"]

    suggested_price = round(
        payload.current_price * (1 - suggested_discount / 100),
        2,
    )

    fallback_text = (
        f"{payload.product_name} için öneri: {action}. "
        f"Sebep: {reason_code}. "
        f"İndirim: %{suggested_discount}."
    )

    explanation = generate_llm_explanation(
        product_name=payload.product_name,
        action=action,
        reason_code=reason_code,
        current_stock=payload.current_stock,
        predicted_demand=payload.predicted_demand,
        suggested_discount_percent=suggested_discount,
        campaign_type=campaign_type,
        fallback_text=fallback_text,
    )

    return CampaignResponse(
        product_id=payload.product_id,
        product_name=payload.product_name,
        action=action,
        suggested_discount_percent=suggested_discount,
        suggested_price=suggested_price,
        priority=priority,
        risk_level=risk_level,
        confidence_score=confidence_score,
        reason_code=reason_code,
        explanation=explanation,
        restock_recommended=restock_recommended,
        campaign_type=campaign_type,
        next_actions=next_actions,
        predicted_demand=payload.predicted_demand,
        recent_sales_7d=payload.recent_sales_7d,
        recent_sales_30d=payload.recent_sales_30d,
        stock_coverage_days=stock_coverage,
        sales_velocity_score=sales_velocity,
        source=source,
    )