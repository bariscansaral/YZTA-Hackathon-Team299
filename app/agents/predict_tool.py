import pickle
import pandas as pd
import os
import numpy as np
from datetime import datetime
from crewai_tools import tool


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ml_module", "exports", "team299_lgbm_final.pkl")
DATA_PATH = os.path.join(BASE_DIR, "ml_module", "data", "retail_sales_kaggle", "train.csv")


try:
    with open(MODEL_PATH, "rb") as f:
        model_pack = pickle.load(f)
    model = model_pack['model']
    scaler = model_pack['scaler']
    ohe = model_pack['ohe']
    features = model_pack['features']
    mapping_dict = model_pack['mapping']
except Exception as e:
    print(f"HATA: Model veya mapping yüklenemedi: {e}")


@tool("sales_forecast_tool")
def sales_forecast_tool(product_name: str, forecast_date: str):
    """
    Belirli bir ürün ve tarih için satış tahmini yapar.
    Ürünün geçmiş satış verilerini (lag) otomatik hesaplar ve modele besler.
    """
    try:
        date_obj = datetime.strptime(forecast_date, '%Y-%m-%d')


        reverse_mapping = {v: k for k, v in mapping_dict.items()}
        target_item_id = reverse_mapping.get(product_name)

        if target_item_id is None:
            return f"Hata: '{product_name}' ürünü geçerli ürün listesinde bulunamadı."

        df_raw = pd.read_csv(DATA_PATH)
        item_sales = df_raw[df_raw['item'] == target_item_id].sort_values('date')['sales'].tolist()

        if not item_sales:
            return f"Hata: '{product_name}' için geçmiş satış verisi bulunamadı."

        last_val = item_sales[-1]
        lag_1 = item_sales[-1] if len(item_sales) >= 1 else last_val
        lag_7 = item_sales[-7] if len(item_sales) >= 7 else last_val
        lag_30 = item_sales[-30] if len(item_sales) >= 30 else last_val
        roll_mean_7 = np.mean(item_sales[-7:]) if len(item_sales) >= 7 else last_val

        data = {
            'month': [date_obj.month],
            'day_of_month': [date_obj.day],
            'day_of_year': [date_obj.timetuple().tm_yday],
            'week_of_year': [int(date_obj.isocalendar()[1])],
            'day_of_week': [date_obj.weekday()],
            'year': [date_obj.year],
            'is_weekend': [1 if date_obj.weekday() >= 5 else 0],
            'is_month_start': [1 if date_obj.day == 1 else 0],
            'is_month_end': [1 if (date_obj.day == pd.Period(date_obj, freq='D').days_in_month) else 0],
            'sales_lag_1': [float(lag_1)],
            'sales_lag_7': [float(lag_7)],
            'sales_lag_30': [float(lag_30)],
            'sales_roll_mean_7': [float(roll_mean_7)]
        }
        X_df = pd.DataFrame(data)

        product_df = pd.DataFrame([[product_name]], columns=['Product Name'])
        ohe_out = ohe.transform(product_df)
        ohe_cols = ohe.get_feature_names_out(['Product Name'])
        df_ohe = pd.DataFrame(ohe_out, columns=ohe_cols)

        X_final = pd.concat([X_df, df_ohe], axis=1)

        for col in features:
            if col not in X_final.columns:
                X_final[col] = 0
        X_final = X_final[features]

        X_scaled = scaler.transform(X_final)
        X_scaled_df = pd.DataFrame(X_scaled, columns=features)

        prediction = model.predict(X_scaled_df)
        res = round(prediction[0], 2)

        return (
            f"'{product_name}' için {forecast_date} tarihindeki tahmin: {res} adet.\n"
            f"Analiz Detayı: Son satış: {lag_1}, 7 günlük ortalama trend: {round(roll_mean_7, 2)}."
        )

    except Exception as e:
        return f"Tahmin hatası: {str(e)}"