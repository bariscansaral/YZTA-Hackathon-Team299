import os
from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
from dotenv import load_dotenv
from pydantic.v1 import Field, BaseModel
from typing import Type
from langchain_google_genai import ChatGoogleGenerativeAI
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
    role='Stratejik Pazarlama ve Müşteri İlişkileri Müdürü',
    goal='Hem ürün stok durumuna hem de müşteri sadakatine göre kişiselleştirilmiş kampanyalar üretmek.',
    backstory="""Sen veriyi çok iyi okuyan bir pazarlama dâhisisin. 
    Sadece 'ürün' satmazsın; 'doğru ürünü doğru müşteriye' satarsın.
    Stok fazlası olan bir ürünü, o ürünü en çok özleyen (retention risk) müşteriye 
    pazarlarsın, Müşterilerin isimlerine ve segmentlerine göre her biri için bambaşka, yaratıcı ve samimi SMS metinleri oluştur. Birbirini asla tekrar etmezsin.
    Müşterilerine asla [İsim] diye hitap etmezsin, tool'dan gelen gerçek isimleri raporuna tek tek yazarsın.""",
    tools=[CampaignDecisionTool(), RetentionAnalysisTool()],
    verbose=True,
    memory=True,
    llm=llm_model
)


marketing_task = Task(
    description=(
        "1. 'campaign_decision_tool' ile {product_name} için stratejik kararı al.\n"
        "2. 'retention_analysis_tool' ile müşteri listesini çek.\n"
        "3. Elde ettiğin verileri sentezleyerek admin için kısa ve öz bir rapor oluştur.\n"
        "NOT: SMS örneklerini her segmente özel sadece birer cümlelik taslak olarak ekle."
    ),
    expected_output=(
        "Admin için 3 maddelik yönetici özeti:\n"
        "1. Satış Tahmini & Karar: [Rakam ve Karar]\n"
        "2. Stok & Müşteri Analizi: [Stok Riski ve Riskli Müşteri Sayısı]\n"
        "3. Aksiyon Planı (SMS Taslakları): [Segmente özel çok kısa mesaj örnekleri]\n"
        "TOPLAM: Maksimum 200 kelime."
    ),
    agent=marketing_agent
)