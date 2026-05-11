def predict_demand_with_oracle(product_name: str, recent_sales_7d: int, recent_sales_30d: int) -> int:
    """
    Tahmin Oracle agent ile entegrasyon için adapter.
    Şimdilik fallback heuristic kullanıyor.
    İsterseniz sonra burayı kendi ml_module fonksiyonunuza bağlarsınız.
    """

    monthly_weekly_avg = recent_sales_30d / 4 if recent_sales_30d > 0 else 0
    momentum_bonus = max(recent_sales_7d - monthly_weekly_avg, 0)
    predicted = int(round(monthly_weekly_avg + (momentum_bonus * 0.8)))

    if predicted < 0:
        predicted = 0

    return predicted
