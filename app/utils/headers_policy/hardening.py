"""
General Hardening Headers Policy

Handles:
- Referrer-Policy (navigation privacy control)
- Permissions-Policy (browser feature restrictions)
- Server header masking (fingerprinting reduction)
- X-Powered-By removal (framework hiding)
- Expect-CT (legacy certificate transparency enforcement)

Notes:
- COOP / COEP / CORP handled in isolation module
- HSTS handled in transport module
- CSP handled separately
"""


from flask import request
import time


# ---------------------------------------------------------------------------
# POLICY LAYER
# Central configuration for hardening behavior
# ---------------------------------------------------------------------------

class HardeningHeaderPolicy:

    # Referrer policy
    REFERRER_POLICY = "strict-origin-when-cross-origin"

    # Server fingerprinting
    MASK_SERVER = True
    SERVER_VALUE = ""

    # Framework fingerprinting
    REMOVE_POWERED_BY = True
    POWERED_BY_VALUE = ""

    # Expect-CT
    EXPECT_CT_MAX_AGE = 86400
    EXPECT_CT_ENFORCE = False
    EXPECT_CT_REPORT_URI = None

    # Permissions presets
    PERMISSIONS_PRESET = None  # deny_all | self_only


# ---------------------------------------------------------------------------
# HEADER BUILDERS
# Each function handles a single hardening directive
# ---------------------------------------------------------------------------

def build_referrer_policy_header(policy):
    return {
        "Referrer-Policy": policy
    }


def build_permissions_policy_header(preset, extra=None):
    feature_map = extra or {}

    directives = []

    for feature, sources in feature_map.items():

        if sources is None:
            continue

        if sources == []:
            directives.append(f"{feature}=()")
        else:
            formatted = " ".join(
                f'"{s}"' if s not in ("self", "*") else s
                for s in sources
            )
            directives.append(f"{feature}=({formatted})")

    return {
        "Permissions-Policy": ", ".join(directives)
    } if directives else {}


def build_server_header(mask, value):
    if mask:
        return {"Server": value}
    return {}


def build_powered_by_header(remove, value):
    if remove:
        return {"X-Powered-By": value}
    return {}


def build_expect_ct_header(max_age, enforce, report_uri):
    parts = [f"max-age={max_age}"]

    if enforce:
        parts.append("enforce")

    if report_uri:
        parts.append(f'report-uri="{report_uri}"')

    return {
        "Expect-CT": ", ".join(parts)
    }


def build_observability_headers(elapsed_ms):
    return {
        "X-Response-Time": f"{elapsed_ms:.2f}ms"
    }


# ---------------------------------------------------------------------------
# PRESETS
# Common hardening configurations
# ---------------------------------------------------------------------------

def preset_deny_all_permissions():
    return {
        "camera": [],
        "microphone": [],
        "geolocation": [],
        "payment": [],
        "usb": [],
        "bluetooth": [],
        "display-capture": [],
        "fullscreen": [],
        "autoplay": [],
        "clipboard-read": [],
        "clipboard-write": [],
        "accelerometer": [],
        "gyroscope": [],
        "magnetometer": [],
        "ambient-light-sensor": [],
        "picture-in-picture": [],
        "web-share": [],
        "midi": [],
    }


def preset_self_permissions():
    self_src = ["self"]

    return {
        "camera": self_src,
        "microphone": self_src,
        "geolocation": self_src,
        "payment": self_src,
        "usb": self_src,
        "display-capture": self_src,
        "fullscreen": self_src,
        "autoplay": self_src,
        "clipboard-read": self_src,
        "clipboard-write": self_src,
    }


# ---------------------------------------------------------------------------
# ORCHESTRATOR
# Controls request lifecycle hooks (before/after request)
# ---------------------------------------------------------------------------

class HardeningHeaderOrchestrator:

    def __init__(self, app):
        self.app = app
        self.start_time = None

    def before_request(self):
        """
        Called before request processing.
        """

        self.start_time = time.perf_counter()

        request.hardening_context = {}

    def after_request(self, response):
        """
        Called after response generation.
        """

        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        headers = {}

        # Referrer Policy
        headers.update(
            build_referrer_policy_header(
                HardeningHeaderPolicy.REFERRER_POLICY
            )
        )

        # Permissions Policy
        if HardeningHeaderPolicy.PERMISSIONS_PRESET == "deny_all":
            permissions = preset_deny_all_permissions()

        elif HardeningHeaderPolicy.PERMISSIONS_PRESET == "self_only":
            permissions = preset_self_permissions()

        else:
            permissions = {}

        headers.update(
            build_permissions_policy_header(
                HardeningHeaderPolicy.PERMISSIONS_PRESET,
                permissions,
            )
        )

        # Fingerprinting protection
        headers.update(
            build_server_header(
                HardeningHeaderPolicy.MASK_SERVER,
                HardeningHeaderPolicy.SERVER_VALUE,
            )
        )

        headers.update(
            build_powered_by_header(
                HardeningHeaderPolicy.REMOVE_POWERED_BY,
                HardeningHeaderPolicy.POWERED_BY_VALUE,
            )
        )

        # Expect CT
        headers.update(
            build_expect_ct_header(
                HardeningHeaderPolicy.EXPECT_CT_MAX_AGE,
                HardeningHeaderPolicy.EXPECT_CT_ENFORCE,
                HardeningHeaderPolicy.EXPECT_CT_REPORT_URI,
            )
        )

        # Observability
        headers.update(
            build_observability_headers(elapsed_ms)
        )

        for key, value in headers.items():
            response.headers[key] = value

        return response


# ---------------------------------------------------------------------------
# REGISTRATION ENTRY POINT
# Used in application bootstrap (register_utils)
# ---------------------------------------------------------------------------

def register_hardening_headers(app):
    """
    Initialize browser hardening middleware system.

    Usage:
        register_hardening_headers(app)
    """

    orchestrator = HardeningHeaderOrchestrator(app)

    app.before_request(orchestrator.before_request)
    app.after_request(orchestrator.after_request)

    return orchestrator