from crewai_tools import tool
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.fraud_agent import analyze_all_orders_for_fraud

@tool("fraud_analysis_tool")
def fraud_analysis_tool(order_id: int):
    """Belirli bir siparişin sahtecilik (fraud) riskini analiz eder ve detaylı rapor döner."""
    db = SessionLocal()
    try:
        report = analyze_all_orders_for_fraud(db)
        if not report:
            return "Sistemde şu an şüpheli veya riskli bir sipariş bulunamadı. Her şey yolunda."

        return str(report)  # Ajan bu listeyi alıp yorumlayacak
    finally:
        db.close()