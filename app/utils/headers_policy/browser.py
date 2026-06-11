"""
Browser Behavior Headers Policy

Handles:
- MIME sniffing protection (X-Content-Type-Options)
- Clickjacking protection (X-Frame-Options)
- Legacy XSS protection (X-XSS-Protection)
- DNS prefetch control (X-DNS-Prefetch-Control)
- Download behavior protection (X-Download-Options)
- Cross-domain policy control (X-Permitted-Cross-Domain-Policies)
- Content-Type enforcement (Content-Type)
- Range request support (Accept-Ranges)
"""

from _headers import registry
from flask import request


# ---------------------------------------------------------------------------
# POLICY LAYER
# ---------------------------------------------------------------------------

class BrowserHeaderPolicy:

    NOSNIFF = True
    FRAME_POLICY = "DENY"
    XSS_PROTECTION = False
    DNS_PREFETCH = False
    DOWNLOAD_OPTIONS = True
    CROSS_DOMAIN_POLICY = "none"

    MIME_TYPE = "text/html"
    CHARSET = "utf-8"

    ACCEPT_RANGES = "bytes"


# ---------------------------------------------------------------------------
# BUILDERS
# (tetap dipakai tapi tidak lagi orchestration)
# ---------------------------------------------------------------------------

def build_content_type_options_header():
    return {
        "X-Content-Type-Options": "nosniff" if BrowserHeaderPolicy.NOSNIFF else ""
    }


def build_frame_options_header():
    return {
        "X-Frame-Options": BrowserHeaderPolicy.FRAME_POLICY
    }


def build_xss_protection_header():
    return {
        "X-XSS-Protection": "1; mode=block"
        if BrowserHeaderPolicy.XSS_PROTECTION
        else "0"
    }


def build_dns_prefetch_control_header():
    return {
        "X-DNS-Prefetch-Control": "on"
        if BrowserHeaderPolicy.DNS_PREFETCH
        else "off"
    }


def build_download_options_header():
    return {"X-Download-Options": "noopen"}


def build_cross_domain_policy_header():
    return {
        "X-Permitted-Cross-Domain-Policies": BrowserHeaderPolicy.CROSS_DOMAIN_POLICY
    }


def build_content_type_header(mime_type, charset):
    binary_types = {
        "image/",
        "audio/",
        "video/",
        "application/octet-stream",
    }

    is_binary = any(mime_type.startswith(p) for p in binary_types)

    value = mime_type if is_binary else f"{mime_type}; charset={charset}"

    return {"Content-Type": value}


def build_accept_ranges_header():
    return {"Accept-Ranges": BrowserHeaderPolicy.ACCEPT_RANGES}


def build_observability_headers(elapsed_ms):
    return {"X-Response-Time": f"{elapsed_ms:.2f}ms"}


# ---------------------------------------------------------------------------
# PLUGIN REGISTRATION (NO ORCHESTRATOR)
# ---------------------------------------------------------------------------

def init_browser_headers():

    def before():
        request.browser_context = {
            **build_content_type_options_header(),
            **build_frame_options_header(),
            **build_xss_protection_header(),
            **build_dns_prefetch_control_header(),
            **build_cross_domain_policy_header(),
        }

    def after(elapsed_ms):
        headers = {
            **build_content_type_header(
                BrowserHeaderPolicy.MIME_TYPE,
                BrowserHeaderPolicy.CHARSET,
            ),
            **build_accept_ranges_header(),
            **build_observability_headers(elapsed_ms),
        }

        if BrowserHeaderPolicy.DOWNLOAD_OPTIONS:
            headers.update(build_download_options_header())

        return headers

    registry.register(before=before, after=after)