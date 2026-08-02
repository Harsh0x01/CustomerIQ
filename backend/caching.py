"""Cache key builders for fastapi-cache that scope responses to the caller.

The default key builder ignores the caller identity, which means cached
responses on authenticated endpoints could be shared across users. These
builders include the authenticated user's `sub` in the key.

The key is intentionally derived only from the request path, query string,
and caller identity — DB session objects (which differ per request) are
excluded so the key stays stable across calls.
"""


def user_aware_key_builder(func, *args, **kwargs):
    """Build a cache key from the request path + caller identity.

    Works for endpoints that declare a FastAPI `Request` and for those
    that only receive `db` / `user` dependency kwargs.
    """
    request = kwargs.get("request")
    if request is not None:
        base = f"{request.url.path}:{sorted(request.query_params.multi_items())}"
    else:
        base = f"{func.__module__}:{func.__name__}"

    user = kwargs.get("user")
    if isinstance(user, dict) and user.get("sub"):
        base = f"{base}:{user['sub']}"

    return base
