"""
API Security Headers Policy

Handles:
- Authentication headers (Authorization, X-API-Key)
- Request tracking (X-Request-ID)
- API versioning (X-API-Version)
- Rate limiting metadata (X-Rate-Limit-*)
- Content negotiation (Accept, Content-Type)
- Response observability (X-Response-Time)
"""

from app.utils.headers import registry
from flask import request


class APIHeaderPolicy:
    AUTHORIZATION = "Bearer YOUR_STATIC_TOKEN"
    API_KEY = "YOUR_STATIC_API_KEY"
    REQUEST_ID = "STATIC-REQUEST-ID-001"

    RATE_LIMIT_LIMIT = "1000"
    RATE_LIMIT_REMAINING = "1000"
    RATE_LIMIT_RESET = "0"

    ACCEPT = "application/json"
    CONTENT_TYPE = "application/json; charset=utf-8"

    API_VERSION = "v1"


# ---------------------------------------------------------------------------
# BUILDERS
# ---------------------------------------------------------------------------


def build_auth_headers():
    return {
        "Authorization": APIHeaderPolicy.AUTHORIZATION,
        "X-API-Key": APIHeaderPolicy.API_KEY,
        "X-Request-ID": APIHeaderPolicy.REQUEST_ID,
        "Accept": APIHeaderPolicy.ACCEPT,
        "Content-Type": APIHeaderPolicy.CONTENT_TYPE,
        "X-API-Version": APIHeaderPolicy.API_VERSION,
    }


def build_rate_headers(elapsed_ms=None):
    return {
        "X-Rate-Limit-Limit": APIHeaderPolicy.RATE_LIMIT_LIMIT,
        "X-Rate-Limit-Remaining": APIHeaderPolicy.RATE_LIMIT_REMAINING,
        "X-Rate-Limit-Reset": APIHeaderPolicy.RATE_LIMIT_RESET,
        "X-Response-Time": f"{elapsed_ms:.2f}ms" if elapsed_ms else "0ms",
    }


# ---------------------------------------------------------------------------
# REGISTER TO GLOBAL ORCHESTRATOR
# ---------------------------------------------------------------------------


def init_api_headers():

    def before():
        request.headers_context.update(build_auth_headers())

    def after(elapsed_ms):
        headers = build_rate_headers(elapsed_ms)
        headers["__module__"] = "api"

        return headers
    
    print(f"[DEBUG][api] using registry id={id(registry)} from module={registry.__class__.__module__}")

    registry.register(before=before, after=after)
