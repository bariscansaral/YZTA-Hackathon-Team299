import os
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from app.agents.predict_tool import sales_forecast_tool
from dotenv import load_dotenv
from app.agents.explanation_tool import strategic_explanation_tool


ROOT_DIR = os.getcwd()
MODEL_PATH = os.path.join(ROOT_DIR, "ml_module", "exports", "team299_lgbm_final.pkl")

load_dotenv()
os.environ["OTEL_SDK_DISABLED"] = "true" #OpenTelemetry

llm_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    verbose=True,
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

oracle_agent = Agent(
    role='Stratejik Satış Tahmincisi',
    goal='{product} ürünü için {date} tarihindeki satış tahminini raporla. Mevcut stok verisi: {current_stock}.', # Stok verisini buraya da gömdük
    backstory='Sen bir veri bilimcisisin. Sana verilen gerçek stok verisi olan {current_stock} rakamına sadık kalmalısın.',
    llm=llm_model,
    tools=[sales_forecast_tool, strategic_explanation_tool],
    verbose=True,
    allow_delegation=False
)

forecast_task = Task(
    description=(
        "1. sales_forecast_tool ile {product} için {date} tahmini rakamını bul.\n"
        "2. strategic_explanation_tool'u kullanırken ona gerçek stok miktarını ({current_stock}) da parametre olarak ver.\n"
        "3. Eğer tool sana yanlış bir stok (100 gibi) döndürürse, o kısmı raporunda GERÇEK STOK ({current_stock}) ile düzelt."
    ),
    expected_output="ML tahmini ve {current_stock} stok verisine dayalı rapor.",
    agent=oracle_agent
)

oracle_crew = Crew(
    agents=[oracle_agent],
    tasks=[forecast_task],
    process=Process.sequential,
    max_rpm=10
)
