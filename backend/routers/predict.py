from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from backend.config import settings
from backend.schemas import ChurnPredictionInput, TrainingMetrics
from backend.limiter import limiter
from backend.recommendations import StrategyAdvisor
from backend.tasks import train_churn_prediction_task, generate_clv_model_task
from ml.churn import (
    train_model, predict_churn, get_shap_values, 
    is_model_trained, get_model_runs, activate_model_version,
    get_local_explanation, detect_drift, detect_anomalies, get_active_model_version
)
from ml.segment import segment_customers, get_segment_summary
from ml.clv import predict_clv, train_clv_model, is_clv_trained

import socket as _socket
import pandas as pd
import logging
import io
import json
from urllib.parse import urlparse
from backend.auth import get_current_user
from backend.caching import user_aware_key_builder
from fastapi_cache.decorator import cache

router = APIRouter()
logger = logging.getLogger("customeriq.predict")

BATCH_REQUIRED_COLUMNS = [
    "customer_id", "age", "gender", "tenure", "balance",
    "num_products", "has_credit_card", "is_active_member", "estimated_salary",
]


def _get_customers_df(db: Session) -> pd.DataFrame:
    customers = db.query(models.Customer).all()
    if not customers:
        raise HTTPException(
            status_code=404,
            detail="No customers found in the database. Upload data first via POST /upload/csv.",
        )
    return pd.DataFrame([c.to_dict() for c in customers])


def _broker_available(timeout: float = 2.0) -> bool:
    """Check whether the Celery/Redis broker is reachable without hanging.

    Celery's ``.delay()`` blocks on the broker connection when Redis is down,
    which turns the API call into an infinite wait. Probe the socket first.
    """
    try:
        parts = urlparse(settings.REDIS_URL)
        host = parts.hostname or "localhost"
        port = parts.port or 6379
        sock = _socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except Exception:
        return False


