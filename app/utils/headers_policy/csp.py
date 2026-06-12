"""
Content Security Policy (CSP) Headers Policy

Handles:
- Content-Security-Policy (enforce mode)
- Content-Security-Policy-Report-Only (monitoring mode)
- Fetch directives
- Navigation directives
- Document directives
- Reporting
- Trusted Types
"""

from app.utils.headers import registry


# ---------------------------------------------------------------------------
# POLICY LAYER
# ---------------------------------------------------------------------------


class CSPHeaderPolicy:
    REPORT_ONLY = False

    DEFAULT_SRC = ["'self'"]
    SCRIPT_SRC = ["'self'"]
    STYLE_SRC = ["'self'"]
    IMG_SRC = ["'self'"]
    FONT_SRC = ["'self'"]
    CONNECT_SRC = ["'self'"]
    MEDIA_SRC = ["'none'"]
    OBJECT_SRC = ["'none'"]
    FRAME_SRC = ["'none'"]
    WORKER_SRC = ["'self'"]

    FORM_ACTION = ["'self'"]
    FRAME_ANCESTORS = ["'none'"]

    BASE_URI = ["'self'"]
    SANDBOX = None

    REPORT_URI = None
    REPORT_TO = None

    TRUSTED_TYPES = None

    PRESET = None  # strict | api | None


# ---------------------------------------------------------------------------
# BUILDERS
# ---------------------------------------------------------------------------


def build_directives(mapping):
    directives = {}

    for key, value in mapping.items():
        if value is not None:
            directives[key] = value

    return directives


def build_fetch_directives():
    return build_directives(
        {
            "default-src": CSPHeaderPolicy.DEFAULT_SRC,
            "script-src": CSPHeaderPolicy.SCRIPT_SRC,
            "style-src": CSPHeaderPolicy.STYLE_SRC,
            "img-src": CSPHeaderPolicy.IMG_SRC,
            "font-src": CSPHeaderPolicy.FONT_SRC,
            "connect-src": CSPHeaderPolicy.CONNECT_SRC,
            "media-src": CSPHeaderPolicy.MEDIA_SRC,
            "object-src": CSPHeaderPolicy.OBJECT_SRC,
            "frame-src": CSPHeaderPolicy.FRAME_SRC,
            "worker-src": CSPHeaderPolicy.WORKER_SRC,
        }
    )


def build_navigation_directives():
    return build_directives(
        {
            "form-action": CSPHeaderPolicy.FORM_ACTION,
            "frame-ancestors": CSPHeaderPolicy.FRAME_ANCESTORS,
        }
    )


def build_document_directives():
    return build_directives(
        {
            "base-uri": CSPHeaderPolicy.BASE_URI,
            "sandbox": CSPHeaderPolicy.SANDBOX,
        }
    )


def build_reporting_directives():
    return build_directives(
        {
            "report-uri": CSPHeaderPolicy.REPORT_URI,
            "report-to": CSPHeaderPolicy.REPORT_TO,
        }
    )


def build_trusted_types_directive():
    if not CSPHeaderPolicy.TRUSTED_TYPES:
        return {}

    return {"trusted-types": " ".join(CSPHeaderPolicy.TRUSTED_TYPES)}


# ---------------------------------------------------------------------------
# ASSEMBLER
# ---------------------------------------------------------------------------


def assemble_csp_policy(directives):
    parts = []

    for directive, value in directives.items():
        if isinstance(value, list):
            parts.append(f"{directive} {' '.join(value)}")

        elif isinstance(value, str):
            parts.append(f"{directive} {value}")

    return "; ".join(parts)


def build_csp_header(policy):
    key = (
        "Content-Security-Policy-Report-Only"
        if CSPHeaderPolicy.REPORT_ONLY
        else "Content-Security-Policy"
    )

    return {key: policy}


# ---------------------------------------------------------------------------
# PRESETS
# ---------------------------------------------------------------------------


def preset_strict():
    return assemble_csp_policy(
        {
            "default-src": ["'self'"],
            "script-src": ["'strict-dynamic'", "'self'"],
            "style-src": ["'self'", "'unsafe-inline'"],
            "img-src": ["'self'", "data:", "https:"],
            "font-src": ["'self'"],
            "connect-src": ["'self'"],
            "media-src": ["'none'"],
            "object-src": ["'none'"],
            "frame-src": ["'none'"],
            "worker-src": ["'self'"],
            "form-action": ["'self'"],
            "frame-ancestors": ["'none'"],
            "base-uri": ["'self'"],
        }
    )


def preset_api():
    return assemble_csp_policy(
        {
            "default-src": ["'none'"],
            "form-action": ["'none'"],
            "frame-ancestors": ["'none'"],
            "base-uri": ["'none'"],
        }
    )


# ---------------------------------------------------------------------------
# PLUGIN INITIALIZER (NO ORCHESTRATOR)
# ---------------------------------------------------------------------------


def init_csp_headers():

    def before():
        return {"csp_context": {}}

    def after(request, elapsed_ms):

        if CSPHeaderPolicy.PRESET == "strict":
            policy = preset_strict()

        elif CSPHeaderPolicy.PRESET == "api":
            policy = preset_api()

        else:
            directives = {
                **build_fetch_directives(),
                **build_navigation_directives(),
                **build_document_directives(),
                **build_reporting_directives(),
                **build_trusted_types_directive(),
            }

            policy = assemble_csp_policy(directives)

        headers = build_csp_header(policy)

        headers.update({"X-Response-Time": f"{elapsed_ms:.2f}ms"})

        headers["__module__"] = "csp"

        return headers
    
    print(f"[DEBUG][csp] using registry id={id(registry)} from module={registry.__class__.__module__}")

    registry.register(before=before, after=after)
