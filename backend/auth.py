import logging
import time

import requests
from jose import jwk, jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.config import settings

logger = logging.getLogger("customeriq.auth")

# Configuration loaded from Central Settings (Strictly validated)
JWT_SECRET = settings.SUPABASE_JWT_SECRET

security = HTTPBearer()

# ── JWKS cache ─────────────────────────────────────────────────
# Newer Supabase projects sign JWTs with ES256 (keyed by a `kid`).
# We fetch the public keys from the project JWKS endpoint and verify
# against them, falling back to the classic HS256 shared secret.
_JWKS_CACHE: dict = {}
_JWKS_CACHE_TS: float = 0.0
_JWKS_TTL = 300  # seconds


def _fetch_public_key(kid: str):
    """Return the JWK matching the token's `kid`, cached for 5 minutes."""
    global _JWKS_CACHE, _JWKS_CACHE_TS
    if not settings.SUPABASE_URL:
        return None

    if not _JWKS_CACHE or (time.time() - _JWKS_CACHE_TS) > _JWKS_TTL:
        try:
            resp = requests.get(
                f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json",
                timeout=5,
            )
            if resp.status_code == 200:
                keys = resp.json().get("keys", [])
                _JWKS_CACHE = {k.get("kid"): k for k in keys if k.get("kid")}
                _JWKS_CACHE_TS = time.time()
        except Exception as exc:
            logger.warning("JWKS fetch failed: %s", exc)

    return _JWKS_CACHE.get(kid)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Decodes and validates a Supabase JWT (HS256 secret or ES256/RS256 via JWKS).
    Returns the user data if valid, otherwise raises a 401.
    """
    token = credentials.credentials

    # Local-development bypass. Never enabled in production.
    if settings.ALLOW_DEMO_TOKEN and token == "dummy-token":
        return {"sub": "local-admin", "email": "admin@customeriq.ai", "role": "authenticated"}

    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", settings.JWT_ALGORITHM)

        if alg in {"ES256", "RS256"}:
            public_jwk = _fetch_public_key(header.get("kid"))
            key = jwk.construct(public_jwk) if public_jwk else JWT_SECRET
            algorithms = ["ES256", "RS256"]
        else:
            key = JWT_SECRET
            algorithms = [settings.JWT_ALGORITHM]

        # verify_aud=False because Supabase uses project-specific audiences
        # (e.g. 'authenticated')
        payload = jwt.decode(
            token,
            key,
            algorithms=algorithms,
            options={"verify_aud": False},
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials: No sub found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except HTTPException:
        raise
    except Exception as e:
        # Detailed log for diagnosis without leaking token contents
        logger.warning("JWT validation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
