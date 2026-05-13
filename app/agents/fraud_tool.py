from crewai_tools import tool
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.fraud_agent import build_fraud_request_from_order_id, analyze_fraud_risk

@tool("fraud_analysis_tool")
def fraud_analysis_tool(order_id: int):
    """Belirli bir siparişin sahtecilik (fraud) riskini analiz eder ve detaylı rapor döner."""
    db = SessionLocal()
    try:
        payload = build_fraud_request_from_order_id(db, order_id)
        report = analyze_fraud_risk(payload)
        return f"Risk Seviyesi: {report.fraud_risk_level}, Skor: {report.fraud_score}, Karar: {report.decision}, Nedenler: {report.reason_codes}"
    finally:
        db.close()