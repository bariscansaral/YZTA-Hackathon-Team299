from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app.schemas.retention import RetentionAnalyzeResponse
from app.services.retention_agent import RetentionAgent

router = APIRouter(prefix="/retention", tags=["Retention Agent"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/run-campaign", response_model=List[RetentionAnalyzeResponse])
def run_retention_campaign(db: Session = Depends(get_db)):
    agent = RetentionAgent(db)
    return agent.analyze_and_engage()