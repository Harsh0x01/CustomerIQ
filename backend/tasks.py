import time
import requests
import json
import logging
from backend.celery_app import celery_app
from ml.churn import train_model as train_churn
from ml.clv import train_clv_model as train_clv
from backend.database import SessionLocal
from backend.models import AuditLog, Customer
from sqlalchemy import func

logger = logging.getLogger("customeriq.tasks")

@celery_app.task(name="train_churn_prediction_task")
def train_churn_prediction_task(use_optuna: bool = False):
    """Background task for churn model training."""
    db = SessionLocal()
    try:
        # Load data from DB
        customers = db.query(Customer).all()
        if not customers:
            return {"status": "error", "message": "No data in database to train on."}
            
        import pandas as pd
        df = pd.DataFrame([c.to_dict() for c in customers])
        
        # Start training
        results = train_churn(df, use_optuna=use_optuna)
        
        # Log to AuditLog
        audit = AuditLog(
            user_email="system@customeriq.ai",
            action="TRAIN_MODEL_ASYNC",
            target=f"churn_v{results.get('run_id')[:8]}",
            details=json.dumps(results)
        )
        db.add(audit)
        db.commit()
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        logger.error(f"Async training failed: {str(e)}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="dispatch_webhook_task")
def dispatch_webhook_task(url: str, payload: dict):
    """Send outward notifications for critical churn anomalies."""
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return {"status": "success", "code": response.status_code}
    except Exception as e:
        logger.error(f"Webhook dispatch failed: {str(e)}")
        return {"status": "failed", "error": str(e)}

@celery_app.task(name="generate_clv_model_task")
def generate_clv_model_task():
    """Background task for CLV regressor training."""
    db = SessionLocal()
    try:
        customers = db.query(Customer).all()
        if not customers:
            return {"status": "error", "message": "No data."}
            
        import pandas as pd
        df = pd.DataFrame([c.to_dict() for c in customers])
        
        results = train_clv(df)
        
        audit = AuditLog(
            user_email="system@customeriq.ai",
            action="TRAIN_CLV_ASYNC",
            target="clv_model_v1",
            details=json.dumps(results)
        )
        db.add(audit)
        db.commit()
        
        return {"status": "success", "results": results}
    finally:
        db.close()
