import os
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest
from scipy.stats import ks_2samp
import optuna
import shap
import joblib
import logging
import mlflow
import mlflow.xgboost
from datetime import datetime

logger = logging.getLogger("customeriq.ml.churn")

# ── Paths & MLflow Config ─────────────────────────────────────
_ROOT = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(_ROOT, "churn_model.joblib")
EXPLAINER_PATH = os.path.join(_ROOT, "shap_explainer.joblib")
ANOMALY_MODEL_PATH = os.path.join(_ROOT, "anomaly_model.joblib")
TRAIN_STATS_PATH = os.path.join(_ROOT, "train_stats.joblib")

# Set local tracking URI
mlflow.set_tracking_uri(f"sqlite:///{os.path.join(_ROOT, 'mlflow.db')}")
mlflow.set_experiment("churn_prediction")

FEATURE_COLS = [
    "age", "gender", "tenure", "balance",
    "num_products", "has_credit_card",
    "is_active_member", "estimated_salary",
]

# ── In-memory singletons ──────────────────────────────────────
model = None
explainer = None


def load_model_if_exists():
    """Load persisted model + explainer from disk on startup."""
    global model, explainer
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            logger.info("✅ Churn model loaded from disk.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            
    if os.path.exists(EXPLAINER_PATH):
        try:
            explainer = joblib.load(EXPLAINER_PATH)
            logger.info("✅ SHAP explainer loaded from disk.")
        except Exception as e:
            logger.error(f"Failed to load explainer: {e}")


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    le = LabelEncoder()
    # Handle missing or non-string values during encoding
    if "gender" in df.columns:
        df["gender"] = le.fit_transform(df["gender"].astype(str))
    return df[FEATURE_COLS]


def run_optuna_study(X, y, n_trials=20):
    """Automated Hyperparameter Optimization via Bayesian Search."""
    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 400),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "random_state": 42,
            "eval_metric": "logloss",
        }
        model = XGBClassifier(**params)
        score = cross_val_score(model, X, y, cv=3, scoring="roc_auc").mean()
        return score

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)
    logger.info(f"Optuna Study Complete — Best AUC: {study.best_value:.4f}")
    return study.best_params


def detect_drift(current_df: pd.DataFrame) -> dict:
    """Detect statistical drift using Kolmogorov-Smirnov test against training distribution."""
    if not os.path.exists(TRAIN_STATS_PATH):
        return {"status": "no_baseline", "drift_detected": False}

    train_stats = joblib.load(TRAIN_STATS_PATH)
    X_curr = prepare_features(current_df)
    
    drift_report = {}
    drift_detected = False
    
    for col in FEATURE_COLS:
        # KS Test: p-value < 0.05 indicates different distributions
        stat, p_val = ks_2samp(train_stats[col], X_curr[col])
        drift_report[col] = {"p_value": round(p_val, 4), "drift": p_val < 0.05}
        if p_val < 0.05:
            drift_detected = True
            
    return {
        "drift_detected": drift_detected,
        "features": drift_report,
        "timestamp": datetime.now().isoformat()
    }


def detect_anomalies(df: pd.DataFrame) -> pd.Series:
    """Identify outliers using Isolation Forest."""
    if not os.path.exists(ANOMALY_MODEL_PATH):
        # Fallback train if missing
        X = prepare_features(df)
        iso = IsolationForest(contamination=0.05, random_state=42)
        iso.fit(X)
        joblib.dump(iso, ANOMALY_MODEL_PATH)
    else:
        iso = joblib.load(ANOMALY_MODEL_PATH)
        
    X = prepare_features(df)
    # -1 for anomaly, 1 for normal
    preds = iso.predict(X)
    return pd.Series(preds == -1)


