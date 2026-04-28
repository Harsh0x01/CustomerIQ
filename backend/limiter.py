from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Create a rate limiter instance
# In a real distributed system, we would store this in Redis.
# For this deployable version, we use the local memory backend.
limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app):
    """
    Registers the rate limiting logic and error handlers with the FastAPI app.
    Prevents API abuse and ensures stability.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
