"""
Bootstrap the model artifacts the backend needs to run locally.

The real artifacts (models/*.pkl) are gitignored and produced by
notebooks/Untitled.ipynb, which requires data/train.csv and
data/transactions.csv from the Kaggle competition. Those two CSVs are not in
this repo, so this script stands in for them: it synthesises a train/transactions
pair from the real stores.csv / oil.csv / holidays_events.csv, then runs the
*same* feature engineering and training steps as the notebook and dumps the
artifacts model_loader.py looks for.

The resulting models are structurally identical to production ones but are
trained on synthetic sales, so their accuracy numbers are NOT the numbers in
README.md. Use this only to exercise the API and dashboard end to end.

    python scripts/bootstrap_dev_models.py
"""

import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import LabelEncoder, StandardScaler

import lightgbm as lgb
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"

# Matches the notebook's FEATURES list / models/features.json
FEATURES = [
    "onpromotion", "dcoilwtico", "transactions",
    "is_holiday", "year", "month", "day",
    "dayofweek", "weekofyear", "quarter", "is_weekend",
    "cluster", "type_enc", "family_enc",
    "lag_7", "lag_14", "lag_28",
    "rolling_7_mean", "rolling_14_mean", "rolling_7_std",
]
TARGET = "sales"

# The 10 families the frontend's Forecast page offers
FAMILIES = [
    "GROCERY I", "BEVERAGES", "PRODUCE", "CLEANING", "DAIRY",
    "BREAD/BAKERY", "POULTRY", "MEATS", "PERSONAL CARE", "DELI",
]

START, END = "2016-01-01", "2017-08-15"
RNG = np.random.default_rng(42)


# ── Synthetic sales / transactions ──────────────────────────────────────────
def synthesize(stores, oil, holidays):
    dates = pd.date_range(START, END, freq="D")
    holiday_dates = set(holidays.loc[~holidays["transferred"].astype(bool), "date"])

    oil_series = (
        oil.set_index("date")["dcoilwtico"]
        .reindex(dates).ffill().bfill()
    )

    # Per-store daily transactions: scale with cluster, weekly seasonality
    trans_rows = []
    store_scale = {}
    for _, s in stores.iterrows():
        scale = 800 + 120 * s["cluster"] + RNG.normal(0, 150)
        store_scale[s["store_nbr"]] = max(scale, 300)
        dow = dates.dayofweek.to_numpy()
        weekly = 1.0 + 0.25 * (dow >= 5) + 0.05 * (dow == 4)
        t = store_scale[s["store_nbr"]] * weekly * RNG.normal(1.0, 0.08, len(dates))
        trans_rows.append(pd.DataFrame({
            "date": dates,
            "store_nbr": s["store_nbr"],
            "transactions": np.clip(t, 0, None).round(),
        }))
    transactions = pd.concat(trans_rows, ignore_index=True)

    # Per family: base level and promo sensitivity
    fam_base = {f: b for f, b in zip(FAMILIES, [2400, 1800, 1500, 700, 900, 800, 500, 600, 450, 350])}
    fam_promo = {f: p for f, p in zip(FAMILIES, [0.35, 0.30, 0.15, 0.40, 0.20, 0.18, 0.25, 0.22, 0.45, 0.20])}

    doy = dates.dayofyear.to_numpy()
    dow = dates.dayofweek.to_numpy()
    t_idx = np.arange(len(dates))
    is_hol = np.isin(dates, list(holiday_dates)).astype(int)
    oil_norm = (oil_series.to_numpy() - oil_series.mean()) / oil_series.std()

    rows = []
    for _, s in stores.iterrows():
        store_mult = store_scale[s["store_nbr"]] / 1200.0
        for fam in FAMILIES:
            promo = RNG.binomial(1, 0.12, len(dates)) * RNG.integers(1, 40, len(dates))
            base = fam_base[fam] * store_mult
            signal = (
                base
                * (1 + 0.10 * np.sin(2 * np.pi * doy / 365.25))      # yearly season
                * (1 + 0.18 * (dow >= 5) - 0.06 * (dow == 1))        # weekly season
                * (1 + 0.00012 * t_idx)                              # slow growth
                * (1 + fam_promo[fam] * (promo > 0))                 # promo lift
                * (1 + 0.12 * is_hol)                                # holiday lift
                * (1 - 0.04 * oil_norm)                              # oil headwind
                * RNG.normal(1.0, 0.10, len(dates))                  # noise
            )
            rows.append(pd.DataFrame({
                "date": dates,
                "store_nbr": s["store_nbr"],
                "family": fam,
                "sales": np.clip(signal, 0, None).round(3),
                "onpromotion": promo,
            }))

    train = pd.concat(rows, ignore_index=True)
    return train, transactions


