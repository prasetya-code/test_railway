# minimal policy web headers yang layak dipasang di production

| Level       | Persentase | Keterangan                                              |
| ----------- | ---------- | ------------------------------------------------------- |
| Basic       | 60-70%     | Sudah aman untuk aplikasi internal                      |
| Recommended | 80-90%     | Cocok untuk mayoritas website dan API production        |
| Hardened    | 95-100%    | Cocok untuk fintech, healthcare, government, enterprise |


# headers

```py
# api.py

# ---------------------------------------------------------------------------
# ORCHESTRATOR
# Controls request lifecycle hooks (before/after request)
# ---------------------------------------------------------------------------

class HeaderOrchestrator:

    def __init__(self, app):
        self.app = app
        self.start_time = None

    def before_request(self):
        """
        Called before each request is processed.

        Responsibilities:
        - Start performance timer
        - Attach request-scoped header context
        """

        self.start_time = time.perf_counter()

        request.headers_context = {
            **build_authorization_header(),
            **build_api_key_header(),
            **build_request_id_header(),
            **build_content_headers(),
            **build_version_headers(),
        }

    def after_request(self, response):
        """
        Called after response is generated.

        Responsibilities:
        - Calculate response time
        - Inject rate limit headers
        - Inject observability headers
        """

        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        headers = {
            **build_rate_limit_headers(),
            **build_observability_headers(elapsed_ms),
        }

        for key, value in headers.items():
            response.headers[key] = value

        return response


# ---------------------------------------------------------------------------
# REGISTRATION ENTRY POINT
# Used in application bootstrap (register_utils)
# ---------------------------------------------------------------------------

def register_headers(app):
    """
    Initialize header middleware system.

    Usage:
        register_headers(app)
    """

    orchestrator = HeaderOrchestrator(app)

    app.before_request(orchestrator.before_request)
    app.after_request(orchestrator.after_request)

    return orchestrator

# browser.py

# ---------------------------------------------------------------------------
# ORCHESTRATOR
# Controls request lifecycle hooks (before/after request)
# ---------------------------------------------------------------------------

class BrowserHeaderOrchestrator:

    def __init__(self, app):
        self.app = app
        self.start_time = None

    def before_request(self):
        """
        Called before each request is processed.

        Responsibilities:
        - Start performance timer
        - Prepare request lifecycle context
        """

        self.start_time = time.perf_counter()

        request.headers_context = {
            **build_content_type_options_header(),
            **build_frame_options_header(),
            **build_xss_protection_header(),
            **build_dns_prefetch_control_header(),
            **build_cross_domain_policy_header(),
        }

    def after_request(self, response):
        """
        Called after response is generated.

        Responsibilities:
        - Calculate response time
        - Inject security headers
        - Inject observability headers
        """

        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

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

        for key, value in headers.items():
            response.headers[key] = value

        return response


# ---------------------------------------------------------------------------
# REGISTRATION ENTRY POINT
# Used in application bootstrap (register_utils)
# ---------------------------------------------------------------------------

def register_browser_headers(app):
    """
    Initialize browser security header middleware system.

    Usage:
        register_browser_headers(app)
    """

    orchestrator = BrowserHeaderOrchestrator(app)

    app.before_request(orchestrator.before_request)
    app.after_request(orchestrator.after_request)

    return orchestrator

# cache.py:
# ---------------------------------------------------------------------------
# ORCHESTRATOR
# Controls request lifecycle (before/after request hooks)
# ---------------------------------------------------------------------------

class CacheHeaderOrchestrator:

    def __init__(self, app):
        self.app = app
        self.start_time = None

    def before_request(self):
        """
        Called before request processing.

        Responsibilities:
        - Start timing
        - Attach cache context (optional future use)
        """

        self.start_time = time.perf_counter()

        request.cache_context = {
            **build_cache_control_header(
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
        }

    def after_request(self, response):
        """
        Called after response generation.

        Responsibilities:
        - Inject cache headers
        - Add ETag / Last-Modified / Vary / Age headers
        - Add observability header
        """

        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

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

        headers.update(
            build_observability_headers(elapsed_ms)
        )

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

        for key, value in headers.items():
            response.headers[key] = value

        return response


# ---------------------------------------------------------------------------
# REGISTRATION ENTRY POINT
# Used in application bootstrap (register_utils)
# ---------------------------------------------------------------------------

def register_cache_headers(app):
    """
    Initialize cache control middleware system.

    Usage:
        register_cache_headers(app)
    """

    orchestrator = CacheHeaderOrchestrator(app)

    app.before_request(orchestrator.before_request)
    app.after_request(orchestrator.after_request)

    return orchestrator

# cors.py

# ---------------------------------------------------------------------------
# ORCHESTRATOR
# Controls request lifecycle (before/after request hooks)
# ---------------------------------------------------------------------------

class CORSHeaderOrchestrator:

    def __init__(self, app):
        self.app = app
        self.start_time = None

    def before_request(self):
        """
        Called before request processing.

        Responsibilities:
        - Start timing
        - Detect request origin
        """

        self.start_time = time.perf_counter()

        request.cors_origin = request.headers.get("Origin")

    def after_request(self, response):
        """
        Called after response generation.

        Responsibilities:
        - Inject CORS headers
        - Handle preflight vs normal response
        - Add observability headers
        """

        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        origin = getattr(request, "cors_origin", None)

        headers = {}

        # Preflight handling (OPTIONS request)
        if request.method == "OPTIONS":
            headers.update(
                build_allow_origin_header(
                    CORSHeaderPolicy.ALLOWED_ORIGINS,
                    origin,
                    CORSHeaderPolicy.ALLOW_ALL_ORIGINS,
                )
            )

            headers.update(
                build_allow_methods_header(
                    CORSHeaderPolicy.ALLOWED_METHODS
                )
            )

            headers.update(
                build_allow_headers_header(
                    CORSHeaderPolicy.ALLOWED_REQUEST_HEADERS
                )
            )

            headers.update(
                build_allow_credentials_header(
                    CORSHeaderPolicy.ALLOW_CREDENTIALS
                )
            )

            headers.update(
                build_max_age_header(
                    CORSHeaderPolicy.PREFLIGHT_MAX_AGE
                )
            )

        # Normal response CORS headers
        else:
            headers.update(
                build_allow_origin_header(
                    CORSHeaderPolicy.ALLOWED_ORIGINS,
                    origin,
                    CORSHeaderPolicy.ALLOW_ALL_ORIGINS,
                )
            )

            headers.update(
                build_allow_methods_header(
                    CORSHeaderPolicy.ALLOWED_METHODS
                )
            )

            headers.update(
                build_allow_headers_header(
                    CORSHeaderPolicy.ALLOWED_REQUEST_HEADERS
                )
            )

            headers.update(
                build_expose_headers_header(
                    CORSHeaderPolicy.EXPOSED_HEADERS
                )
            )

            headers.update(
                build_allow_credentials_header(
                    CORSHeaderPolicy.ALLOW_CREDENTIALS
                )
            )

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

def register_cors_headers(app):
    """
    Initialize CORS middleware system.

    Usage:
        register_cors_headers(app)
    """

    orchestrator = CORSHeaderOrchestrator(app)

    app.before_request(orchestrator.before_request)
    app.after_request(orchestrator.after_request)

    return orchestrator

# csp.py

# ---------------------------------------------------------------------------
# ORCHESTRATOR
# Controls request lifecycle hooks (before/after request)
# ---------------------------------------------------------------------------

class CSPHeaderOrchestrator:

    def __init__(self, app):
        self.app = app
        self.start_time = None

    def before_request(self):
        """
        Called before request processing.
        """

        self.start_time = time.perf_counter()

        request.csp_context = build_fetch_directives()

    def after_request(self, response):
        """
        Called after response generation.
        """

        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

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

        headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"

        for key, value in headers.items():
            response.headers[key] = value

        return response


# ---------------------------------------------------------------------------
# REGISTRATION ENTRY POINT
# Used in application bootstrap (register_utils)
# ---------------------------------------------------------------------------

def register_csp_headers(app):
    """
    Initialize CSP middleware system.

    Usage:
        register_csp_headers(app)
    """

    orchestrator = CSPHeaderOrchestrator(app)

    app.before_request(orchestrator.before_request)
    app.after_request(orchestrator.after_request)

    return orchestrator

# hardening.py

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

# isolation.py

# ---------------------------------------------------------------------------
# ORCHESTRATOR
# Controls request lifecycle (before/after request)
# ---------------------------------------------------------------------------

class IsolationHeaderOrchestrator:

    def __init__(self, app):
        self.app = app
        self.start_time = None

    def before_request(self):
        """
        Called before request processing.
        """

        self.start_time = time.perf_counter()

        request.isolation_context = {}

    def after_request(self, response):
        """
        Called after response generation.
        """

        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        headers = {}

        preset = IsolationHeaderPolicy.PRESET

        # -------------------------
        # PRESET MODE
        # -------------------------
        if preset == "full":
            config = preset_full_isolation()

        elif preset == "credentialless":
            config = preset_credentialless_isolation()

        elif preset == "none":
            config = preset_no_isolation()

        # -------------------------
        # MANUAL MODE
        # -------------------------
        else:
            config = {
                "coop": IsolationHeaderPolicy.COOP_POLICY,
                "coep": IsolationHeaderPolicy.COEP_POLICY,
                "corp": IsolationHeaderPolicy.CORP_POLICY,
                "oac": IsolationHeaderPolicy.ORIGIN_AGENT_CLUSTER,
            }

        # COOP
        headers.update(
            build_coop_header(
                config["coop"],
                IsolationHeaderPolicy.REPORT_TO,
            )
        )

        # COEP
        headers.update(
            build_coep_header(
                config["coep"],
                IsolationHeaderPolicy.REPORT_TO,
            )
        )

        # CORP
        headers.update(
            build_corp_header(
                config["corp"]
            )
        )

        # Origin Agent Cluster
        headers.update(
            build_origin_agent_cluster_header(
                config["oac"]
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

def register_isolation_headers(app):
    """
    Initialize cross-origin isolation middleware system.

    Usage:
        register_isolation_headers(app)
    """

    orchestrator = IsolationHeaderOrchestrator(app)

    app.before_request(orchestrator.before_request)
    app.after_request(orchestrator.after_request)

    return orchestrator
```

headers end