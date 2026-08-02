import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Enterprise-grade configuration using Pydantic-Settings.
    Strictly validates required environment variables at startup.
    """
    # ── Database ────────────────────────────────────────────────
    # Required: Will raise an error if not found in .env
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    
    # ── Redis ───────────────────────────────────────────────────
    # Required for caching and Celery
    REDIS_URL: str = Field("redis://localhost:6379/0", description="Redis connection URL for caching/tasks")
    
    # ── Supabase ────────────────────────────────────────────────
    # Required: JWT Secret for HS256 token validation
    SUPABASE_JWT_SECRET: str = Field(..., description="JWT Secret from Supabase API settings")
    SUPABASE_URL: str = Field("", description="Supabase project URL (used to fetch JWKS for ES256/RS256 tokens)")
    SUPABASE_ANON_KEY: str = Field("", description="Supabase anon/publishable key")
    JWT_ALGORITHM: str = "HS256"

    # ── Auth Bypass (Local Development Only) ────────────────────
    # Enables the hard-coded "dummy-token" bypass used by the offline dev flows.
    # MUST stay False in any production deployment.
    ALLOW_DEMO_TOKEN: bool = False

    # ── App Metadata ────────────────────────────────────────────
    APP_NAME: str = "CustomerIQ"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ── CORS ────────────────────────────────────────────────────
    # Default to localhost for development, can be csv for production
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://localhost:8501"
    
    # ── Rate Limiting ───────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 20
    LOG_JSON: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Singleton instance
settings = Settings()
