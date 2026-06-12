"""
CORS (Cross-Origin Resource Sharing) Headers Policy

Handles:
- Access-Control-Allow-Origin
- Access-Control-Allow-Methods
- Access-Control-Allow-Headers
- Access-Control-Expose-Headers
- Access-Control-Allow-Credentials
- Access-Control-Max-Age
- Origin validation
"""

from app.utils.headers import registry


# ---------------------------------------------------------------------------
# POLICY LAYER
# ---------------------------------------------------------------------------


class CORSHeaderPolicy:
    ALLOW_ALL_ORIGINS = False
    ALLOWED_ORIGINS = []

    ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    ALLOWED_REQUEST_HEADERS = [
        "Accept",
        "Authorization",
        "Content-Type",
        "Origin",
        "X-Requested-With",
        "X-API-Key",
        "X-Request-ID",
    ]

    EXPOSED_HEADERS = [
        "Content-Type",
        "Content-Length",
        "ETag",
        "X-Request-ID",
        "X-Rate-Limit-Limit",
        "X-Rate-Limit-Remaining",
        "X-Rate-Limit-Reset",
    ]

    ALLOW_CREDENTIALS = False
    PREFLIGHT_MAX_AGE = 600


# ---------------------------------------------------------------------------
# BUILDERS
# ---------------------------------------------------------------------------


def build_allow_origin_header(allowed_origins, request_origin, allow_all):
    if allow_all:
        return {"Access-Control-Allow-Origin": "*"}

    if request_origin and request_origin in allowed_origins:
        return {
            "Access-Control-Allow-Origin": request_origin,
            "Vary": "Origin",
        }

    if not request_origin and allowed_origins:
        return {
            "Access-Control-Allow-Origin": allowed_origins[0],
            "Vary": "Origin",
        }

    return {}


def build_allow_methods_header(methods):
    if not methods:
        return {}

    return {"Access-Control-Allow-Methods": ", ".join(m.upper() for m in methods)}


def build_allow_headers_header(headers):
    if not headers:
        return {}

    return {"Access-Control-Allow-Headers": ", ".join(headers)}


def build_expose_headers_header(headers):
    if not headers:
        return {}

    return {"Access-Control-Expose-Headers": ", ".join(headers)}


def build_allow_credentials_header(allow):
    return {"Access-Control-Allow-Credentials": "true" if allow else "false"}


def build_max_age_header(max_age):
    return {"Access-Control-Max-Age": str(max_age)}


def build_observability_headers(elapsed_ms):
    return {"X-Response-Time": f"{elapsed_ms:.2f}ms"}


# ---------------------------------------------------------------------------
# PLUGIN INITIALIZER (NO ORCHESTRATOR)
# ---------------------------------------------------------------------------


def init_cors_headers():

    def before():
        return {"cors_origin": None}

    def after(request, elapsed_ms):

        origin = request.headers.get("Origin")

        headers = {}

        if request.method == "OPTIONS":
            headers.update(
                build_allow_origin_header(
                    CORSHeaderPolicy.ALLOWED_ORIGINS,
                    origin,
                    CORSHeaderPolicy.ALLOW_ALL_ORIGINS,
                )
            )

            headers.update(build_allow_methods_header(CORSHeaderPolicy.ALLOWED_METHODS))

            headers.update(
                build_allow_headers_header(CORSHeaderPolicy.ALLOWED_REQUEST_HEADERS)
            )

            headers.update(
                build_allow_credentials_header(CORSHeaderPolicy.ALLOW_CREDENTIALS)
            )

            headers.update(build_max_age_header(CORSHeaderPolicy.PREFLIGHT_MAX_AGE))

        else:
            headers.update(
                build_allow_origin_header(
                    CORSHeaderPolicy.ALLOWED_ORIGINS,
                    origin,
                    CORSHeaderPolicy.ALLOW_ALL_ORIGINS,
                )
            )

            headers.update(build_allow_methods_header(CORSHeaderPolicy.ALLOWED_METHODS))

            headers.update(
                build_allow_headers_header(CORSHeaderPolicy.ALLOWED_REQUEST_HEADERS)
            )

            headers.update(
                build_expose_headers_header(CORSHeaderPolicy.EXPOSED_HEADERS)
            )

            headers.update(
                build_allow_credentials_header(CORSHeaderPolicy.ALLOW_CREDENTIALS)
            )

        headers.update(build_observability_headers(elapsed_ms))

        headers["__module__"] = "cors"

        return headers
    
    print(f"[DEBUG][cors] using registry id={id(registry)} from module={registry.__class__.__module__}")

    registry.register(before=before, after=after)
