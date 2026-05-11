import pickle
import pandas as pd
import os
import numpy as np
from datetime import datetime
from crewai.tools import tool


MODEL_PATH = "../../ml_module/exports/team299_lightgbm_final.pkl"
print(f"DEBUG: Mevcut çalışma dizini: {os.getcwd()}")
print(f"DEBUG: Aranan Model Yolu: {MODEL_PATH}")

try:
    with open(MODEL_PATH, "rb") as f:
        model_pack = pickle.load(f)
    model = model_pack['model']
    scaler = model_pack['scaler']
    ohe = model_pack['ohe']
    features = model_pack['features']

except Exception as e:
    print(f"Model yüklenirken hata: {e}")


@tool("sales_forecast_tool")
def sales_forecast_tool(product_name: str, forecast_date: str):
    """
        Belirli bir ürün ve tarih için satış tahmini yapar.
        Girdi olarak ürün adını ve tarihi alır, tahmin edilen satış miktarını döner.
    """
    try:
        date_obj = datetime.strptime(forecast_date, '%Y-%m-%d')

        data = {
            'month': [date_obj.month],
            'day_of_month': [date_obj.day],
            'day_of_year': [date_obj.timetuple().tm_yday],
            'week_of_year': [int(date_obj.isocalendar()[1])],
            'day_of_week': [date_obj.weekday()],
            'year': [date_obj.year],
            'is_weekend': [1 if date_obj.weekday() >= 5 else 0],
            'is_month_start': [1 if date_obj.day == 1 else 0],
            'is_month_end': [1 if (date_obj.day == pd.Period(date_obj, freq='D').days_in_month) else 0]
        }

        df = pd.DataFrame(data)


        ohe_out = ohe.transform([[product_name]])
        ohe_cols = ohe.get_feature_names_out(['Product Name'])
        df_ohe = pd.DataFrame(ohe_out, columns=ohe_cols)


        X_final = pd.concat([df, df_ohe], axis=1)


        for col in features:
            if col not in X_final.columns:
                X_final[col] = 0

        X_final = X_final[features]


        X_scaled = scaler.transform(X_final)
        prediction = model.predict(X_scaled)

        return f"{product_name} için {forecast_date} tarihinde beklenen satış: {round(prediction[0], 2)} adet."
    except Exception as e:
        return f"Tahmin sırasında hata oluştu: {str(e)}"

