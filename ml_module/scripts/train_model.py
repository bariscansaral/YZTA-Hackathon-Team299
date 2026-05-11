import pandas as pd
import numpy as np
import random
import os
import pickle
import warnings
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

def extract_temporal_features(df):
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['day_of_month'] = df['date'].dt.day
    df['day_of_year'] = df['date'].dt.dayofyear
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
    df['day_of_week'] = df['date'].dt.dayofweek
    df['year'] = df['date'].dt.year
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
    df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
    return df

def apply_window_logic(df):
    df = df.sort_values(by=['item', 'date'])
    df['sales_lag_1'] = df.groupby('item')['sales'].shift(1)
    df['sales_lag_7'] = df.groupby('item')['sales'].shift(7)
    df['sales_lag_30'] = df.groupby('item')['sales'].shift(30)
    df['sales_roll_mean_7'] = df.groupby('item')['sales'].transform(lambda x: x.shift(1).rolling(window=7).mean())
    return df.dropna()

def main():
    print("Team 299 - Model Training Pipeline Başladı...")

    current_dir = os.path.dirname(os.path.abspath(__file__)) # scripts klasörü
    data_path = os.path.abspath(os.path.join(current_dir, "../data/retail_sales_kaggle/train.csv"))
    export_path = os.path.abspath(os.path.join(current_dir, "../exports/team299_lgbm_final.pkl"))

    print(f"Veri aranıyor: {data_path}")

    try:
        df = pd.read_csv(data_path)
    except Exception as e:
        print(f"HATA: Veri dosyası bulunamadı! \nBaktığım yer: {data_path}")
        return

    top_30_ids = df.groupby('item')['sales'].sum().nlargest(30).index.tolist()
    df = df[df['item'].isin(top_30_ids)].copy()

    products = [
        "Kars Kaşarı", "Erzincan Tulumu", "İzmir Tulumu", "Çeçil Peyniri", "Süzme Yoğurt",
        "Manda Yoğurdu", "Meyveli Yoğurt", "Keçi Yoğurdu", "Tam Yağlı Süt", "Yarım Yağlı Süt",
        "Laktozsuz Süt", "Yayık Tereyağı", "Vakfıkebir Tereyağı", "Köy Tereyağı", "Tuzlu Tereyağı",
        "Maraş Dondurması", "Vanilyalı Dondurma", "Kakaolu Dondurma", "Sade Yağ", "Süt Yağı",
        "Naneli Ayran", "Sade Ayran", "Fesleğenli Ayran", "Lor Peyniri", "Köy Peyniri",
        "Süzme Peynir", "Çökelek", "Kefir", "Pastörize Ayran", "Kımız"
    ]
    random.seed(42)
    shuffled = products.copy()
    random.shuffle(shuffled)
    mapping_dict = dict(zip(top_30_ids, shuffled))
    df['Product Name'] = df['item'].map(mapping_dict)

    df = extract_temporal_features(df)
    df = apply_window_logic(df)

    train_data = df[df['date'] < '2017-07-01']
    val_data = df[df['date'] >= '2017-07-01']

    X_train = train_data.drop(['sales', 'date'], axis=1)
    y_train = train_data['sales']
    X_val = val_data.drop(['sales', 'date'], axis=1)
    y_val = val_data['sales']

    ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    ohe_train = ohe.fit_transform(X_train[['Product Name']])
    ohe_val = ohe.transform(X_val[['Product Name']])

    ohe_cols = ohe.get_feature_names_out(['Product Name'])
    X_train_final = pd.concat([X_train.drop(['item', 'Product Name'], axis=1).reset_index(drop=True),
                               pd.DataFrame(ohe_train, columns=ohe_cols)], axis=1)
    X_val_final = pd.concat([X_val.drop(['item', 'Product Name'], axis=1).reset_index(drop=True),
                             pd.DataFrame(ohe_val, columns=ohe_cols)], axis=1)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_final)
    X_val_scaled = scaler.transform(X_val_final)

    model = LGBMRegressor(n_estimators=500, learning_rate=0.05, random_state=42, verbose=-1)
    model.fit(X_train_scaled, y_train)

    preds = model.predict(X_val_scaled)
    rmse = np.sqrt(mean_squared_error(y_val, preds))
    print(f"Skorlar: R2: {r2_score(y_val, preds):.4f} | MAE: {mean_absolute_error(y_val, preds):.4f} | RMSE: {rmse:.4f}")

    model_bundle = {
        "model": model, "ohe": ohe, "scaler": scaler,
        "features": list(X_train_final.columns), "mapping": mapping_dict
    }

    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, 'wb') as f:
        pickle.dump(model_bundle, f)

    print("Model başarıyla export edildi: ml_module/exports/team299_lgbm_final.pkl")

if __name__ == "__main__":
    main()