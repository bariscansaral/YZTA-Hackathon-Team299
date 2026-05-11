import os


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
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return fallback_text

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        prompt = f"""
You are a retail campaign recommendation assistant.

Product: {product_name}
Recommended action: {action}
Reason: {reason_code}
Current stock: {current_stock}
Predicted demand: {predicted_demand}
Discount: %{suggested_discount_percent}
Campaign type: {campaign_type}

Explain this recommendation in 2 short business sentences.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a business analytics assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception:
        return fallback_text