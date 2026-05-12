import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from predict_tool import sales_forecast_tool
from dotenv import load_dotenv
from explanation_tool import strategic_explanation_tool


ROOT_DIR = os.getcwd()
MODEL_PATH = os.path.join(ROOT_DIR, "ml_module", "exports", "team299_lgbm_final.pkl")

load_dotenv()
os.environ["OTEL_SDK_DISABLED"] = "true" #OpenTelemetry
gemini_llm = LLM(
    model="gemini/gemini-3.1-flash-lite",
    api_key=os.environ.get("GOOGLE_API_KEY")
)

# Agent Tanımı
oracle_agent = Agent(
    role='Stratejik Satış Tahmincisi',
    goal='{product} ürünü için {date} tarihindeki satış tahminini raporla, Raporda mutlaka tooldan gelen sayısal veriyi kullan ve X gibi ifadeler bırakma strategic_explanation_tooldan gelen stratejik yorumu raporun sonuç kısmına aynen ekle.',
    backstory='Sen bir veri bilimcisi ve satış stratejistisin, tahmin yaparken sadece haftanın günlerine değil; resmi tatillere, '
              'dini bayramlara ve Anneler Günü gibi özel ticari dönemlere karşı aşırı duyarlısın, Rakamları bulduktan sonra strategic_explanation_tool kullanarak yönetici özeti hazırlarsın.',
    llm=gemini_llm,
    tools=[sales_forecast_tool,strategic_explanation_tool],
    verbose=True,
    allow_delegation=False
)

# Görev Tanımı
forecast_task = Task(
    description=(
        "{product} ürünü için {date} tarihinde satış tahmini yap. "
        "ÖNCE sales_forecast_tool ile {product} için {date} tarihindeki rakamı bul.\n"
        "2. BU RAKAMI AL VE MUTLAKA strategic_explanation_tool aracına gönder. Bu adımı atlama!\n"
        "3. BU ARACIN (strategic_explanation_tool) ÜRETTİĞİ profesyonel açıklamayı raporunun 'Stratejik Analiz' bölümüne kelimesi kelimesine ekle.\n"
        "4. Final raporunda hem ham tahmin rakamını (86.96 gibi) hem de bu tool'dan gelen resmi açıklamayı kullan."
    ),
    expected_output="predict_tool'dan gelen ML tahmini ve strategic_explanation_tool'dan gelen resmi analizi içeren tam rapor.",
    agent=oracle_agent
)

# Crew Oluşturma
crew = Crew(
    agents=[oracle_agent],
    tasks=[forecast_task],
    process=Process.sequential,
    rpm_limit=10
)

if __name__ == "__main__":
    result = crew.kickoff(inputs={
        'product': 'Tuzlu Tereyağı',
        'date': '2026-05-10'
    })

    print("\n\n########################")
    print("AGENT SONUCU:")
    print(result)