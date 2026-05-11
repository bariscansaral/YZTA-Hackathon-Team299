from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.fraud import FraudRequest, FraudResponse


def build_fraud_request_from_order_id(db: Session, order_id: int) -> FraudRequest:
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise ValueError("Order not found")

    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    if not items:
        raise ValueError("Order has no items")

    user_order_count = (
        db.query(func.count(Order.id))
        .filter(Order.user_id == order.user_id)
        .scalar()
    ) or 0

    order_total = 0.0
    item_count = 0
    unique_product_ids = set()
    contains_high_value_item = False
    unusual_quantity = False

    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue

        line_total = float(product.price) * item.quantity
        order_total += line_total
        item_count += item.quantity
        unique_product_ids.add(item.product_id)

        if float(product.price) >= 800:
            contains_high_value_item = True

        if item.quantity >= 10:
            unusual_quantity = True

    return FraudRequest(
        order_id=str(order.id),
        user_id=str(order.user_id),
        user_order_count=user_order_count,
        order_total=order_total,
        item_count=item_count,
        unique_product_count=len(unique_product_ids),
        contains_high_value_item=contains_high_value_item,
        repeated_failed_orders=0,
        unusual_quantity=unusual_quantity,
    )


def analyze_fraud_risk(payload: FraudRequest, source: str = "manual_input") -> FraudResponse:
    score = 0.0
    reason_codes = []

    if payload.user_order_count <= 1:
        score += 0.20
        reason_codes.append("new_user")

    if payload.order_total > 5000:
        score += 0.30
        reason_codes.append("high_order_value")
    elif payload.order_total > 2500:
        score += 0.18
        reason_codes.append("medium_high_order_value")

    if payload.item_count >= 20:
        score += 0.20
        reason_codes.append("large_item_count")

    if payload.unique_product_count >= 8:
        score += 0.12
        reason_codes.append("many_unique_products")

    if payload.contains_high_value_item:
        score += 0.15
        reason_codes.append("high_value_item")

    if payload.repeated_failed_orders >= 2:
        score += 0.20
        reason_codes.append("repeated_failed_orders")

    if payload.unusual_quantity:
        score += 0.18
        reason_codes.append("unusual_quantity")

    score = min(round(score, 2), 1.0)

    fraud_risk_level = "low"
    decision = "approve"
    explanation = "Sipariş düşük riskli görünüyor. Otomatik onaylanabilir."
    recommended_actions = [
        "Siparişi normal akışta işle",
        "Standart teslimat sürecine devam et",
    ]

    if score >= 0.75:
        fraud_risk_level = "critical"
        decision = "block_temporarily"
        explanation = "Sipariş çok yüksek riskli görünüyor. Geçici blok ve manuel inceleme önerilir."
        recommended_actions = [
            "Siparişi geçici olarak durdur",
            "Kullanıcı ve ödeme bilgilerini manuel incele",
            "Gerekirse müşteriyle doğrulama yap",
        ]

    elif score >= 0.50:
        fraud_risk_level = "high"
        decision = "manual_review"
        explanation = "Sipariş yüksek risk sinyalleri taşıyor. Manuel inceleme önerilir."
        recommended_actions = [
            "Siparişi manuel incelemeye al",
            "Ürün adetlerini ve ödeme bilgisini kontrol et",
            "Onay sonrası işleme devam et",
        ]

    elif score >= 0.25:
        fraud_risk_level = "medium"
        decision = "review_light"
        explanation = "Siparişte orta seviye risk sinyalleri var. Hafif kontrol önerilir."
        recommended_actions = [
            "Siparişi otomatik işleme almadan önce temel kontrol yap",
            "Kullanıcı geçmişini kontrol et",
        ]

    if not reason_codes:
        reason_codes.append("normal_order_pattern")

    return FraudResponse(
        order_id=payload.order_id,
        user_id=payload.user_id,
        fraud_risk_level=fraud_risk_level,
        fraud_score=score,
        decision=decision,
        reason_codes=reason_codes,
        explanation=explanation,
        recommended_actions=recommended_actions,
        source=source,
    )
