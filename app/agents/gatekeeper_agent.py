import os
from crewai import Agent, Task, Crew
from app.agents.auth_tool import AuthorityCheckTool
from app.agents.logistics_tool import OrderTrackingTool
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    verbose=True,
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

gatekeeper_agent = Agent(
    role='Akıllı Kurumsal Kapı Denetçisi ve Koordinatör',
    goal='Kullanıcının kimliğini doğrulayarak yetkisine göre operasyonel stratejileri veya kişisel kargo bilgilerini sunmak.',
    backstory="""Sen sistemin en üst düzey yöneticisisin. AuthorityCheckTool kullanarak gelen kişinin 
    ADMIN mi yoksa USER mı olduğunu anlarsın. ADMIN'lere şirketin tüm mutfak bilgilerini (tahmin, hammadde, strateji) 
    raporlarsın; USER'lara ise sadece kendi kargolarını ve onlara özel kampanyaları söylersin. 
    Veri gizliliği senin için kırmızı çizgidir.""",
    tools=[AuthorityCheckTool(), OrderTrackingTool()],
    llm=llm_model,
    verbose=True
)

gatekeeper_task = Task(
    description=(
        "1. Önce '{user_name}' kullanıcısının yetkisini 'AuthorityCheckTool' ile sorgula.\n"
        "2. EĞER YETKİ 'USER' İSE:\n"
        "   - SADECE 'OrderTrackingTool' kullan ve kargo durumunu öğren.\n"
        "   - Çıktıyı şu formatta ver ve BAŞKA HİÇBİR ŞEY YAZMA: 'Sayın [user_name], kargonuz [durum] aşamasındadır.'\n"
        "   - DİKKAT: USER için asla Oracle veya Supply agent'larını çağırma, analize devam etme.\n"
        "3. EĞER YETKİ 'ADMIN' İSE: 'Yönetici onayı alındı' notuyla analize devam et."
    ),
    expected_output="Eğer kullanıcı USER ise sadece tek cümlelik kargo bilgisi. ADMIN ise tüm rapor.",
    agent=gatekeeper_agent
)

gatekeeper_crew = Crew(
    agents=[gatekeeper_agent],
    tasks=[gatekeeper_task],
    verbose=True,
    max_rpm=10
)