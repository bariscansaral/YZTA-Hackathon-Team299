from crewai.tools import tool
import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
from app.services.llm_explainer import generate_llm_explanation

@tool("strategic_explanation_tool")
def strategic_explanation_tool(
    product_name: str,
    action: str,
    reason_code: str,
    current_stock: int,
    predicted_demand: int,
    suggested_discount_percent: int,
    campaign_type: str
) -> str:
    """
    Karmaşık satış ve stok verilerini insan diline, profesyonel bir iş özetine dönüştürür.
    Tahmin rakamları ve stok durumları arasındaki ilişkiyi açıklamak için kullanılır.
    """
    return generate_llm_explanation(
        product_name=product_name,
        action=action,
        reason_code=reason_code,
        current_stock=current_stock,
        predicted_demand=predicted_demand,
        suggested_discount_percent=suggested_discount_percent,
        campaign_type=campaign_type,
        fallback_text="Veriler analiz ediliyor, lütfen bekleyiniz."
    )