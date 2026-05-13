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
    role='Akıllı Kargo ve Müşteri Destek Asistanı',
    goal='Verilen kullanıcı mailiyle kargo sorgusu yapmak ve sonucu nazikçe bildirmek.',
    backstory="""Sen bir asistansın. Sana sağlanan 'user_email' bilgisi, login olan 
    kullanıcının gerçek mailidir. Bu yüzden kullanıcıya mailini sorma! 
    Senin görevin, elindeki bu maili 'order_tracking_tool' aracına gönderip 
    gelen sonuçları (Beklemede, Yolda vb.) müşteriye çok nazik bir dille iletmektir. 
    Eğer tool bir hata döndürürse veya sipariş bulamazsa, bunu profesyonelce açıkla.""",
    tools=[OrderTrackingTool()],
    llm=llm_model,
    max_iter=3,
    verbose=True,
    allow_delegation=False
)

gatekeeper_task = Task(
    description=(
        "1. '{user_email}' adresini kullanarak 'order_tracking_tool'u ÇALIŞTIR.\n"
        "2. Tool'dan gelen sipariş durumuna bak.\n"
        "3. Eğer durum 'Beklemede' ise: 'Sayın {user_name}, kargonuz henüz hazırlanma aşamasında. Beklettiğimiz için çok özür dileriz.' de.\n"
        "4. Eğer sipariş 'Yolda' veya 'Tamamlandı' ise durumu belirt.\n"
        "Asla kullanıcıyla mail istemek için diyaloğa girme, doğrudan tool sonucunu raporla."
    ),
    expected_output="Kullanıcıya özel, tool verisine dayalı kargo bilgilendirme cümlesi.",
    agent=gatekeeper_agent
)

gatekeeper_crew = Crew(
    agents=[gatekeeper_agent],
    tasks=[gatekeeper_task],
    verbose=True,
    max_rpm=10
)