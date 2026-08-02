"""Natural-language intelligence endpoints.

Backs the React "Intelligence" module. Not a full GraphRAG system — it
derives a deterministic, data-driven answer from the live churn model,
SHAP importance, and KMeans segments so the page is functional end-to-end.
"""

import logging

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.database import get_db
from backend.schemas import IntelligenceQuery
from ml.churn import get_shap_values, predict_churn, is_model_trained
from ml.segment import segment_customers, get_segment_summary

router = APIRouter()
logger = logging.getLogger("customeriq.intelligence")


def _customers_df(db: Session) -> pd.DataFrame:
    customers = db.query(models.Customer).all()
    if not customers:
        return pd.DataFrame()
    return pd.DataFrame([c.to_dict() for c in customers])


def _derive_insights(df: pd.DataFrame) -> dict:
    """Compute the insight payload: drivers, risk counts, segment shape."""
    insights = {
        "top_drivers": [],
        "high_risk": None,
        "medium_risk": None,
        "segments": [],
    }

    preds = None
    if is_model_trained():
        try:
            importance = get_shap_values(df)
            insights["top_drivers"] = [
                {"feature": k, "impact": float(v)}
                for k, v in list(importance.items())[:3]
            ]
            preds = predict_churn(df)
            insights["high_risk"] = int((preds["risk_level"] == "High").sum())
            insights["medium_risk"] = int((preds["risk_level"] == "Medium").sum())
        except Exception as e:
            logger.warning(f"Model-backed insight computation failed: {e}")

    if not df.empty:
        try:
            segs = segment_customers(df, n_clusters=4)
            if preds is not None and not preds.empty:
                segs = segs.merge(
                    preds[["customer_id", "churn_probability"]],
                    on="customer_id",
                    how="left",
                )
            insights["segments"] = get_segment_summary(segs)
        except Exception as e:
            logger.warning(f"Segmentation insight computation failed: {e}")

    return insights


@router.post("/query")
def intelligence_query(
    payload: IntelligenceQuery,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Answer a natural-language question with data-derived reasoning."""
    query = payload.query
    df = _customers_df(db)
    if df.empty:
        return {
            "status": "ok",
            "query": query,
            "answer": "No customer data loaded yet. Upload a CSV via the Upload module to begin.",
            "reasoning": [],
        }

    insights = _derive_insights(df)

    if insights["segments"]:
        by_churn = [s for s in insights["segments"] if s.get("avg_churn", 0) > 0]
        focus = max(by_churn, key=lambda s: s["avg_churn"]) if by_churn else None
        if focus is None:
            focus = max(insights["segments"], key=lambda s: s["percentage"])
        focus_text = (
            f"Segment '{focus['segment']}' ({focus['count']} customers, "
            f"{focus['percentage']}% of base) shows the highest churn signal "
            f"at {focus['avg_churn'] * 100:.1f}% average probability."
        )
    else:
        focus_text = "Segmentation is not yet available for this dataset."

    drivers = insights["top_drivers"]
    drivers_text = (
        ", ".join(f"{d['feature']} (impact {d['impact']:.3f})" for d in drivers)
        if drivers else "no trained model available for SHAP attribution"
    )

    risk_text = ""
    if insights["high_risk"] is not None:
        risk_text = (
            f" {insights['high_risk']} customers are currently high-risk and "
            f"{insights['medium_risk']} are medium-risk."
        )

    answer = (
        f"{focus_text} Top churn drivers by SHAP contribution: {drivers_text}."
        f"{risk_text} Recommended action: prioritize high-touch retention outreach "
        "for the highest-risk accounts in that segment."
    )

    reasoning = [
        "Ranked churn drivers by mean |SHAP| contribution across the active model",
        f"Scored the customer base and bucketed risk tiers",
        "Clustered the base with KMeans and computed per-segment churn means",
    ]

    return {
        "status": "ok",
        "query": query,
        "answer": answer,
        "reasoning": reasoning,
        "insights": {
            "top_drivers": insights["top_drivers"],
            "high_risk": insights["high_risk"],
            "medium_risk": insights["medium_risk"],
            "segments": insights["segments"],
        },
    }


@router.post("/brief")
def generate_brief(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Generate a structured executive summary brief from current analytics."""
    df = _customers_df(db)
    if df.empty:
        return {
            "status": "ok",
            "brief": {
                "headline": "No data loaded",
                "sections": ["Upload customer data to generate an executive brief."],
            },
        }

    insights = _derive_insights(df)

    total = len(df)
    churned = int(df["exited"].sum()) if "exited" in df.columns else 0
    churn_rate = round(churned / total * 100, 2) if total else 0.0

    segments = insights["segments"]
    top_segment = max(segments, key=lambda s: s["percentage"]) if segments else None

    sections = [
        f"Base size: {total} customers with a historical churn rate of {churn_rate}%.",
    ]
    if insights["high_risk"] is not None:
        sections.append(
            f"Model projects {insights['high_risk']} high-risk and "
            f"{insights['medium_risk']} medium-risk accounts."
        )
    if insights["top_drivers"]:
        sections.append(
            "Primary churn drivers: "
            + ", ".join(d["feature"] for d in insights["top_drivers"]) + "."
        )
    if top_segment:
        sections.append(
            f"Largest segment: '{top_segment['segment']}' at "
            f"{top_segment['percentage']}% of the base."
        )

    return {
        "status": "ok",
        "brief": {
            "headline": f"Executive churn briefing — {churn_rate}% historical churn",
            "sections": sections,
        },
    }
