from pydantic import BaseModel
from typing import List, Optional

class RetentionAnalyzeResponse(BaseModel):
    user_id: int
    days_since_last_order: Optional[int]
    status: str
    recommendation: str
    generated_message: str  # Müşteriye gidecek olan mesaj