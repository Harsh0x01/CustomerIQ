from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models
from typing import Optional
import logging
from backend.auth import get_current_user
from fastapi_cache.decorator import cache

router = APIRouter()
logger = logging.getLogger("customeriq.customers")


@router.get("/stats")
@cache(expire=300)
def get_stats(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """High-level platform statistics — Single-pass production optimization."""
    try:
        # Optimized: All statistics in 1 database round-trip
        stats = db.query(
            func.count(models.Customer.id).label("total"),
            func.sum(models.Customer.exited).label("churned"),
            func.avg(models.Customer.balance).label("avg_balance"),
            func.avg(models.Customer.age).label("avg_age"),
            func.avg(models.Customer.tenure).label("avg_tenure"),
        ).first()

        total = stats.total or 0
        if total == 0:
            return {
                "total_customers": 0,
                "churned": 0,
                "active": 0,
                "churn_rate": 0.0,
                "avg_balance": 0.0,
                "avg_age": 0.0,
                "avg_tenure": 0.0,
            }

        churned = int(stats.churned or 0)
        active = total - churned

        return {
            "total_customers": total,
            "churned": churned,
            "active": active,
            "churn_rate": round(churned / total * 100, 2),
            "avg_balance": round(float(stats.avg_balance or 0), 2),
            "avg_age": round(float(stats.avg_age or 0), 1),
            "avg_tenure": round(float(stats.avg_tenure or 0), 1),
        }
    except Exception as e:
        logger.error(f"Platform Stats Engine Failure: {e}")
        raise HTTPException(status_code=500, detail="Intelligence Engine Unavailable")


@router.get("/")
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=5000),
    gender: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    min_balance: Optional[float] = None,
    max_balance: Optional[float] = None,
    exited: Optional[int] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Paginated, filterable customer list."""
    query = db.query(models.Customer)

    if gender:
        query = query.filter(models.Customer.gender == gender)
    if min_age is not None:
        query = query.filter(models.Customer.age >= min_age)
    if max_age is not None:
        query = query.filter(models.Customer.age <= max_age)
    if min_balance is not None:
        query = query.filter(models.Customer.balance >= min_balance)
    if max_balance is not None:
        query = query.filter(models.Customer.balance <= max_balance)
    if exited is not None:
        query = query.filter(models.Customer.exited == exited)

    total = query.count()
    customers = query.order_by(models.Customer.customer_id).offset(skip).limit(limit).all()

    return {
        "total": total,
        "returned": len(customers),
        "customers": [c.to_dict() for c in customers],
    }


@router.get("/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Fetch a single customer by ID."""
    customer = (
        db.query(models.Customer)
        .filter(models.Customer.customer_id == customer_id)
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")
    return customer.to_dict()


@router.delete("/all", status_code=200)
def delete_all_customers(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """⚠️ Wipe all customer records."""
    deleted = db.query(models.Customer).delete()
    db.commit()
    return {"message": f"Deleted {deleted} customers."}


@router.get("/audit/logs")
@cache(expire=60)
def get_audit_logs(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Fetch chronological platform action logs."""
    logs = db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "user_email": l.user_email,
            "action": l.action,
            "target": l.target,
            "details": l.details,
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M")
        } for l in logs
    ]
