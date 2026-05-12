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

        prompt = f"""
                        Sen bir kıdemli perakende analistisin. Verilen verilere dayanarak kısa bir yönetici özeti yaz.

                        VERİLER:
                        - Ürün: {product_name}
                        - Mevcut Stok: {current_stock}
                        - Tahmin Edilen Talep: {predicted_demand}
                        - Önerilen Aksiyon: {action} (Neden: {reason_code})
                        - Kampanya: %{suggested_discount_percent} indirimli {campaign_type}

                        ANALİZ KURALLARI:
                        1. Mutlaka rakamları ({current_stock} vs {predicted_demand}) birbiriyle kıyasla.
                        2. {action} aksiyonunun neden mantıklı olduğunu {reason_code} koduna atıfta bulunarak açıkla.
                        3. {campaign_type} kampanyasının bu stok/talep dengesine etkisini yorumla.
                        4. Maksimum 5 profesyonel cümle kur.
                        """

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Explainer Hatası: {e}")
        return fallback_text