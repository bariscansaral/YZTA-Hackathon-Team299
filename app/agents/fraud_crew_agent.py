from crewai import Agent, Task, Crew, Process
from app.agents.fraud_tool import fraud_analysis_tool
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

llm_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    verbose=True,
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

fraud_inspector_agent = Agent(
    role='Güvenlik ve Sahtecilik Denetçisi',
    goal='Siparişlerdeki şüpheli aktiviteleri tespit etmek ve işletmeyi korumak',
    backstory="""Sen bir dijital adli tıp uzmanısın. Sipariş miktarları, kullanıcı geçmişi 
    ve ödeme alışkanlıklarındaki anormallikleri saptamakta ustasın. Karmaşık verileri 
    inceleyip 'Bu sipariş neden riskli?' sorusuna mantıklı açıklamalar getirirsin.""",
    tools=[fraud_analysis_tool],
    verbose=True,
    llm=llm_model,
    allow_delegation=False
)

fraud_task = Task(
    description=(
        "Sistem genelindeki tüm kullanıcı hareketlerini ve siparişleri analiz et.\n"
        "1. Birden fazla hesaptan gelen şüpheli siparişleri kontrol et.\n"
        "2. Stok seviyeleri ile sipariş adetleri arasındaki tutarsızlıkları bul.\n"
        "3. Yüksek tutarlı veya anormal sıklıktaki işlemleri raporla.\n"
        "DİKKAT: Analizini tek bir kullanıcıyla sınırlama, tüm veritabanı genelinde bir risk raporu hazırla."
    ),
    expected_output="Tüm sistemi kapsayan, riskli kullanıcıları ve şüpheli işlemleri listeleyen güvenlik raporu.",
    agent=fraud_inspector_agent
)

fraud_crew = Crew(
    agents=[fraud_inspector_agent],
    tasks=[fraud_task],
    process=Process.sequential,
    verbose=True,
    max_rpm=10
)