def train_model(df: pd.DataFrame, params: dict = None, use_optuna: bool = False) -> dict:
    """Train XGBoost with optional AutoML tuning and drift baselining."""
    global model, explainer

    os.makedirs(_ROOT, exist_ok=True)

    X = prepare_features(df)
    y = df["exited"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Phase 2: Hyperparameter Optimization
    if use_optuna:
        logger.info("Starting Optuna AutoML study...")
        params = run_optuna_study(X_train, y_train)
    elif params is None:
        params = {
            "n_estimators": 200,
            "max_depth": 4,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "eval_metric": "logloss",
        }

    with mlflow.start_run(run_name=f"churn_train_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        model = XGBClassifier(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)

        # Log to MLflow
        mlflow.log_params(params)
        mlflow.log_metrics({
            "accuracy": accuracy,
            "roc_auc": roc_auc
        })
        
        # Log feature importance as a metric for comparison
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X_test)
        importance = np.abs(shap_vals).mean(axis=0)
        for i, col in enumerate(FEATURE_COLS):
            mlflow.log_metric(f"importance_{col}", importance[i])

        # Baseline for drift detection
        train_dist = X_train.to_dict(orient="list")
        joblib.dump(train_dist, TRAIN_STATS_PATH)
        
        # Train Anomaly Detection (Isolation Forest)
        iso = IsolationForest(contamination=0.05, random_state=42)
        iso.fit(X_train)
        joblib.dump(iso, ANOMALY_MODEL_PATH)

        # Save model and explainer locally and to MLflow
        joblib.dump(model, MODEL_PATH)
        joblib.dump(explainer, EXPLAINER_PATH)
        mlflow.log_artifact(MODEL_PATH)
        mlflow.log_artifact(EXPLAINER_PATH)
        mlflow.log_artifact(ANOMALY_MODEL_PATH)
        mlflow.log_artifact(TRAIN_STATS_PATH)
        
        # Tag the run
        mlflow.set_tag("version", "2.0-masterpiece")
        mlflow.set_tag("has_optuna", str(use_optuna))

        logger.info(f"Model trained & logged — accuracy={accuracy:.4f} roc_auc={roc_auc:.4f}")

    return {
        "accuracy": round(accuracy, 4),
        "roc_auc": round(roc_auc, 4),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "optuna_optimized": use_optuna,
        "run_id": mlflow.active_run().info.run_id if mlflow.active_run() else None
    }


def _json_safe(value):
    """Recursively coerce numpy/pandas types into JSON-serializable values."""
    import numpy as np
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            return value.item()
        except Exception:
            pass
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def get_model_runs():
    """Retrieve all historical MLflow runs for the experiment (JSON-safe)."""
    runs = mlflow.search_runs(experiment_names=["churn_prediction"])
    if runs is None or runs.empty:
        return []

    # Sort by start_time descending
    runs = runs.sort_values(by="start_time", ascending=False)
    return [_json_safe(r) for r in runs.to_dict(orient="records")]


def get_active_model_version() -> str:
    """Return the version tag of the most recent training run."""
    try:
        runs = mlflow.search_runs(experiment_names=["churn_prediction"])
        if runs is not None and not runs.empty:
            runs = runs.sort_values(by="start_time", ascending=False)
            version = runs.iloc[0].get("tags.version")
            if version:
                return str(version).strip('"')
    except Exception as e:
        logger.warning(f"Failed to resolve active model version: {e}")
    return "2.0-masterpiece"


def activate_model_version(run_id: str):
    """Roll back/activate a specific model version from an MLflow run."""
    global model, explainer

    run = mlflow.get_run(run_id)
    if run is None:
        return False

    try:
        # Download artifacts to a local temp dir (handles file:// and
        # cloud stores cross-platform via MLflow's artifact layer).
        artifact_dir = mlflow.artifacts.download_artifacts(run_id=run_id)
    except Exception as e:
        logger.error(f"Failed to download artifacts for run {run_id}: {e}")
        return False

    model_src = os.path.join(artifact_dir, "churn_model.joblib")
    explainer_src = os.path.join(artifact_dir, "shap_explainer.joblib")

    if os.path.exists(model_src):
        import shutil
        shutil.copy(model_src, MODEL_PATH)
        if os.path.exists(explainer_src):
            shutil.copy(explainer_src, EXPLAINER_PATH)

        # Reload singletons
        load_model_if_exists()
        return True
    return False


def predict_churn(df: pd.DataFrame) -> pd.DataFrame:
    global model
    if model is None:
        load_model_if_exists()
    if model is None:
        raise ValueError("Model not trained yet. Call POST /predict/train first.")

    X = prepare_features(df)
    out = df[["customer_id"]].copy()
    out["churn_probability"] = model.predict_proba(X)[:, 1].round(4)
    out["churn_prediction"] = model.predict(X)
    out["risk_level"] = pd.cut(
        out["churn_probability"],
        bins=[0, 0.3, 0.6, 1.0],
        labels=["Low", "Medium", "High"],
    )
    return out


def get_shap_values(df: pd.DataFrame) -> dict:
    """Dataset-level feature importance (Global)."""
    global explainer
    if explainer is None:
        load_model_if_exists()
    if explainer is None:
        raise ValueError("Model not trained yet.")

    X = prepare_features(df)
    shap_vals = explainer.shap_values(X)
    importance = dict(zip(
        FEATURE_COLS,
        np.abs(shap_vals).mean(axis=0).round(6).tolist(),
    ))
    return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))


def get_local_explanation(df_row: pd.DataFrame) -> dict:
    """Row-level feature contribution (Local) for strategic insight."""
    global explainer
    if explainer is None:
        load_model_if_exists()
    if explainer is None:
        raise ValueError("Model not trained yet.")

    X = prepare_features(df_row)
    # Calculate SHAP values for a single row
    shap_vals = explainer.shap_values(X)
    
    # We want to identify the features contributing MOST to the 'Churn' side
    # Features with the highest positive SHAP values are driving the probability up
    row_shap = shap_vals[0]
    
    # Map back to features
    impacts = []
    for i, col in enumerate(FEATURE_COLS):
        impacts.append({
            "feature": col,
            "impact": float(row_shap[i]),
            "value": str(df_row.iloc[0][col])
        })
    
    # Sort by impact (highest contributors to churn first)
    top_churn_drivers = sorted(
        [imp for imp in impacts if imp["impact"] > 0], 
        key=lambda x: x["impact"], reverse=True
    )
    
    return top_churn_drivers[:3]


def is_model_trained() -> bool:
    return model is not None or os.path.exists(MODEL_PATH)


# Auto-load on import
load_model_if_exists()