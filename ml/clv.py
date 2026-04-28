import os
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
import logging

logger = logging.getLogger("customeriq.ml.clv")

# ── Paths ─────────────────────────────────────────────────────
_ROOT = os.path.join(os.path.dirname(__file__), "..", "models")
CLV_MODEL_PATH = os.path.join(_ROOT, "clv_model.joblib")

FEATURE_COLS = [
    "age", "gender", "tenure", "balance",
    "num_products", "has_credit_card",
    "is_active_member", "estimated_salary",
]

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    le = LabelEncoder()
    # Fill numeric NaNs and encode gender
    df["gender"] = le.fit_transform(df["gender"].astype(str))
    return df[FEATURE_COLS]

def calculate_target(df: pd.DataFrame) -> pd.Series:
    """
    Define CLV as a composite score of Tenure, Balance, and Salary.
    Formula: (Balance * 0.4) + (EstimatedSalary * 0.1 * Tenure / 10)
    This provides a continuous dollar-value target for regression.
    """
    return (df["balance"] * 0.4) + (df["estimated_salary"] * 0.1 * (df["tenure"] + 1) / 10)

def train_clv_model(df: pd.DataFrame) -> dict:
    """Train XGBoost Regressor to predict Customer Lifetime Value."""
    os.makedirs(_ROOT, exist_ok=True)

    X = prepare_features(df)
    y = calculate_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        objective='reg:squarederror',
        random_state=42
    )
    
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    joblib.dump(model, CLV_MODEL_PATH)
    logger.info(f"CLV model trained — MAE: {mae:.2f}, R2: {r2:.4f}")

    return {
        "mae": round(float(mae), 2),
        "r2": round(float(r2), 4),
        "avg_clv": round(float(y.mean()), 2)
    }

def predict_clv(df: pd.DataFrame) -> pd.DataFrame:
    """Predict future value for a set of customers."""
    if not os.path.exists(CLV_MODEL_PATH):
        raise FileNotFoundError("CLV model not trained. Call train_clv_model first.")
    
    model = joblib.load(CLV_MODEL_PATH)
    X = prepare_features(df)
    
    out = df[["customer_id"]].copy()
    out["predicted_clv"] = model.predict(X).round(2)
    
    # Tiering based on predicted value
    q_high = out["predicted_clv"].quantile(0.75)
    q_low = out["predicted_clv"].quantile(0.25)
    
    def get_tier(val):
        if val >= q_high: return "High Value"
        if val >= q_low: return "Medium Value"
        return "Low Value"
        
    out["value_tier"] = out["predicted_clv"].apply(get_tier)
    return out

def is_clv_trained() -> bool:
    return os.path.exists(CLV_MODEL_PATH)