# ── Notebook feature engineering (Section 2) ────────────────────────────────
def engineer(train, stores, oil, holidays, transactions):
    df = train.merge(stores, on="store_nbr", how="left")
    df = df.merge(oil, on="date", how="left")
    df = df.merge(transactions, on=["date", "store_nbr"], how="left")

    holiday_dates = set(holidays.loc[~holidays["transferred"].astype(bool), "date"])
    df["is_holiday"] = df["date"].isin(holiday_dates).astype(int)

    df["dcoilwtico"] = df["dcoilwtico"].ffill().bfill()

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["dayofweek"] = df["date"].dt.dayofweek
    df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)
    df["quarter"] = df["date"].dt.quarter
    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)

    df = df.sort_values(["store_nbr", "family", "date"])
    g = df.groupby(["store_nbr", "family"])["sales"]
    df["lag_7"] = g.shift(7)
    df["lag_14"] = g.shift(14)
    df["lag_28"] = g.shift(28)
    df["rolling_7_mean"] = g.transform(lambda x: x.shift(1).rolling(7).mean())
    df["rolling_14_mean"] = g.transform(lambda x: x.shift(1).rolling(14).mean())
    df["rolling_7_std"] = g.transform(lambda x: x.shift(1).rolling(7).std())

    le_family, le_type = LabelEncoder(), LabelEncoder()
    df["family_enc"] = le_family.fit_transform(df["family"])
    df["type_enc"] = le_type.fit_transform(df["type"])

    df_clean = df.dropna(subset=FEATURES + [TARGET]).reset_index(drop=True)
    return df_clean, le_family, le_type


def evaluate(name, y_true, y_pred):
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    mape = float(np.mean(np.abs((y_true - y_pred) / np.where(y_true == 0, 1, y_true))) * 100)
    print(f"   {name:<10} RMSE {rmse:9.2f} | MAE {mae:9.2f} | MAPE {mape:6.2f}%")
    return {"rmse": rmse, "mae": mae, "mape": mape}


