"""API-level tests for the CustomerIQ backend.

These run against an isolated in-memory (file-backed) SQLite database so the
local dev database is never touched. Auth is overridden per test so JWT
behaviour can be exercised without a live Supabase instance.
"""

import pytest
from fastapi.testclient import TestClient
from jose import jwt as jose_jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import Base, get_db
from backend.auth import get_current_user
from backend.config import settings

CSV_HEADER = (
    "customer_id,age,gender,tenure,balance,num_products,"
    "has_credit_card,is_active_member,estimated_salary,exited"
)


def _csv_row(customer_id="CUST1", age=30, gender="Male", tenure=5, balance=10000.0,
             products=2, card=1, active=1, salary=50000.0, exited=0):
    return (f"{customer_id},{age},{gender},{tenure},{balance},{products},"
            f"{card},{active},{salary},{exited}")


@pytest.fixture()
def client(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_auth():
        return {"sub": "test-user", "email": "test@example.com", "role": "authenticated"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_auth

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _upload(client, content):
    return client.post(
        "/api/v1/upload/",
        files={"file": ("customers.csv", content, "text/csv")},
    )


# ── Meta / health ─────────────────────────────────────────────

def test_health(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# ── Auth ──────────────────────────────────────────────────────

def test_demo_token_denied_when_disabled(client, monkeypatch):
    monkeypatch.setattr(settings, "ALLOW_DEMO_TOKEN", False)
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.get("/api/v1/customers/stats", headers={"Authorization": "Bearer dummy-token"})
    assert resp.status_code == 401


def test_demo_token_allowed_when_enabled(client, monkeypatch):
    monkeypatch.setattr(settings, "ALLOW_DEMO_TOKEN", True)
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.get("/api/v1/customers/stats", headers={"Authorization": "Bearer dummy-token"})
    assert resp.status_code == 200


def test_hs256_jwt_accepted(client):
    token = jose_jwt.encode(
        {"sub": "real-user", "email": "user@example.com"},
        settings.SUPABASE_JWT_SECRET,
        algorithm="HS256",
    )
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.get(
        "/api/v1/customers/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


def test_garbage_token_rejected(client):
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.get(
        "/api/v1/customers/stats",
        headers={"Authorization": "Bearer not.a.jwt"},
    )
    assert resp.status_code == 401


# ── Customers ─────────────────────────────────────────────────

def test_stats_empty_base(client):
    resp = client.get("/api/v1/customers/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_customers"] == 0
    assert data["churn_rate"] == 0.0


def test_customers_list_empty(client):
    resp = client.get("/api/v1/customers/")
    assert resp.status_code == 200
    assert resp.json()["customers"] == []


def test_upload_requires_auth(client):
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.post(
        "/api/v1/upload/",
        files={"file": ("customers.csv", CSV_HEADER + "\n" + _csv_row(), "text/csv")},
    )
    assert resp.status_code in (401, 403)


def test_upload_rejects_non_csv(client):
    resp = client.post("/api/v1/upload/", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert resp.status_code == 400
    assert "CSV" in resp.json()["detail"]


def test_upload_validates_columns(client):
    resp = _upload(client, "customer_id,age\nCUST1,30\n")
    assert resp.status_code == 400
    assert "Missing column" in resp.json()["detail"]


def test_upload_valid_csv_and_stats(client):
    content = CSV_HEADER + "\n" + _csv_row() + "\n" + _csv_row("CUST2", exited=1)
    resp = _upload(client, content)
    assert resp.status_code == 200
    body = resp.json()
    assert body["saved"] == 2
    assert body["skipped"] == 0

    stats = client.get("/api/v1/customers/stats").json()
    assert stats["total_customers"] == 2
    assert stats["churned"] == 1
    assert stats["churn_rate"] == 50.0

    listing = client.get("/api/v1/customers/").json()
    assert listing["total"] == 2


def test_upload_skips_duplicates(client):
    content = CSV_HEADER + "\n" + _csv_row() + "\n" + _csv_row()
    resp = _upload(client, content)
    assert resp.json()["saved"] == 1
    assert resp.json()["skipped"] == 1


# ── Segments ──────────────────────────────────────────────────

def _seed_customers(client, n=8):
    rows = [CSV_HEADER]
    for i in range(n):
        rows.append(_csv_row(f"CUST{i}", age=25 + i, balance=1000 * (i + 1),
                             salary=30000 + 5000 * i))
    resp = _upload(client, "\n".join(rows))
    assert resp.status_code == 200


def test_segments_contract(client):
    _seed_customers(client, n=8)
    resp = client.get("/api/v1/predict/segments", params={"n_clusters": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert data["n_clusters"] == 3
    # Summary must be an iterable list (frontends iterate it)
    assert isinstance(data["summary"], list)
    assert all("segment" in s and "count" in s and "percentage" in s for s in data["summary"])
    assert sum(s["count"] for s in data["summary"]) == 8
    # Rows carry the numeric drivers for the React 3D scatter
    row = data["segments"][0]
    assert {"cluster", "balance", "estimated_salary", "tenure"}.issubset(row)


def test_segments_rejects_out_of_range_clusters(client):
    _seed_customers(client, n=8)
    resp = client.get("/api/v1/predict/segments", params={"n_clusters": 6})
    assert resp.status_code == 422


# ── Batch prediction validation ───────────────────────────────

def test_predict_batch_validates_columns(client, monkeypatch):
    monkeypatch.setattr("backend.routers.predict.is_model_trained", lambda: True)
    resp = client.post(
        "/api/v1/predict/batch",
        files={"file": ("batch.csv", "customer_id,age\nCUST1,30\n", "text/csv")},
    )
    assert resp.status_code == 400
    assert "Missing required column" in resp.json()["detail"]


# ── Intelligence ──────────────────────────────────────────────

def test_intelligence_query_empty_base(client):
    resp = client.post("/api/v1/intelligence/query", json={"query": "Who is at risk?"})
    assert resp.status_code == 200
    assert "No customer data" in resp.json()["answer"]


def test_intelligence_brief(client, monkeypatch):
    monkeypatch.setattr("backend.routers.intelligence.is_model_trained", lambda: False)
    _seed_customers(client, n=8)
    resp = client.post("/api/v1/intelligence/brief", json={})
    assert resp.status_code == 200
    brief = resp.json()["brief"]
    assert brief["headline"]
    assert len(brief["sections"]) >= 1
