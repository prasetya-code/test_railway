from flask_talisman import Talisman
import os
import traceback


# =========================
# TALISMAN INSTANCE
# =========================
fl_talisman = Talisman()


# =========================
# CONFIG DIRECTORY (OPTIONAL FUTURE USE)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# =========================
# CONFIG (STATIC ONLY)
# =========================
class TalismanConfig:
    """
    Flask-Talisman Security Configuration

    Fungsi utama:
    - Security headers (HSTS, XFO, dll)
    - CSP (Content Security Policy)
    - HTTPS enforcement (optional)
    - Secure cookies behavior

    ⚠️ NOTE:
    - Ini hanya konfigurasi statis
    - Logic enable/disable ada di init_talisman()
    """

    # =========================
    # HTTPS SETTINGS
    # =========================
    FORCE_HTTPS = os.getenv("FORCE_HTTPS", "false").lower() == "true"
    STRICT_TRANSPORT_SECURITY = True
    STRICT_TRANSPORT_SECURITY_PRELOAD = True
    STRICT_TRANSPORT_SECURITY_MAX_AGE = 31536000  # 1 year

    # =========================
    # FRAME & MIME SECURITY
    # =========================
    FRAME_OPTIONS = "DENY"
    CONTENT_TYPE_NOSNIFF = True
    REFERRER_POLICY = "strict-origin-when-cross-origin"

    # =========================
    # XSS PROTECTION (legacy header behavior)
    # =========================
    X_XSS_PROTECTION = 1

    # =========================
    # BASIC CSP (SAFE DEFAULT)
    # =========================
    CONTENT_SECURITY_POLICY = {
        "default-src": "'self'",
        "script-src": ["'self'"],
        "style-src": ["'self'"],
        "img-src": ["'self'", "data:"],
        "font-src": ["'self'"],
        "connect-src": ["'self'"],
        "frame-ancestors": ["'none'"],
        "base-uri": ["'self'"],
    }

    # =========================
    # COOKIE SECURITY
    # =========================
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # =========================
    # TALISMAN FLAGS
    # =========================
    FORCE_CONTENT_SECURITY_POLICY = True


# =========================
# CSP CUSTOM OVERRIDE (OPTIONAL)
# =========================
def get_custom_csp(app):
    """
    Optional dynamic CSP override via ENV or app config
    """

    try:
        csp_mode = os.getenv("CSP_MODE", "strict").lower()

        # STRICT MODE (default)
        if csp_mode == "strict":
            return TalismanConfig.CONTENT_SECURITY_POLICY

        # DEVELOPMENT MODE (more relaxed)
        elif csp_mode == "dev":
            return {
                "default-src": "'self'",
                "script-src": ["'self'", "'unsafe-inline'"],
                "style-src": ["'self'", "'unsafe-inline'"],
                "img-src": ["'self'", "data:", "*"],
                "connect-src": ["'self'", "*"],
            }

        # CUSTOM FROM APP CONFIG
        elif csp_mode == "app":
            return app.config.get("CUSTOM_CSP", TalismanConfig.CONTENT_SECURITY_POLICY)

        else:
            return TalismanConfig.CONTENT_SECURITY_POLICY

    except Exception as e:
        print(f"[TALISMAN CSP ERROR] {e}")
        traceback.print_exc()

        return TalismanConfig.CONTENT_SECURITY_POLICY


# =========================
# INIT TALISMAN
# =========================
def init_talisman(app):
    try:
        # =========================
        # LOAD CONFIG
        # =========================
        app.config.from_object(TalismanConfig)

        print("[TALISMAN] Loading configuration...")

        # =========================
        # ENV CONTROL
        # =========================
        ENABLE_SECURITY = os.getenv("ENABLE_TALISMAN", "true").lower() == "true"

        if not ENABLE_SECURITY:
            print("[TALISMAN] Disabled via ENV")
            return

        # =========================
        # FORCE HTTPS CONTROL
        # =========================
        force_https = app.config.get("FORCE_HTTPS", False)

        # =========================
        # CSP SELECTION
        # =========================
        csp = get_custom_csp(app)

        print(f"[TALISMAN] FORCE_HTTPS = {force_https}")
        print("[TALISMAN] CSP MODE LOADED")

        # =========================
        # INIT TALISMAN
        # =========================
        fl_talisman.init_app(
            app,
            force_https=force_https,
            content_security_policy=csp,
            frame_options=app.config.get("FRAME_OPTIONS"),
            strict_transport_security=True,
            strict_transport_security_max_age=app.config.get(
                "STRICT_TRANSPORT_SECURITY_MAX_AGE"
            ),
            strict_transport_security_preload=app.config.get(
                "STRICT_TRANSPORT_SECURITY_PRELOAD"
            ),
            session_cookie_secure=app.config.get("SESSION_COOKIE_SECURE"),
            session_cookie_http_only=app.config.get("SESSION_COOKIE_HTTPONLY"),
            session_cookie_samesite=app.config.get("SESSION_COOKIE_SAMESITE"),
        )

        print("[TALISMAN] Initialized successfully\n")

    except Exception as e:
        print(f"[TALISMAN ERROR] Failed to initialize: {e}")
        traceback.print_exc()

        # =========================
        # FALLBACK SAFE MODE
        # =========================
        try:
            print("[TALISMAN] Falling back to minimal security mode...")

            fl_talisman.init_app(
                app,
                force_https=False,
                content_security_policy={"default-src": "'self'"},
            )

        except Exception as fallback_error:
            print(f"[TALISMAN CRITICAL] Fallback failed: {fallback_error}")
            traceback.print_exc()
