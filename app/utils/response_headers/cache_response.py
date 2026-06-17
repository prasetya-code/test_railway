"""
Cache Control Response Headers

Handles:

* Cache-Control
* Vary

NOTE:
- Server-side caching sudah ditangani oleh Flask-Caching (@fl_cache.cached)
- Module ini hanya mengatur HTTP cache behavior (browser/CDN layer)
"""

import traceback


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

NO_STORE = False
# Cache-Control: no-store
# Possible values:
# - True  -> cache tidak boleh disimpan sama sekali
# - False -> cache boleh disimpan sesuai policy lain
#
# Purpose:
# - Mencegah penyimpanan data sensitif di browser/CDN
#
# Security impact: HIGH

NO_CACHE = False
# Cache-Control: no-cache
# Possible values:
# - True  -> cache harus revalidate ke server
# - False -> cache normal behavior
#
# Purpose:
# - Memastikan data selalu divalidasi ulang

MUST_REVALIDATE = False
# Cache-Control: must-revalidate
# Possible values:
# - True  -> expired cache wajib revalidate
# - False -> tidak dipaksa revalidate
#
# Purpose:
# - Menjaga konsistensi data setelah expired cache

PUBLIC = False
# Cache-Control: public
# Possible values:
# - True  -> cache boleh di CDN + browser
# - False -> tidak public cache
#
# Purpose:
# - Mengizinkan caching di shared cache (CDN)

PRIVATE = True
# Cache-Control: private
# Possible values:
# - True  -> hanya browser user yang boleh cache
# - False -> tidak dibatasi private cache
#
# Purpose:
# - Mencegah caching di shared proxy/CDN

MAX_AGE = 60
# Cache-Control: max-age
# Possible values:
# - int (seconds) -> durasi cache di browser
# - None          -> tidak menggunakan max-age
#
# Purpose:
# - Mengontrol lifetime cache di client

S_MAXAGE = None
# Cache-Control: s-maxage
# Possible values:
# - int (seconds) -> CDN cache duration
# - None          -> tidak digunakan
#
# Purpose:
# - Override max-age khusus CDN layer

IMMUTABLE = False
# Cache-Control: immutable
# Possible values:
# - True  -> resource tidak berubah selama cache lifetime
# - False -> resource bisa berubah
#
# Purpose:
# - Optimasi asset static (CSS/JS versioned)

VARY = ["Accept-Encoding"]
# Vary
# Possible values:
# - list[str] -> header yang mempengaruhi variasi cache
# - None / []  -> tidak ada variasi
#
# Purpose:
# - Menentukan variasi response caching (gzip, brotli, dll)


# ---------------------------------------------------------------------------
# REMOVED / NOT NEEDED (handled by Flask-Caching or HTTP layer)
# ---------------------------------------------------------------------------

# Pragma is removed
# Reason:
# - Legacy HTTP/1.0 only

# Expires is removed
# Reason:
# - Digantikan Cache-Control: max-age

# Age is removed
# Reason:
# - Header CDN/proxy internal

# Clear-Site-Data is removed
# Reason:
# - Bukan caching layer (security/session)

# Observability headers removed
# Reason:
# - Bukan bagian cache policy


# ---------------------------------------------------------------------------
# CACHE CONTROL BUILDER
# ---------------------------------------------------------------------------


def build_cache_control_header():
    """
    Cache-Control

    Build HTTP caching behavior for browser/CDN layer.
    """

    try:
        directives = []

        if NO_STORE:
            directives.append("no-store")

        if NO_CACHE:
            directives.append("no-cache")

        if MUST_REVALIDATE:
            directives.append("must-revalidate")

        if PUBLIC:
            directives.append("public")
        elif PRIVATE:
            directives.append("private")

        if MAX_AGE is not None:
            directives.append(f"max-age={MAX_AGE}")

        if S_MAXAGE is not None:
            directives.append(f"s-maxage={S_MAXAGE}")

        if IMMUTABLE:
            directives.append("immutable")

        return {"Cache-Control": ", ".join(directives) if directives else "no-store"}

    except Exception:
        print("[ERROR][cache][cache_control] failed building header")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# VARY HEADER
# ---------------------------------------------------------------------------


def build_vary_header():
    """
    Vary

    Define cache variation rules.
    """

    try:
        if not VARY:
            return {}

        return {"Vary": ", ".join(VARY)}

    except Exception:
        print("[ERROR][cache][vary] failed building header")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# BUILDERS
# ---------------------------------------------------------------------------


def build_cache_headers():
    """
    Build all cache response headers.
    """

    try:
        headers = {
            **build_cache_control_header(),
            **build_vary_header(),
        }

        print(f"[CACHE HEADERS][final] headers={headers}")

        return headers

    except Exception:
        print("[ERROR][cache][build] failed building cache headers")

        traceback.print_exc()

        return {}


# ---------------------------------------------------------------------------
# APPLY TO RESPONSE
# ---------------------------------------------------------------------------


def apply_cache_headers(response):
    """
    Apply cache headers to Flask response.
    """

    try:
        response.headers.update(build_cache_headers())

        return response

    except Exception:
        print("[ERROR][cache][apply] failed applying cache headers")

        traceback.print_exc()

        return response
