import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from predict_tool import sales_forecast_tool
from dotenv import load_dotenv


ROOT_DIR = os.getcwd()
MODEL_PATH = os.path.join(ROOT_DIR, "ml_module", "exports", "team299_lightgbm_final.pkl")

print(f"DEBUG: Kesin Yol: {MODEL_PATH}")

os.environ["GOOGLE_API_KEY"] = "AIzaSyBmsRYxupLSclJjynAzQ_nQ7dSPqtn8BuU"
os.environ["OTEL_SDK_DISABLED"] = "true" #OpenTelemetry
model_name="gemini-2.5-flash"

# Agent Tanımı
oracle_agent = Agent(
    role='Stratejik Satış Tahmincisi',
    goal='{product} ürünü için {date} tarihindeki satış tahminini raporla.',
    backstory='Sen bir veri bilimcisi ve satış stratejistisin.',
    llm=model_name,
    verbose=True,
    allow_delegation=False
)

# Görev Tanımı
forecast_task = Task(
    description="{product} ürünü için {date} tarihinde ne kadar satış beklediğimizi raporla.",
    expected_output="Ürün adı, tarih ve tahmin rakamını içeren profesyonel bir rapor.",
    agent=oracle_agent
)

# Crew Oluşturma
crew = Crew(
    agents=[oracle_agent],
    tasks=[forecast_task],
    process=Process.sequential
)

if __name__ == "__main__":
    result = crew.kickoff(inputs={
        'product': 'Tuzlu Tereyağı',
        'date': '2026-06-15'
    })

    print("\n\n########################")
    print("AGENT SONUCU:")
    print(result)