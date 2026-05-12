import os
from crewai import Agent, Task
from dotenv import load_dotenv
from app.agents.supply_tool import SupplierAnalysisTool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    verbose=True,
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Agent Tanımı
supply_chain_agent = Agent(
    role='Operasyon ve Tedarik Zinciri Danışmanı',
    goal='{product} ürünü için hammadde ihtiyaçlarını belirlemek ve en uygun firmayı (A, B, C) önermek.',
    backstory="""Sen bir KOBİ operasyon uzmanısın. Hangi süt ürünü için hangi hammaddelerin 
    (süt, maya, tuz, kültür, paketleme vb.) gerektiğini çok iyi bilirsin. 
    Stok durumuna ve satış tahminine bakarak, işletme kârını maksimize edecek firmayı seçersin.""",
    tools=[SupplierAnalysisTool()],
    llm=llm_model,
    verbose=True
)


supply_task = Task(
    description=(
        "1. Oracle'dan gelen {product} tahminine ve mevcut {current_stock} miktarına bak.\n"
        "2. {product} üretimi için gereken hammaddeleri (Süt, Maya, Kültür vb.) genel uzmanlık bilginle listele.\n"
        "3. Stok yetersizse, hangi hammaddenin hangi firmadan (A, B, C) alınması gerektiğini açıkla."
    ),
    expected_output="{product} için hammadde listesi ve stratejik tedarik planı raporu.",
    agent=supply_chain_agent
)