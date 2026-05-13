import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool
from dotenv import load_dotenv
from pydantic.v1 import Field, BaseModel
from typing import Type
from langchain_google_genai import ChatGoogleGenerativeAI
from app.agents.predict_tool import sales_forecast_tool
from langchain.tools import tool
from app.services.campaign_agent import generate_campaign_recommendation
from app.services.retention_agent import RetentionAgent
from app.schemas.campaign import CampaignRequest, CampaignResponse

load_dotenv()

llm_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    verbose=True,
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class RetentionAnalysisTool(BaseTool):
    name: str = "retention_analysis_tool"
    description: str = "Veritabanındaki kullanıcıları analiz eder ve segmentleri listeler."

    def _run(self) -> str:
        from app.services.retention_agent import RetentionAgent
        from app.database import SessionLocal

        db = SessionLocal()
        agent = RetentionAgent(db)
        results = agent.analyze_and_engage()
        db.close()
        return str(results)

class CampaignInput(BaseModel):
    product_id: str = Field(..., description="Ürün ID")
    product_name: str = Field(..., description="Ürün adı")
    current_stock: int = Field(..., description="Mevcut stok")
    predicted_demand: int = Field(..., description="Tahmin edilen talep")
    current_price: float = Field(..., description="Fiyat")
    recent_sales_7d: int = Field(..., description="7 günlük satış")
    recent_sales_30d: int = Field(..., description="30 günlük satış")

class CampaignDecisionTool(BaseTool):
    name: str = "campaign_decision_tool"
    description: str = "Stok ve tahmin verilerini alarak kampanya kararı veren resmi karar motorudur."
    args_schema: Type[BaseModel] = CampaignInput
    def _run(self, product_id: str, product_name: str, current_stock: int, predicted_demand: int, current_price: float,
             recent_sales_7d: int, recent_sales_30d: int) -> str:
        # Mevcut logic'ini buraya al
        from app.services.campaign_agent import generate_campaign_recommendation
        from app.schemas.campaign import CampaignRequest

        payload = CampaignRequest(
            product_id=str(product_id),
            product_name=product_name,
            current_stock=int(current_stock),
            predicted_demand=int(predicted_demand),
            current_price=float(current_price),
            recent_sales_7d=int(recent_sales_7d),
            recent_sales_30d=int(recent_sales_30d)
        )
        result = generate_campaign_recommendation(payload)
        return str(result)


marketing_agent = Agent(
    role='Stratejik Pazarlama Müdürü',
    goal='Stok verisi ve satış tahminlerini karşılaştırarak kampanya stratejisi üretmek ve kişiselleştirmiş mesajlar hazırlamak.',
    backstory="""Sen veriye dayalı kampanya yürüten, çözüm odaklı bir yöneticisin. 
    Sana verilen ürün bilgilerini (fiyat, satış geçmişi vb.) analiz eder, 
    eğer bazı teknik detaylar eksikse bunları sektör standartlarına göre makul değerlerle 
    tamamlayarak karar motorunu (CampaignDecisionTool) mutlaka çalıştırırsın. 
    Amacın stok eritmek ve müşteri sadakatini artırmaktır.""",
    tools=[CampaignDecisionTool(), RetentionAnalysisTool(), sales_forecast_tool],
    llm=llm_model,
    verbose=True
)


marketing_task = Task(
    description=(
        "1. '{product_name}' için '{date}' tarihindeki satışı 'sales_forecast_tool' ile tahmin et.\n"
        "2. Tahmini rakamı ve mevcut stok olan '{current_stock}'u 'campaign_decision_tool'a gönder.\n"
        "3. 'retention_analysis_tool' ile riskli müşteri segmentlerini belirle.\n"
        "4. Elde edilen verilerle kısa bir aksiyon planı hazırla."
    ),
    expected_output="Tahmin, Stok Durumu ve 3 maddelik kısa pazarlama aksiyon planı.",
    agent=marketing_agent
)

sms_generation_task = Task(
    description=(
        "1. Strateji görevinden gelen sonuçları al.\n"
        "2. 'retention_analysis_tool'dan gelen GERÇEK müşteri isimlerini kullan.\n"
        "3. Her segment (Kaybetme Riski, Sadık Müşteri vb.) için birer adet, "
        "kullanıcının adıyla hitap eden, samimi ve kısa SMS taslağı oluştur.\n"
        "Örn: 'Merhaba Barışcan, çok sevdiğin İzmir Tulumu bugün sana özel indirimde!'"
    ),
    expected_output="Müşteri isimlerine özel hazırlanmış 3-4 farklı SMS taslağı.",
    agent=marketing_agent,
    context=[marketing_task]
)

marketing_crew = Crew(
    agents=[marketing_agent],
    tasks=[marketing_task, sms_generation_task],
    process=Process.sequential,
    verbose=True,
    max_rpm=10
)