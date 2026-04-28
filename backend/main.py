import logging
import sys
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pythonjsonlogger import jsonlogger
from sqlalchemy.sql import text

from backend.routers import upload, predict, customers
from backend.database import engine, get_db
from backend import models
from backend.config import settings
from backend.limiter import setup_rate_limiting

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

# ── Structured JSON Logging ──────────────────────────────────
# Essential for professional deployment (ELK/Datadog/CloudWatch)
if settings.LOG_JSON:
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        timestamp=True
    )
    log_handler.setFormatter(formatter)

    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
    root_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)

    # Silence verbose third-party loggers
    logging.getLogger("uvicorn.access").handlers = [log_handler]
    logging.getLogger("uvicorn.error").handlers = [log_handler]
else:
    # Use standard uvicorn/fastapi logging for local development
    logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)

logger = logging.getLogger("customeriq")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Production Lifecycle Management.
    Handles startup configuration, caching initialization, and connection pool cleanup.
    """
    logger.info("🚀 CustomerIQ platform starting up...", extra={"version": settings.APP_VERSION})
    
    # Initialize Redis Caching
    try:
        redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        logger.info("✅ Redis caching initialized.")
    except Exception as e:
        logger.error("❌ Redis initialization failed", extra={"error": str(e)})

    # Schema management is now handled via Alembic migrations.
    
    yield
    
    logger.info("👋 CustomerIQ platform shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-Ready AI Platform for Customer Intelligence.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ── Middleware & Security ─────────────────────────────────────
# Rate Limiting Setup
setup_rate_limiting(app)

# CORS Lockdown
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ── Performance: Caching Middleware ──────────────────────────
@app.middleware("http")
async def add_cache_control_header(request, call_next):
    """Injects Cache-Control headers into GET responses for performance."""
    response = await call_next(request)
    if request.method == "GET" and response.status_code == 200:
        response.headers["Cache-Control"] = "public, max-age=300"
    return response

# ── API Versioning (v1) ───────────────────────────────────────
# Encapsulating routers for future-proof iteration.
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
v1_router.include_router(upload.router,    prefix="/upload",    tags=["Upload"])
v1_router.include_router(predict.router,   prefix="/predict",   tags=["Predict"])

@v1_router.get("/health", tags=["Meta"])
def health_check(db=Depends(get_db)):
    """
    Instrumented Health Check.
    Verifies that the application can actually reach the database.
    """
    try:
        # Perform a low-impact query to verify DB connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error("Health check failed: Database unreachable", extra={"error": str(e)})
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "reason": "Database connection failed"}
        )

app.include_router(v1_router)

@app.get("/", tags=["Meta"])
def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "restricted"
    }

# ── Global Error Handling ─────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Centralized error catching for production stability.
    Ensures all errors are logged as JSON for analysis.
    """
    logger.error(f"Internal Server Error on {request.url}", extra={"error": str(exc)}, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "A secure internal error occurred. Audit logs have been generated."}
    )