from app.models.product import Product
from app.schemas.stock_risk import StockRiskRequest, StockRiskResponse
from app.services.forecast_adapter import predict_demand_with_oracle


def build_stock_risk_request_from_product_id(db, product_id: int) -> StockRiskRequest:
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise ValueError("Product not found")

    recent_sales_7d = 10
    recent_sales_30d = 40

    predicted_demand = predict_demand_with_oracle(
        product_name=product.name,
        recent_sales_7d=recent_sales_7d,
        recent_sales_30d=recent_sales_30d,
    )

    return StockRiskRequest(
        product_id=str(product.id),
        product_name=product.name,
        current_stock=product.stock,
        predicted_demand=predicted_demand,
        recent_sales_7d=recent_sales_7d,
        recent_sales_30d=recent_sales_30d,
    )


def analyze_stock_risk(payload: StockRiskRequest, source: str = "manual_input") -> StockRiskResponse:
    stock = payload.current_stock
    demand = max(payload.predicted_demand, 1)

    stock_coverage_ratio = round(stock / demand, 2)

    risk_level = "low"
    risk_score = 0.25
    stock_status = "healthy"
    restock_recommended = False
    recommended_restock_quantity = 0
    explanation = f"{payload.product_name} için stok seviyesi sağlıklı görünüyor."
    next_actions = [
        "Stok seviyesini izlemeye devam et",
        "Haftalık talep değişimini kontrol et",
    ]

    if stock <= 0:
        risk_level = "critical"
        risk_score = 1.0
        stock_status = "out_of_stock"
        restock_recommended = True
        recommended_restock_quantity = demand * 3
        explanation = f"{payload.product_name} stokta yok. Acil tedarik önerilir."
        next_actions = [
            "Acil tedarik başlat",
            "Ürünü kampanyadan çıkar",
            "Müşteri tarafında stok uyarısı göster",
        ]

    elif stock < demand:
        risk_level = "high"
        risk_score = 0.85
        stock_status = "understock"
        restock_recommended = True
        recommended_restock_quantity = max((demand * 2) - stock, 0)
        explanation = f"{payload.product_name} için stok, tahmini talebin altında."
        next_actions = [
            "Tedarik siparişi oluştur",
            "İndirim kampanyalarını durdur",
            "Satış hızını günlük takip et",
        ]

    elif stock < demand * 2:
        risk_level = "medium"
        risk_score = 0.55
        stock_status = "watch"
        restock_recommended = True
        recommended_restock_quantity = max((demand * 3) - stock, 0)
        explanation = f"{payload.product_name} için stok yeterli ama güvenli seviyede değil."
        next_actions = [
            "Tedarik hazırlığı yap",
            "Stok alarmı kur",
            "Kampanya kararını dikkatli ver",
        ]

    elif stock > demand * 5:
        risk_level = "low"
        risk_score = 0.20
        stock_status = "overstock"
        restock_recommended = False
        explanation = f"{payload.product_name} için stok tahmini talebe göre yüksek."
        next_actions = [
            "Campaign Agent ile indirim ihtimalini değerlendir",
            "Ürünü vitrinde öne çıkar",
            "Stok devir hızını takip et",
        ]

    return StockRiskResponse(
        product_id=payload.product_id,
        product_name=payload.product_name,
        current_stock=payload.current_stock,
        predicted_demand=payload.predicted_demand,
        risk_level=risk_level,
        risk_score=risk_score,
        stock_coverage_ratio=stock_coverage_ratio,
        stock_status=stock_status,
        restock_recommended=restock_recommended,
        recommended_restock_quantity=recommended_restock_quantity,
        explanation=explanation,
        next_actions=next_actions,
        source=source,
    )
