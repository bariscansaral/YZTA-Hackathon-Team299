from app.schemas.campaign import CampaignRequest, CampaignResponse


def generate_campaign_recommendation(payload: CampaignRequest) -> CampaignResponse:
    stock = payload.current_stock
    demand = payload.predicted_demand
    sales_7d = payload.recent_sales_7d
    price = payload.current_price

    action = "monitor"
    discount = 0
    priority = "medium"
    reason_code = "balanced_state"
    explanation = "Durum dengeli görünüyor. Şimdilik izleme önerilir."
    restock_recommended = False
    suggested_price = price

    if stock < 10 and demand > 80:
        action = "restock_alert"
        priority = "high"
        reason_code = "critical_low_stock_high_demand"
        explanation = (
            f"{payload.product_name} için stok kritik seviyede ve beklenen talep yüksek. "
            "İndirim yapılmamalı, acil tedarik planı önerilir."
        )
        restock_recommended = True

    elif stock < 20 and demand > 50:
        action = "hold_price"
        priority = "high"
        reason_code = "low_stock_high_demand"
        explanation = (
            f"{payload.product_name} ürününde talep güçlü ancak stok sınırlı. "
            "İndirim yerine fiyatın korunması önerilir."
        )
        restock_recommended = True

    elif stock > 100 and demand < 30:
        action = "discount"
        discount = 15
        priority = "high"
        reason_code = "high_stock_low_demand"
        explanation = (
            f"{payload.product_name} ürününde stok yüksek ve beklenen talep düşük. "
            f"Satış hızını artırmak için %{discount} kampanya önerilir."
        )
        suggested_price = round(price * (1 - discount / 100), 2)

    elif stock > 60 and sales_7d < 10:
        action = "discount"
        discount = 10
        priority = "medium"
        reason_code = "slow_moving_inventory"
        explanation = (
            f"{payload.product_name} son 7 günde yavaş satılmış görünüyor. "
            f"Hafif kampanya ile ürün hareketlendirilebilir. Öneri: %{discount} indirim."
        )
        suggested_price = round(price * (1 - discount / 100), 2)

    elif stock >= 20 and demand >= 50:
        action = "hold_price"
        priority = "medium"
        reason_code = "healthy_demand"
        explanation = (
            f"{payload.product_name} için talep sağlıklı görünüyor. "
            "Mevcut fiyat korunabilir."
        )

    return CampaignResponse(
        product_id=payload.product_id,
        product_name=payload.product_name,
        action=action,
        suggested_discount_percent=discount,
        suggested_price=suggested_price,
        priority=priority,
        reason_code=reason_code,
        explanation=explanation,
        restock_recommended=restock_recommended,
    )