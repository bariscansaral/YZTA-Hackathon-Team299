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

fraud_check_task = Task(
    description="""
    Sistemdeki son siparişleri ve '{product_name}' ile ilgili yapılan işlem geçmişini incele. 
    1. Belirtilen order_id veya kullanıcı geçmişindeki anormallikleri tespit etmek için fraud_analysis_tool'u kullan.
    2. Sipariş tutarı, ürün adedi ve kullanıcı güven puanı arasındaki tutarsızlıkları 2 cümleyle raporla.
    3. Eğer yüksek riskli bir durum varsa, admin için acil eylem planı (bloklama veya manuel inceleme) öner.
    """,
    expected_output="""
    Siparişin risk skorunu, tespit edilen şüpheli örüntüleri ve alınması gereken 
    aksiyonu içeren 4 cümlelik güvenlik raporu.
    """,
    agent=fraud_inspector_agent
)

fraud_crew = Crew(
    agents=[fraud_inspector_agent],
    tasks=[fraud_check_task],
    process=Process.sequential,
    verbose=True,
    max_rpm=10
)