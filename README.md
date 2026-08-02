# CustomerIQ

End-to-end customer intelligence platform. Ingests customer data, trains a churn prediction model (XGBoost), explains predictions with SHAP, and segments users via KMeans — all through a REST API and web interface.

Built this to solve a real problem: most businesses react to churn *after* it happens. This system predicts it early, explains *why*, and groups customers so you can actually act on it.

## What it does

- **Churn prediction** — XGBoost classifier with probability-based risk tiering. Stratified split, 200 estimators, handles class imbalance.
- **Explainability** — SHAP TreeExplainer breaks down every prediction into per-feature contributions. No black box.
- **Segmentation** — KMeans with configurable k. Clusters customers into behavioral cohorts (high-value, at-risk, etc).
- **CLV estimation** — Lifetime value scoring to prioritize retention efforts where they matter.

## Architecture

```
Frontend (React/Vite) →  Backend API (FastAPI)  →  PostgreSQL (Supabase)
                              ↓
                         ML Engine (XGBoost/SHAP/KMeans)
                              ↓
                         Redis (cache) + Celery (async tasks)
```

The backend is versioned (`/api/v1/`) with JWT auth, rate limiting, and structured logging. Redis handles caching for repeated queries. Celery runs model training async so the API stays responsive.

## Stack

| | |
|---|---|
| API | FastAPI, Uvicorn, Pydantic v2 |
| DB | PostgreSQL (Supabase), SQLAlchemy, Alembic |
| ML | XGBoost, SHAP, scikit-learn |
| Frontend | React 18 + Vite (Tailwind, Recharts, Three.js) |
| Infra | Docker Compose, Nginx, Redis, Celery |
| Auth | Supabase JWT (ES256/RS256 via JWKS, HS256 fallback) |

## Project layout

```
backend/
  main.py           — app setup, lifespan, middleware
  config.py         — pydantic-settings config
  auth.py           — Supabase JWT verification (JWKS)
  models.py         — SQLAlchemy ORM
  caching.py        — per-user cache key builder
  routers/
    customers.py    — CRUD, stats, filtering
    upload.py       — CSV ingestion
    predict.py      — train/predict/shap/segment endpoints
    intelligence.py — natural-language analysis + briefs

ml/
  churn.py          — XGBoost training + SHAP
  segment.py        — KMeans clustering
  clv.py            — lifetime value estimation

frontend/                 — React + Vite app
  src/
    pages/                — dashboard, upload, segments, intelligence, etc.
    services/api.js       — typed API client

data/
  customers.csv           — sample dataset for uploads/demos

tests/
  test_api.py             — backend test suite (auth, upload, predict, segments)
  conftest.py             — fixtures + dependency overrides
```

## Running locally

```bash
# setup
git clone https://github.com/Harsh0x01/CustomerIQ.git
cd CustomerIQ
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# config
cp .env.example .env
# fill in DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY,
# SUPABASE_JWT_SECRET, REDIS_URL. Keep ALLOW_DEMO_TOKEN=false in production.

# run
uvicorn backend.main:app --reload --port 8000   # backend
celery -A backend.tasks worker --loglevel=info   # worker
cd frontend && npm install && npm run dev        # React frontend
```

Or just `.\run_all.ps1` on Windows — it launches everything.

Backend: http://localhost:8000 (docs at `/docs`)
Frontend: http://localhost:5173

## API

```
GET  /api/v1/health                      — DB-verified health check
GET  /api/v1/customers/stats             — aggregated KPIs
GET  /api/v1/customers/                  — paginated list with filters
POST /api/v1/upload/csv                  — ingest CSV
POST /api/v1/predict/train               — train XGBoost model
GET  /api/v1/predict/churn               — run predictions
GET  /api/v1/predict/shap                — feature importance (SHAP values)
GET  /api/v1/predict/segments?n_clusters=4  — KMeans clustering
POST /api/v1/intelligence/query             — natural-language analysis
POST /api/v1/intelligence/brief             — automated executive brief
```

All endpoints under `/api/v1` require a `Bearer` JWT from Supabase. A
`dummy-token` bypass exists for local dev only and is disabled by default
(`ALLOW_DEMO_TOKEN=false`).

## Docker

```bash
docker-compose up --build -d
```

Spins up Postgres, backend (migrations run automatically via `alembic upgrade
head`), Celery, Redis, React frontend, and Nginx reverse proxy (port 80).

## Frontend modules

1. **Dashboard** — live KPIs, risk distribution, high-risk customer table
2. **Upload** — CSV validation, column checking, data preview
3. **Churn Prediction** — one-click training, probability histogram, exportable results
4. **Segments** — interactive cluster count, pie/scatter viz, profile cards
5. **Feature Importance** — SHAP bar chart with per-feature explanations
6. **Customer Explorer** — multi-filter search, card/table view, merged churn scores
7. **Model Management** — versioning, retraining, performance tracking
8. **Retention Analysis** — cohort analysis, churn trends
9. **Intelligence** — natural-language analysis and executive briefs

## Design decisions

- **Why XGBoost over deep learning?** — Tabular customer data. Gradient boosting consistently outperforms neural nets on structured data this size. Plus SHAP integrates natively with tree models.
- **Why React + Vite?** — The canonical product UI. Fast HMR, typed API client, and richer interactive visualizations (Recharts, Three.js) than the legacy Streamlit prototype.
- **Why Supabase?** — Managed Postgres with built-in auth. No infra overhead for a project this scope. Easy to swap for self-hosted PG if needed.
- **API versioning from day one** — `/api/v1/` prefix. Makes it possible to iterate on the API without breaking existing integrations.

## Notes

- `.env` is gitignored. Use `.env.example` as template.
- Rate limiting is set to 20 req/min — adjust `RATE_LIMIT_PER_MINUTE` in config.
- Logs can be switched to JSON format (`LOG_JSON=true`) for production log aggregation.
- `ALLOW_DEMO_TOKEN` enables a `dummy-token` auth bypass for local development only — never enable it in production.
- `ec2_setup.sh` included if you want to deploy on AWS.
- Run the backend test suite with `python -m pytest tests -q`.

---

Built by [Harsh Vardhan Sahu](https://github.com/Harsh0x01)
