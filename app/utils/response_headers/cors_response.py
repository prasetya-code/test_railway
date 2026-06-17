"""
CORS (Cross-Origin Resource Sharing) Response Headers Policy

Handles:

* Access-Control-Allow-Origin
* Access-Control-Allow-Methods
* Access-Control-Allow-Headers
* Access-Control-Expose-Headers
* Access-Control-Allow-Credentials
* Access-Control-Max-Age

NOTE:
- This module is designed to WORK WITH flask-cors, not replace it.
- Avoid duplication with Flask-CORS internal header handling.
"""

import traceback


# ---------------------------------------------------------------------------
# CONFIGURATION (SYNC WITH flask-cors)
# ---------------------------------------------------------------------------

ALLOW_ALL_ORIGINS = False
# NOTE:
# - If using flask-cors with origins="*"
#   set this to False to avoid duplicate override

ALLOWED_ORIGINS = []
# NOTE:
# - Should match flask-cors origins config if used

ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
# NOTE:
# - flask-cors already handles this if configured globally
# - kept here ONLY for documentation consistency

ALLOWED_REQUEST_HEADERS = [
    "Accept",
    "Authorization",
    "Content-Type",
    "Origin",
    "X-Requested-With",
    "X-API-Key",
    "X-Request-ID",
]
# NOTE:
# - If flask-cors is used, this should match allow_headers config

EXPOSED_HEADERS = [
    "Content-Type",
    "Content-Length",
    "ETag",
    "X-Request-ID",
    "X-Rate-Limit-Limit",
    "X-Rate-Limit-Remaining",
    "X-Rate-Limit-Reset",
]
# NOTE:
# - SAFE to keep here even with flask-cors

ALLOW_CREDENTIALS = False
# NOTE:
# - MUST match flask-cors supports_credentials config

PREFLIGHT_MAX_AGE = 600
# NOTE:
# - Can be controlled either here or flask-cors max_age (avoid double source of truth)


# ---------------------------------------------------------------------------
# ORIGIN VALIDATION (OPTIONAL LAYER ONLY)
# ---------------------------------------------------------------------------


def is_origin_allowed(origin):
    """
    Optional validation layer (NOT replacement for flask-cors).
    """

    try:
        if not origin:
            return False

        if ALLOW_ALL_ORIGINS:
            return True

        return origin in ALLOWED_ORIGINS

    except Exception:
        print("[ERROR][cors][origin_check] failed")
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# BUILDERS (SAFE WITH flask-cors)
# ---------------------------------------------------------------------------


def build_expose_headers_header():
    """
    Access-Control-Expose-Headers

    NOTE:
    Safe to apply even when using flask-cors.
    flask-cors does NOT always enforce expose headers globally.
    """

    try:
        if not EXPOSED_HEADERS:
            return {}

        return {"Access-Control-Expose-Headers": ", ".join(EXPOSED_HEADERS)}

    except Exception:
        print("[ERROR][cors][expose_headers] failed")
        traceback.print_exc()
        return {}


def build_allow_credentials_header():
    """
    Access-Control-Allow-Credentials

    NOTE:
    Should MATCH flask-cors config (do not conflict).
    """

    try:
        return {
            "Access-Control-Allow-Credentials": "true" if ALLOW_CREDENTIALS else "false"
        }

    except Exception:
        print("[ERROR][cors][credentials] failed")
        traceback.print_exc()
        return {}


def build_max_age_header():
    """
    Access-Control-Max-Age

    NOTE:
    Preflight caching (OPTIONS optimization).
    Still relevant even with flask-cors.
    """

    try:
        return {"Access-Control-Max-Age": str(PREFLIGHT_MAX_AGE)}

    except Exception:
        print("[ERROR][cors][max_age] failed")
        traceback.print_exc()
        return {}


# ---------------------------------------------------------------------------
# MAIN BUILDER (MINIMAL OVERRIDE STRATEGY)
# ---------------------------------------------------------------------------


def build_cors_headers(request_obj):
    """
    Build ONLY safe supplemental CORS headers.

    IMPORTANT:
    We do NOT override:
    - Allow-Origin
    - Allow-Methods
    - Allow-Headers

    Because those are handled by flask-cors.
    """

    try:
        # origin = request_obj.headers.get("Origin")

        headers = {}

        # ---------------------------------------------------------
        # SAFE: credentials sync layer
        # ---------------------------------------------------------
        headers.update(build_allow_credentials_header())

        # ---------------------------------------------------------
        # SAFE: expose headers (not always enforced by flask-cors)
        # ---------------------------------------------------------
        if request_obj.method != "OPTIONS":
            headers.update(build_expose_headers_header())

        # ---------------------------------------------------------
        # SAFE: preflight optimization
        # ---------------------------------------------------------
        if request_obj.method == "OPTIONS":
            headers.update(build_max_age_header())

        # ---------------------------------------------------------
        # DEBUG LOG (keep for tracing)
        # ---------------------------------------------------------
        print(f"[CORS HEADERS][final] method={request_obj.method} headers={headers}")

        return headers

    except Exception:
        print("[ERROR][cors][build] failed")
        traceback.print_exc()
        return {}


# ---------------------------------------------------------------------------
# APPLY TO RESPONSE
# ---------------------------------------------------------------------------


def apply_cors_headers(response, request_obj):
    """
    Apply SAFE CORS extension headers only.
    """

    try:
        response.headers.update(build_cors_headers(request_obj))

        return response

    except Exception:
        print("[ERROR][cors][apply] failed")
        traceback.print_exc()
        return response
