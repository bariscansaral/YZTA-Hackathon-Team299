import os
from crewai import Agent, Task, Crew
from langchain.tools import tool
from app.services.campaign_agent import generate_campaign_recommendation
from app.schemas.campaign import CampaignRequest, CampaignResponse


@tool("campaign_decision_tool")
def campaign_decision_tool(product_id: str, product_name: str, current_stock: int, predicted_demand: int, current_price: float, recent_sales_7d: int, recent_sales_30d: int) -> CampaignResponse:
    """
    Stok ve tahmin verilerini alarak; indirim mi yapılmalı, stok mu yenilenmeli
    yoksa fiyat sabit mi kalmalı, reklam kampanyası hangi platform üzerinden nasıl yürütülmeli kararını veren resmi karar motorudur.
    """
    payload = CampaignRequest(
        product_id=product_id,
        product_name=product_name,
        current_stock=current_stock,
        predicted_demand=predicted_demand,
        current_price=current_price,
        recent_sales_7d= recent_sales_7d,
        recent_sales_30d= recent_sales_30d
    )
    return generate_campaign_recommendation(payload)

# --- AGENT TANIMI ---
marketing_agent = Agent(
    role='Kreatif Pazarlama Müdürü',
    goal='Stratejik kampanya kararlarını satış artırıcı kreatif içeriklere dönüştürmek.',
    backstory="""Sen KOBİ'ler için çalışan bir pazarlama dâhisisin. 
    Karar motorundan gelen 'indirim' veya 'stok' uyarılarını alıp, 
    müşteriyi cezbedecek SMS, sosyal medya postu ve sloganlar üretirsin.""",
    tools=[campaign_decision_tool],
    verbose=True,
    memory=True
)

# --- TASK (GÖREV) TANIMI ---
marketing_task = Task(
    description=(
        "1. {product_name} ürünü için aşağıdaki verileri kullanarak campaign_decision_tool'u çalıştır:\n"
        "   - Mevcut Stok: {current_stock}\n"
        "   - Tahmin Edilen Talep: {predicted_demand}\n"
        "   - Son 7 Günlük Satış: {recent_sales_7d}\n"
        "   - Son 30 Günlük Satış: {recent_sales_30d}\n"
        "   - Mevcut Fiyat: {current_price}\n"
        "2. Araçtan gelen kararı analiz et.\n"
        "3. Karar 'discount_campaign' ise, talep ({predicted_demand}) ve stok ({current_stock}) dengesini vurgulayan, "
        "müşteriyi harekete geçirecek 3 farklı reklam sloganı ve bir kampanya SMS'i hazırla.\n"
        "4. Karar 'restock' ise, operasyon ekibi için acil stok yenileme notu yaz."
    ),
    expected_output="Rakamlara dayalı, profesyonelce hazırlanmış pazarlama içerikleri ve operasyonel kararlar.",
    agent=marketing_agent
)