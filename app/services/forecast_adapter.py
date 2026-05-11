import joblib
import pandas as pd
import os
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
MODEL_PATH = os.path.join(project_root, "ml_module", "exports", "team299_lgbm_final.pkl")


if os.path.exists(MODEL_PATH):
    model_pack = joblib.load(MODEL_PATH)
    model = model_pack.get("model")
    scaler = model_pack.get("scaler")
    ohe = model_pack.get("ohe")
    features = model_pack.get("features")
    mapping = model_pack.get("mapping")

    print(f"Model components loaded. Expected features: {len(features)}")
else:
    model = None
    print("Model not found at:", {MODEL_PATH})


def predict_demand_with_oracle(product_name: str, recent_sales_7d: int, recent_sales_30d: int) -> int:
    if model is None:
        monthly_weekly_avg = recent_sales_30d / 4 if recent_sales_30d > 0 else 0
        momentum_bonus = max(recent_sales_7d - monthly_weekly_avg, 0)
        predicted = int(round(monthly_weekly_avg + (momentum_bonus * 0.8)))
        return max(0, predicted)

    try:
        now = datetime.now()
        data = {
            "month": now.month,
            "day_of_month": now.day,
            "day_of_year": now.timetuple().tm_yday,
            "week_of_year": now.isocalendar()[1],
            "day_of_week": now.weekday(),
            "year": now.year,
            "is_weekend": 1 if now.weekday() >= 5 else 0,
            "is_month_start": 1 if now.day == 1 else 0,
            "is_month_end": 1 if (now.day >= 28) else 0,
            "sales_lag_1": recent_sales_7d / 7,
            "sales_lag_7": recent_sales_7d,
            "sales_lag_30": recent_sales_30d,
            "sales_roll_mean_7": recent_sales_7d / 7,
            "Product Name": product_name
        }

        input_df = pd.DataFrame([data])

        ohe_data = ohe.transform(input_df[['Product Name']])
        ohe_cols = ohe.get_feature_names_out(['Product Name'])
        ohe_df = pd.DataFrame(ohe_data, columns=ohe_cols, index=input_df.index)

        final_df = pd.concat([input_df.drop(["Product Name"], axis=1), ohe_df], axis=1)

        for col in features:
            if col not in final_df.columns:
                final_df[col] = 0

        final_df = final_df[features]

        scaled_data = scaler.transform(final_df)

        prediction = model.predict(scaled_data)
        return max(0, int(round(prediction[0])))

    except Exception as e:
        print("Prediction logic error:", {e})
        return int(recent_sales_30d / 4)