def main():
    for f in ("stores.csv", "oil.csv", "holidays_events.csv"):
        if not (DATA_DIR / f).exists():
            raise SystemExit(f"Missing required file: data/{f}")

    stores = pd.read_csv(DATA_DIR / "stores.csv")
    oil = pd.read_csv(DATA_DIR / "oil.csv", parse_dates=["date"])
    holidays = pd.read_csv(DATA_DIR / "holidays_events.csv", parse_dates=["date"])

    print("Synthesising sales + transactions ...")
    train, transactions = synthesize(stores, oil, holidays)
    print(f"   train {train.shape} | transactions {transactions.shape}")

    print("Engineering features ...")
    df_clean, le_family, le_type = engineer(train, stores, oil, holidays, transactions)
    print(f"   usable rows {df_clean.shape}")

    # Train / test split: last 90 days held out (notebook Section 3)
    split_date = df_clean["date"].max() - pd.Timedelta(days=90)
    tr = df_clean[df_clean["date"] <= split_date]
    te = df_clean[df_clean["date"] > split_date]
    X_train, y_train = tr[FEATURES], tr[TARGET]
    X_test, y_test = te[FEATURES], te[TARGET]
    print(f"   train {len(X_train):,} | test {len(X_test):,}")

    print("Training forecasters ...")
    xgb_model = xgb.XGBRegressor(
        n_estimators=400, learning_rate=0.05, max_depth=8,
        subsample=0.8, colsample_bytree=0.8, random_state=42,
        n_jobs=-1, tree_method="hist",
    )
    xgb_model.fit(X_train, y_train)

    lgb_model = lgb.LGBMRegressor(
        n_estimators=400, learning_rate=0.05, num_leaves=64,
        subsample=0.8, colsample_bytree=0.8, random_state=42,
        n_jobs=-1, verbose=-1,
    )
    lgb_model.fit(X_train, y_train)

    metrics = {
        "XGBoost": evaluate("XGBoost", y_test.values, xgb_model.predict(X_test)),
        "LightGBM": evaluate("LightGBM", y_test.values, lgb_model.predict(X_test)),
    }

    # Store-level segmentation (notebook Section 5)
    print("Training segmentation ...")
    store_features = df_clean.groupby("store_nbr").agg(
        total_sales=("sales", "sum"),
        avg_sales=("sales", "mean"),
        std_sales=("sales", "std"),
        total_promo=("onpromotion", "sum"),
        avg_oil=("dcoilwtico", "mean"),
        avg_trans=("transactions", "mean"),
        holiday_count=("is_holiday", "sum"),
        unique_families=("family", "nunique"),
    ).reset_index()

    # NOTE: predict.py/segment feeds RAW (unscaled) store features straight to
    # kmeans/gmm, so these are fit on raw values to match how they are served.
    X_seg = store_features.drop("store_nbr", axis=1).to_numpy()
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10).fit(X_seg)
    gmm = GaussianMixture(n_components=4, random_state=42).fit(X_seg)

    # scaler.pkl is fit on the 8 SEGMENTATION features, exactly as the notebook
    # does. This matters: _build_feature_array_from_request() in predict.py calls
    # scaler.transform() on a 20-feature forecast vector and swallows the
    # resulting ValueError, so the forecasters correctly receive raw features --
    # which is what they were trained on. Fitting this scaler on the 20 forecast
    # features instead would make that transform succeed and silently corrupt
    # every prediction.
    scaler = StandardScaler().fit(X_seg)

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(xgb_model, MODEL_DIR / "xgboost_model.pkl")
    joblib.dump(lgb_model, MODEL_DIR / "lgbm_model.pkl")
    joblib.dump(kmeans, MODEL_DIR / "kmeans_model.pkl")
    joblib.dump(gmm, MODEL_DIR / "gmm_model.pkl")
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
    joblib.dump(le_family, MODEL_DIR / "le_family.pkl")
    joblib.dump(le_type, MODEL_DIR / "le_type.pkl")

    with open(MODEL_DIR / "features.json", "w", encoding="utf-8") as f:
        json.dump(FEATURES, f)

    # model_loader.py looks for models/training_sample.csv for /drift and
    # /explain (SHAP background data).
    sample = df_clean[["store_nbr", "family", "date"] + FEATURES + [TARGET]].sample(
        n=min(20000, len(df_clean)), random_state=42
    )
    sample.to_csv(MODEL_DIR / "training_sample.csv", index=False)

    with open(MODEL_DIR / "metrics_summary.json", encoding="utf-8") as f:
        summary = json.load(f)
    summary["dev_bootstrap_metrics"] = metrics
    summary["dev_bootstrap_note"] = (
        "Artifacts in this folder were generated by scripts/bootstrap_dev_models.py "
        "on synthetic sales data. The top-level XGBoost/LightGBM/ARIMA metrics are "
        "the original notebook results and do not describe these .pkl files."
    )
    with open(MODEL_DIR / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nWrote to models/:")
    for name in sorted(os.listdir(MODEL_DIR)):
        kb = (MODEL_DIR / name).stat().st_size / 1024
        print(f"   {name:<28} {kb:9.1f} KB")


if __name__ == "__main__":
    main()
