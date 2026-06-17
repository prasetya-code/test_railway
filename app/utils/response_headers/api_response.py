"""
API Metadata Response Headers

Handles:

* X-Request-ID
* X-Correlation-ID
* X-API-Version
* Deprecation
* Sunset
"""

import uuid
import traceback

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
API_VERSION = "v1"

# ---------------------------------------------------------------------------
# OPTIONAL API LIFECYCLE HEADERS
# ---------------------------------------------------------------------------
# Deprecation: Indicates that an API endpoint is deprecated.
# Format:
#   True | None

DEPRECATION = None

# Sunset: Indicates when an API endpoint will be retired.
# Format:
#   Day, DD Mon YYYY HH:MM:SS GMT | None
#
# Examples:
#   "Fri, 01 Jan 2027 00:00:00 GMT"
#   "Mon, 30 Jun 2026 12:00:00 GMT"

SUNSET = None

# ---------------------------------------------------------------------------
# OPTIONAL RATE LIMIT HEADERS
# ---------------------------------------------------------------------------
# Jika rate limit sudah diterapkan maka tidak perlu set rate limit statis di headers


# ---------------------------------------------------------------------------
# REQUEST TRACKING
# ---------------------------------------------------------------------------


def build_request_tracking_headers():
    """
    Request tracing headers.

    X-Request-ID:
        Unique identifier for a single request.

    X-Correlation-ID:
        Used to trace requests across multiple services.
    """

    try:
        correlation_id = str(uuid.uuid4())

        return {
            "X-Request-ID": correlation_id,
            "X-Correlation-ID": correlation_id,
        }

    except Exception:
        print("[ERROR][api][request_tracking] failed building request tracking headers")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# API VERSIONING
# ---------------------------------------------------------------------------


def build_version_headers():
    """
    API version metadata.
    """

    try:
        return {
            "X-API-Version": API_VERSION,
        }

    except Exception:
        print("[ERROR][api][version] failed building version headers")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# API LIFECYCLE
# ---------------------------------------------------------------------------


def build_lifecycle_headers():
    """
    API lifecycle metadata.

    Deprecation:
        Indicates that an API endpoint is deprecated.

    Sunset:
        Indicates when the endpoint will be retired.
    """

    try:
        headers = {}

        if DEPRECATION is not None:
            headers["Deprecation"] = str(DEPRECATION)

        if SUNSET is not None:
            headers["Sunset"] = str(SUNSET)

        return headers

    except Exception:
        print("[ERROR][api][lifecycle] failed building lifecycle headers")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# BUILDERS
# ---------------------------------------------------------------------------


def build_api_headers():
    """
    Build all API response headers.
    """

    try:
        headers = {
            # unpack all value (**)
            **build_request_tracking_headers(),
            **build_version_headers(),
            **build_lifecycle_headers(),
        }

        print(f"[API HEADERS][final] headers={headers}")

        return headers

    except Exception:
        print("[ERROR][api][build] failed building api headers")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# APPLY TO RESPONSE
# ---------------------------------------------------------------------------


def apply_api_headers(response):
    """
    Apply API headers to Flask response.
    """

    try:
        headers = build_api_headers()

        print(f"[API HEADERS][apply] applying {len(headers)} headers")

        response.headers.update(headers)

        return response

    except Exception:
        print("[ERROR][api][apply] failed applying api headers")

        traceback.print_exc()

        return response
