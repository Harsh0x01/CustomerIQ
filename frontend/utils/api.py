import requests
import streamlit as st
from streamlit import cache_data
import os
from dotenv import load_dotenv

load_dotenv()

# ── Dynamic Configuration ─────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 5  # seconds — prevents infinite hangs when backend is down

def get_auth_headers():
    """Injects the Supabase JWT into every outgoing request."""
    if "token" in st.session_state and st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# ── Customer Data Tier ────────────────────────────────────────

@cache_data(ttl=300)
def get_stats():
    """Fetches high-level executive statistics."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/customers/stats", headers=get_auth_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception:
        return {}

@cache_data(ttl=300)
def get_customers(limit: int = 1000, skip: int = 0):
    """Fetches paginated customer records."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/customers/",
            params={"limit": limit, "skip": skip},
            headers=get_auth_headers(),
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        return {"customers": []}
    except Exception:
        return {"customers": []}

def upload_csv(file):
    """Ingests raw CSV data into the platform."""
    try:
        files = {"file": (file.name, file.getvalue(), "text/csv")}
        response = requests.post(f"{API_BASE_URL}/api/v1/upload/", files=files, headers=get_auth_headers(), timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

# ── ML Intelligence Tier ──────────────────────────────────────

def predict_single(data: dict):
    """Inference for a single customer profile (with history logging)."""
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/predict/", json=data, headers=get_auth_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        # Return the error detail so the UI can display it
        try:
            detail = response.json().get("detail", f"Server returned {response.status_code}")
        except Exception:
            detail = f"Server returned {response.status_code}"
        return {"_error": detail}
    except requests.exceptions.ConnectionError:
        return {"_error": "Backend is not running. Start FastAPI server first."}
    except requests.exceptions.Timeout:
        return {"_error": "Backend request timed out."}
    except Exception as e:
        return {"_error": str(e)}

def get_recommendations(customer_id: str):
    """Fetches diagnostic SHAP drivers and prescriptive advice."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/predict/recommendations/{customer_id}",
            headers=get_auth_headers(),
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get("detail", "Strategic analysis failed")
    except Exception as e:
        return False, str(e)

@cache_data(ttl=300)
def get_clv_prediction():
    """Fetches Customer Lifetime Value estimates for the base."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/predict/clv", headers=get_auth_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

@cache_data(ttl=300)
def get_segments(n_clusters: int = 4):
    """Fetches behavioral segmentation clusters."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/predict/segments",
            params={"n_clusters": n_clusters},
            headers=get_auth_headers(),
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

@cache_data(ttl=300)
def get_shap_values():
    """Fetches global explainability metrics."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/predict/shap", headers=get_auth_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return {"feature_importance": {}}
    except Exception:
        return {"feature_importance": {}}

def get_feature_importance():
    """Alias for get_shap_values to support legacy pages."""
    return get_shap_values()

# ── MLOps & Observability Tier ────────────────────────────────

def train_model_async(use_optuna: bool = False):
    """Triggers background training task via Celery."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/predict/train/async",
            params={"use_optuna": use_optuna},
            headers=get_auth_headers(),
            timeout=REQUEST_TIMEOUT
        )
        return response.json()
    except Exception:
        return {"status": "failed"}

@cache_data(ttl=300)
def get_audit_logs(limit: int = 10):
    """Fetches platform action history."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/customers/audit/logs",
            params={"limit": limit},
            headers=get_auth_headers(),
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

@cache_data(ttl=300)
def get_drift_report():
    """Fetches statistical variance diagnostics."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/predict/drift", headers=get_auth_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return {"drift_detected": False}
    except Exception:
        return {"drift_detected": False}

@cache_data(ttl=300)
def get_model_status():
    """Checks for active weights on disk."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/predict/status", headers=get_auth_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json().get("model_trained", False)
        return False
    except Exception:
        return False

def health_check():
    """Verifies that the backend is reachable and healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return True
        return False
    except Exception:
        return False

def predict_batch(file):
    """Predict churn for multiple customers via CSV upload."""
    try:
        files = {"file": (file.name, file.getvalue(), "text/csv")}
        response = requests.post(f"{API_BASE_URL}/api/v1/predict/batch", files=files, headers=get_auth_headers(), timeout=30)
        if response.status_code == 200:
            return response.json()
        try:
            detail = response.json().get("detail", f"Server returned {response.status_code}")
        except Exception:
            detail = f"Server returned {response.status_code}"
        return {"_error": detail}
    except requests.exceptions.ConnectionError:
        return {"_error": "Backend is not running. Start FastAPI server first."}
    except requests.exceptions.Timeout:
        return {"_error": "Batch prediction timed out. Try a smaller file."}
    except Exception as e:
        return {"_error": str(e)}

@cache_data(ttl=300)
def get_model_runs():
    """Fetches historical MLflow training runs."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/predict/runs", headers=get_auth_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json().get("runs", [])
        return []
    except Exception:
        return []

def activate_model_run(run_id: str):
    """Rolls back the active model to a specific historical run."""
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/predict/activate/{run_id}", headers=get_auth_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return True, response.json().get("message")
        return False, response.json().get("detail", "Activation failed")
    except Exception as e:
        return False, str(e)

def train_model():
    """Synchronous model training (Legacy Support)."""
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/predict/train", headers=get_auth_headers(), timeout=60)
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get("detail", "Training failed")
    except Exception as e:
        return False, str(e)