@router.post("/train", response_model=dict)
@limiter.limit("5/minute")
def train(request: Request, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Sync training (small datasets only)."""
    df = _get_customers_df(db)
    if len(df) < 10:
        raise HTTPException(status_code=422, detail="Need at least 10 customers.")
    metrics = train_model(df)
    
    # Log to AuditLog
    audit = models.AuditLog(
        user_email=user["email"],
        action="TRAIN_MODEL_SYNC",
        target="churn_v1.0",
        details=json.dumps(metrics)
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Model trained successfully.", "metrics": metrics}


@router.post("/train/async")
def train_async(use_optuna: bool = False, user: dict = Depends(get_current_user)):
    """Fire and forget training task for larger datasets."""
    task = train_churn_prediction_task.delay(use_optuna=use_optuna)
    return {"task_id": task.id, "status": "queued"}


@router.get("/drift")
def check_drift(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Statistical verification of data health."""
    df = _get_customers_df(db)
    report = detect_drift(df)
    return report


@router.get("/runs")
def list_runs(user: dict = Depends(get_current_user)):
    """List all historical MLflow training runs."""
    try:
        runs = get_model_runs()
        return {"runs": runs}
    except Exception as e:
        logger.error(f"Failed to fetch runs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve model history.")


@router.post("/activate/{run_id}")
def activate_version(run_id: str, user: dict = Depends(get_current_user)):
    """Activate/Rollback to a specific model version from MLflow."""
    try:
        success = activate_model_version(run_id)
        if success:
            return {"message": f"Successfully activated model run {run_id}."}
        else:
            raise HTTPException(status_code=404, detail="Run ID invalid or artifacts missing.")
    except Exception as e:
        logger.error(f"Activation failed: {e}")
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/")
@limiter.limit("30/minute")
def predict_single(
    request: Request, 
    data: ChurnPredictionInput, 
    db: Session = Depends(get_db), 
    user: dict = Depends(get_current_user)
):
    """
    Predict churn with automated history logging and anomaly detection.
    Supports 'What-If' simulations by enabling feature overrides.
    """
    if not is_model_trained():
        raise HTTPException(status_code=409, detail="Model not trained.")
    
    try:
        input_dict = data.model_dump()
        df = pd.DataFrame([input_dict])
        
        # 1. Prediction execution
        results = predict_churn(df)
        res_dict = results.iloc[0].to_dict()
        
        # 2. Anomaly Check
        is_anomaly = detect_anomalies(df).iloc[0]
        res_dict["is_anomaly"] = bool(is_anomaly)

        # 3. Persistence & Audit Trail (Senior Tier Requirement)
        customer_id = input_dict.get("customer_id") or "WHAT_IF_SIM"
        prediction_record = models.PredictionHistory(
            customer_id=customer_id,
            model_version=get_active_model_version(),
            inputs=input_dict,
            probability=float(res_dict["churn_probability"]),
            prediction=int(res_dict["churn_prediction"]),
            risk_level=res_dict["risk_level"]
        )
        db.add(prediction_record)
        
        # Log What-If scenarios separately to AuditLog
        if customer_id == "WHAT_IF_SIM":
            audit = models.AuditLog(
                user_email=user["email"],
                action="WHAT_IF_SIMULATION",
                details=json.dumps(input_dict)
            )
            db.add(audit)
            
        db.commit()
        return res_dict

    except Exception as e:
        logger.error(f"Prediction flow failed: {e}")
        raise HTTPException(status_code=422, detail="Diagnostic processing engine failed.")


@router.get("/recommendations/{customer_id}")
@limiter.limit("20/minute")
@cache(expire=600, key_builder=user_aware_key_builder)
def get_recommendations(
    request: Request,
    customer_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Generates a formal retention strategy (Cached for 10 min).
    """
    if not is_model_trained():
        raise HTTPException(status_code=409, detail="Model not trained.")

    # ... logic remains consistent ...
    customer = db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
        
    df_row = pd.DataFrame([customer.to_dict()])
    drivers = get_local_explanation(df_row)
    strategies = StrategyAdvisor.generate_strategy(drivers)
    
    return {
        "customer_id": customer_id,
        "risk_drivers": drivers,
        "strategic_directives": strategies
    }


@router.post("/batch")
@limiter.limit("10/minute")
async def predict_batch(
    request: Request,
    file: UploadFile = File(...), 
    user: dict = Depends(get_current_user)
):
    """Predict churn for multiple customers in a CSV file. Limited to 10 files/min."""
    if not is_model_trained():
        raise HTTPException(status_code=409, detail="Model not trained.")
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed.")
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))

        missing = [c for c in BATCH_REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required column(s): {', '.join(missing)}",
            )

        results = predict_churn(df)
        return results.to_dict(orient="records")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/status")
def model_status():
    """Check if a trained model is available."""
    trained = is_model_trained()
    return {"model_trained": trained}


@router.get("/churn")
def churn_predictions(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Run churn predictions on all customers."""
    if not is_model_trained():
        raise HTTPException(
            status_code=409,
            detail="Model not trained yet. Call POST /predict/train first.",
        )
    df = _get_customers_df(db)
    results = predict_churn(df)
    return {
        "total_customers": len(results),
        "high_risk": int((results["risk_level"] == "High").sum()),
        "medium_risk": int((results["risk_level"] == "Medium").sum()),
        "low_risk": int((results["risk_level"] == "Low").sum()),
        "predictions": results.to_dict(orient="records"),
    }


@router.get("/shap")
@cache(expire=3600, key_builder=user_aware_key_builder)
def shap_values(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Global feature importance (Cached for 1 Hour)."""
    if not is_model_trained():
        raise HTTPException(status_code=409, detail="Model not trained.")
    df = _get_customers_df(db)
    return {"feature_importance": get_shap_values(df)}


@router.get("/clv")
@cache(expire=3600, key_builder=user_aware_key_builder)
def clv_predictions(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Predict Customer Lifetime Value for the entire base."""
    if not is_clv_trained():
        if _broker_available():
            # Async path (Redis/Celery up) — train in the background
            generate_clv_model_task.delay()
            raise HTTPException(status_code=202, detail="CLV model training initiated in background.")
        logger.warning("Redis broker unavailable — training CLV model synchronously.")
        try:
            train_clv_model(_get_customers_df(db))
        except Exception as e:
            logger.error(f"Synchronous CLV training failed: {e}")
            raise HTTPException(status_code=503, detail="CLV model unavailable.")

    df = _get_customers_df(db)
    results = predict_clv(df)
    return results.to_dict(orient="records")


@router.get("/segments")
@cache(expire=1800, key_builder=user_aware_key_builder)
def segments(
    n_clusters: int = Query(4, ge=2, le=5),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Segment customers using KMeans (Cached for 30 min)."""
    df = _get_customers_df(db)
    results = segment_customers(df, n_clusters=n_clusters)

    # Enrich each segment with average churn probability when a model exists
    if is_model_trained():
        try:
            churn = predict_churn(df)[["customer_id", "churn_probability"]]
            results = results.merge(churn, on="customer_id", how="left")
        except Exception as e:
            logger.warning(f"Failed to merge churn scores into segments: {e}")

    summary = get_segment_summary(results)
    return {
        "n_clusters": n_clusters,
        "summary": summary,
        "segments": results.to_dict(orient="records"),
    }