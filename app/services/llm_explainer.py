import os
import google.generativeai as genai

def generate_llm_explanation(
    product_name: str,
    action: str,
    reason_code: str,
    current_stock: int,
    predicted_demand: int,
    suggested_discount_percent: int,
    campaign_type: str,
    fallback_text: str,
) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return fallback_text

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.1-flash-lite")


        prompt = f"""Sen kıdemli bir perakende analistisin. 
        SADECE aşağıdaki verileri kullanarak profesyonel bir özet yaz.

        VERİLER:
        Ürün: {product_name}
        Mevcut Stok: {current_stock}
        Tahmin Edilen Talep: {predicted_demand}
        Önerilen Aksiyon: {action}
        Neden Kodu: {reason_code}
        Kampanya: %{suggested_discount_percent} indirim ({campaign_type})

        KURALLAR:
        1. Mevcut stok olan {current_stock} ile tahmini talep olan {predicted_demand} rakamlarını KESİNLİKLE kullan.
        2. Başka yerden sayı uydurma.
        3. Maksimum 4 cümle.
        """

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Explainer Hatası: {e}")
        return fallback_text