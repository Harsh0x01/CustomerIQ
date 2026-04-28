import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger("customeriq.ml.segment")

FEATURE_COLS = ["age", "balance", "tenure", "estimated_salary", "num_products"]
SEGMENT_LABELS = ["Low Value", "Mid Value", "High Value", "Premium", "Elite"]

scaler = None
kmeans_model = None


def segment_customers(df: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """Cluster customers into value segments using KMeans."""
    global scaler, kmeans_model

    if n_clusters < 2 or n_clusters > len(SEGMENT_LABELS):
        raise ValueError(f"n_clusters must be between 2 and {len(SEGMENT_LABELS)}")

    df = df.copy()
    X = df[FEATURE_COLS].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["segment"] = kmeans_model.fit_predict(X_scaled)

    # Rank segments by average balance, then assign labels lowest → highest
    segment_means = df.groupby("segment")["balance"].mean().sort_values()
    label_map = {
        seg: SEGMENT_LABELS[i]
        for i, seg in enumerate(segment_means.index)
    }
    df["segment_label"] = df["segment"].map(label_map)

    logger.info(f"Segmented {len(df)} customers into {n_clusters} clusters.")
    return df[["customer_id", "segment", "segment_label"]]


def get_segment_summary(df: pd.DataFrame) -> dict:
    """Aggregate counts + percentages per segment label."""
    total = len(df)
    summary = {}
    for label in sorted(df["segment_label"].unique()):
        group = df[df["segment_label"] == label]
        summary[label] = {
            "count": len(group),
            "percentage": round(len(group) / total * 100, 1),
        }
    return summary