import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger("customeriq.ml.segment")

FEATURE_COLS = ["age", "balance", "tenure", "estimated_salary", "num_products"]
SEGMENT_LABELS = ["Low Value", "Mid Value", "High Value", "Premium", "Elite"]

# Columns returned per customer. Includes the numeric drivers so the React
# 3D scatter (and any other consumer) can render real coordinates.
OUTPUT_COLS = [
    "customer_id", "segment", "cluster", "segment_label",
    "balance", "estimated_salary", "tenure",
]


def segment_customers(df: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """Cluster customers into value segments using KMeans."""
    if n_clusters < 2 or n_clusters > len(SEGMENT_LABELS):
        raise ValueError(f"n_clusters must be between 2 and {len(SEGMENT_LABELS)}")

    df = df.copy()
    X = df[FEATURE_COLS].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["segment"] = kmeans.fit_predict(X_scaled)

    # Rank segments by average balance, then assign labels lowest → highest
    segment_means = df.groupby("segment")["balance"].mean().sort_values()
    label_map = {
        seg: SEGMENT_LABELS[i]
        for i, seg in enumerate(segment_means.index)
    }
    df["segment_label"] = df["segment"].map(label_map)
    # Alias used by frontends that expect a `cluster` field
    df["cluster"] = df["segment"]

    logger.info(f"Segmented {len(df)} customers into {n_clusters} clusters.")
    cols = [c for c in OUTPUT_COLS if c in df.columns]
    return df[cols]


def get_segment_summary(df: pd.DataFrame) -> list:
    """Aggregate per-cluster stats. Returns a list so frontends can iterate.

    Each item carries both `segment` and `segment_name` keys for compatibility
    with the Streamlit pages and the React dashboard.
    """
    total = len(df) or 1
    churn_col = "churn_probability" if "churn_probability" in df.columns else None
    balance_col = "balance" if "balance" in df.columns else None

    summary = []
    for seg_id in sorted(df["segment"].unique()):
        group = df[df["segment"] == seg_id]
        label = group["segment_label"].iloc[0]

        avg_balance = 0.0
        if balance_col is not None:
            avg_balance = float(group[balance_col].mean() or 0.0)

        avg_churn = 0.0
        if churn_col is not None:
            avg_churn = round(float(group[churn_col].mean() or 0.0), 4)

        summary.append({
            "segment": label,
            "segment_name": label,
            "count": int(len(group)),
            "percentage": round(len(group) / total * 100, 1),
            "avg_balance": round(avg_balance, 2),
            "avg_churn": avg_churn,
            "top_feature": "Balance",
        })
    return summary
