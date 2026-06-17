"""
Browser Behavior Response Headers

Handles:

* X-Content-Type-Options
* X-Frame-Options
* X-XSS-Protection
* X-DNS-Prefetch-Control
* X-Download-Options
* X-Permitted-Cross-Domain-Policies

NOTE: Some headers are handled automatically by Flask/Werkzeug and should NOT be overridden here.
"""

import traceback


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

NOSNIFF = True
# X-Content-Type-Options: nosniff
# Purpose:
# - Mencegah browser melakukan MIME type sniffing
# - Memaksa browser mengikuti Content-Type dari server
#
# Security impact: HIGH (recommended ON)

FRAME_POLICY = "DENY"
# X-Frame-Options
# Possible values:
# - DENY  -> tidak boleh di-embed iframe sama sekali
# - SAMEORIGIN -> hanya domain yang sama boleh embed
#
# Purpose:
# - Mencegah clickjacking attack
# Security impact: HIGH (recommended DENY)

XSS_PROTECTION = False
# X-XSS-Protection
# Possible values:
# - 1; mode=block (enable legacy XSS filter)
# - 0 (disable)
#
# NOTE:
# - Sudah deprecated di modern browser (Chrome/Edge/Firefox)
# - Tetap dipertahankan hanya untuk legacy support
# Security impact: LOW / LEGACY ONLY

DNS_PREFETCH = False
# X-DNS-Prefetch-Control
# Possible values:
# - on  -> browser boleh pre-resolve domain DNS
# - off -> disable DNS prefetching
#
# Purpose:
# - Mengurangi tracking / speculative DNS lookup
# - Sedikit meningkatkan privacy
#
# Security impact: LOW / PRIVACY

DOWNLOAD_OPTIONS = True
# X-Download-Options
# Possible values:
# - noopen (mencegah file download langsung dieksekusi di IE)
#
# Purpose:
# - Proteksi legacy browser (Internet Explorer)
#
# Security impact: LOW / LEGACY ONLY

CROSS_DOMAIN_POLICY = "none"
# X-Permitted-Cross-Domain-Policies
# Possible values:
# - none
# - master-only
# - by-content-type
# - all
#
# Purpose:
# - Mengontrol akses cross-domain policy files (Flash/PDF legacy system)
#
# Security impact: LOW / LEGACY SYSTEM ONLY


# ---------------------------------------------------------------------------
# REMOVED / NOT NEEDED (handled by Flask automatically)
# ---------------------------------------------------------------------------

# Content-Type is handled automatically by Flask/Werkzeug
# Reason:
# - jsonify() sets application/json automatically
# - send_file() sets MIME type automatically
# - Response() respects explicit content type per endpoint

# Accept-Ranges is handled automatically by Flask/Werkzeug in file-based responses
# Reason:
# - send_file() supports Range requests automatically
# - Werkzeug handles 206 Partial Content responses
# - Not relevant for normal API responses (JSON, REST)


# ---------------------------------------------------------------------------
# MIME SNIFFING PROTECTION
# ---------------------------------------------------------------------------


def build_content_type_options_headers():
    """
    X-Content-Type-Options

    Prevent MIME type sniffing.
    """

    try:
        return {"X-Content-Type-Options": "nosniff" if NOSNIFF else ""}

    except Exception:
        print("[ERROR][browser][content_type_options] failed building header")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# CLICKJACKING PROTECTION
# ---------------------------------------------------------------------------


def build_frame_options_headers():
    """
    X-Frame-Options

    Protect against clickjacking.
    """

    try:
        return {"X-Frame-Options": FRAME_POLICY}

    except Exception:
        print("[ERROR][browser][frame_options] failed building header")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# LEGACY XSS PROTECTION (DEPRECATED)
# ---------------------------------------------------------------------------


def build_xss_protection_headers():
    """
    X-XSS-Protection

    NOTE:
    Deprecated in modern browsers (Chrome, Edge, Firefox ignore this header).
    Kept only for legacy compatibility.
    """

    try:
        return {"X-XSS-Protection": "1; mode=block" if XSS_PROTECTION else "0"}

    except Exception:
        print("[ERROR][browser][xss_protection] failed building header")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# DNS PREFETCH CONTROL (PARTIALLY OBSOLETE)
# ---------------------------------------------------------------------------


def build_dns_prefetch_headers():
    """
    X-DNS-Prefetch-Control

    NOTE:
    Modern browsers may ignore or override this based on user settings.
    """

    try:
        return {"X-DNS-Prefetch-Control": "on" if DNS_PREFETCH else "off"}

    except Exception:
        print("[ERROR][browser][dns_prefetch] failed building header")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# DOWNLOAD OPTIONS
# ---------------------------------------------------------------------------


def build_download_options_headers():
    """
    X-Download-Options

    Protect download behavior (mainly legacy IE support).
    """

    try:
        return {"X-Download-Options": "noopen"}

    except Exception:
        print("[ERROR][browser][download_options] failed building header")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# CROSS DOMAIN POLICY
# ---------------------------------------------------------------------------


def build_cross_domain_policy_headers():
    """
    X-Permitted-Cross-Domain-Policies

    Restrict legacy cross-domain policy (Flash/PDF systems).
    """

    try:
        return {"X-Permitted-Cross-Domain-Policies": CROSS_DOMAIN_POLICY}

    except Exception:
        print("[ERROR][browser][cross_domain_policy] failed building header")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# BUILDERS
# ---------------------------------------------------------------------------


def build_browser_headers():
    """
    Build all browser response headers.
    """

    try:
        headers = {
            **build_content_type_options_headers(),
            **build_frame_options_headers(),
            **build_xss_protection_headers(),
            **build_dns_prefetch_headers(),
            **build_cross_domain_policy_headers(),
        }

        # REMOVED:
        # Accept-Ranges header builder
        #
        # REASON:
        # - Handled automatically by Flask/Werkzeug
        # - Only relevant for send_file / streaming responses
        # - Not part of browser security headers scope

        if DOWNLOAD_OPTIONS:
            headers.update(build_download_options_headers())

        print(f"[BROWSER HEADERS][final] headers={headers}")

        return headers

    except Exception:
        print("[ERROR][browser][build] failed building browser headers")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# APPLY TO RESPONSE
# ---------------------------------------------------------------------------


def apply_browser_headers(response):
    """
    Apply browser headers to Flask response.
    """

    try:
        headers = build_browser_headers()

        print(f"[BROWSER HEADERS][apply] applying {len(headers)} headers")

        response.headers.update(headers)

        return response

    except Exception:
        print("[ERROR][browser][apply] failed applying browser headers")

        traceback.print_exc()

        return response
