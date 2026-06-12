"""
Cache Control Headers Policy

Handles:
- Cache-Control (strategi caching utama)
- Pragma (legacy cache control)
- Expires (HTTP/1.0 compatibility)
- ETag (cache validation)
- Last-Modified (conditional request)
- Vary (cache variation rules)
- Age (CDN/proxy cache age)
- Clear-Site-Data (reset client cache/session data)
"""

from app.utils.headers import registry


# ---------------------------------------------------------------------------
# POLICY LAYER
# ---------------------------------------------------------------------------


class CacheHeaderPolicy:
    NO_STORE = False
    NO_CACHE = False
    MUST_REVALIDATE = False
    PUBLIC = False
    PRIVATE = True

    MAX_AGE = None
    S_MAXAGE = None

    IMMUTABLE = False
    STALE_WHILE_REVALIDATE = None
    STALE_IF_ERROR = None

    PRAGMA_NO_CACHE = False

    VARY = None
    AGE_SECONDS = None

    CLEAR_CACHE = False
    CLEAR_COOKIES = False
    CLEAR_STORAGE = False


# ---------------------------------------------------------------------------
# BUILDERS (tetap dipakai)
# ---------------------------------------------------------------------------


def build_cache_control_header(
    no_store=False,
    no_cache=False,
    must_revalidate=False,
    public=False,
    private=True,
    max_age=None,
    s_maxage=None,
    immutable=False,
    stale_while_revalidate=None,
    stale_if_error=None,
):
    directives = []

    if no_store:
        directives.append("no-store")

    if no_cache:
        directives.append("no-cache")

    if must_revalidate:
        directives.append("must-revalidate")

    if public:
        directives.append("public")
    elif private:
        directives.append("private")

    if max_age is not None:
        directives.append(f"max-age={max_age}")

    if s_maxage is not None:
        directives.append(f"s-maxage={s_maxage}")

    if immutable:
        directives.append("immutable")

    if stale_while_revalidate is not None:
        directives.append(f"stale-while-revalidate={stale_while_revalidate}")

    if stale_if_error is not None:
        directives.append(f"stale-if-error={stale_if_error}")

    return {"Cache-Control": ", ".join(directives) if directives else "no-store"}


def build_pragma_header(no_cache=True):
    return {"Pragma": "no-cache" if no_cache else ""}


def build_expires_header(expires_at=None):
    if expires_at is None:
        return {"Expires": "0"}

    return {"Expires": expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT")}


def build_vary_header(headers):
    if not headers:
        return {}

    return {"Vary": ", ".join(headers)}


def build_age_header(age_seconds):
    return {"Age": str(age_seconds)}


def build_clear_site_data_header(
    cache=True,
    cookies=False,
    storage=False,
    execution_contexts=False,
):
    targets = []

    if cache:
        targets.append('"cache"')

    if cookies:
        targets.append('"cookies"')

    if storage:
        targets.append('"storage"')

    if execution_contexts:
        targets.append('"executionContexts"')

    if not targets:
        return {}

    return {"Clear-Site-Data": ", ".join(targets)}


def build_observability_headers(elapsed_ms):
    return {"X-Response-Time": f"{elapsed_ms:.2f}ms"}


# ---------------------------------------------------------------------------
# PLUGIN INITIALIZER (NO ORCHESTRATOR)
# ---------------------------------------------------------------------------


def init_cache_headers():

    def before():
        # optional future cache context
        pass

    def after(elapsed_ms):
        headers = {}

        headers.update(
            build_cache_control_header(
                no_store=CacheHeaderPolicy.NO_STORE,
                no_cache=CacheHeaderPolicy.NO_CACHE,
                must_revalidate=CacheHeaderPolicy.MUST_REVALIDATE,
                public=CacheHeaderPolicy.PUBLIC,
                private=CacheHeaderPolicy.PRIVATE,
                max_age=CacheHeaderPolicy.MAX_AGE,
                s_maxage=CacheHeaderPolicy.S_MAXAGE,
                immutable=CacheHeaderPolicy.IMMUTABLE,
                stale_while_revalidate=CacheHeaderPolicy.STALE_WHILE_REVALIDATE,
                stale_if_error=CacheHeaderPolicy.STALE_IF_ERROR,
            )
        )

        headers.update(build_observability_headers(elapsed_ms))

        if CacheHeaderPolicy.PRAGMA_NO_CACHE:
            headers.update(build_pragma_header(True))

        if CacheHeaderPolicy.VARY:
            headers.update(build_vary_header(CacheHeaderPolicy.VARY))

        if CacheHeaderPolicy.AGE_SECONDS is not None:
            headers.update(build_age_header(CacheHeaderPolicy.AGE_SECONDS))

        if (
            CacheHeaderPolicy.CLEAR_CACHE
            or CacheHeaderPolicy.CLEAR_COOKIES
            or CacheHeaderPolicy.CLEAR_STORAGE
        ):
            headers.update(
                build_clear_site_data_header(
                    cache=CacheHeaderPolicy.CLEAR_CACHE,
                    cookies=CacheHeaderPolicy.CLEAR_COOKIES,
                    storage=CacheHeaderPolicy.CLEAR_STORAGE,
                )
            )

        headers["__module__"] = "cache"

        return headers
    
    print(f"[DEBUG][cache] using registry id={id(registry)} from module={registry.__class__.__module__}")

    registry.register(before=before, after=after)
