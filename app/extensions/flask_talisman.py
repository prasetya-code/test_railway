import os
import traceback
from flask_talisman import Talisman

# =========================
# INSTANCE
# =========================
fl_talisman = Talisman()

# =========================
# CSP PERFECT HARDENED (OWASP + MODERN BROWSER)
# =========================
DEFAULT_CSP = {
    "default-src": ["'self'"],

    "base-uri": ["'self'"],

    "object-src": ["'none'"],

    "frame-ancestors": ["'none'"],

    "script-src": ["'self'", 
                   # iconify script
                   "https://code.iconify.design"],

    "style-src": ["'self'"],

    "img-src": ["'self'", 
                "data:"],

    "font-src": ["'self'"],

    "connect-src": ["'self'", 
                    # iconify pre-connect
                    "https://api.iconify.design"],


    # 🔥 HARDENING LAYER
    "upgrade-insecure-requests": [],
    "block-all-mixed-content": [],
}

# =========================
# INIT TALISMAN (PERFECT VERSION)
# =========================
def init_talisman(app):

    try:
        print("\n=========================")
        print("[TALISMAN INIT START]")
        print("=========================\n")

        # =========================
        # GLOBAL CONTROL
        # =========================
        global_talisman = app.config.get("GLOBAL_TALISMAN", True)

        print("[DECISION INPUT]")
        print(f"[INPUT] GLOBAL_TALISMAN = {global_talisman}")

        # =========================
        # MODE DECISION
        # =========================
        if global_talisman:
            mode = "production"
            is_dev = False
        else:
            mode = "development"
            is_dev = True

        print("\n[MODE DECISION]")
        print(f"[MODE] ACTIVE_MODE = {mode}")
        print(f"[MODE] is_dev      = {is_dev}")

        # =========================
        # SECURITY FLAGS (PERFECT LOGIC)
        # =========================
        force_https = not is_dev
        hsts_enabled = not is_dev
        csp_enabled = not is_dev

        frame_mode = "DENY" if not is_dev else "SAMEORIGIN"

        # 🔥 PERFECT ADDITION: XSS + MIME + COOKIE HARDENING
        x_content_type_options = "nosniff"
        referrer_policy = "strict-origin-when-cross-origin"

        permissions_policy = {
            "camera": "()",
            "microphone": "()",
            "geolocation": "()",
            "payment": "()",
            "usb": "()",
            
            # deprecated
            # "interest-cohort": "()",
            # "browsing-topics": "()"
        }

        print("\n[SECURITY DECISION]")
        print(f"[DECISION] force_https  = {force_https}")
        print(f"[DECISION] hsts_enabled = {hsts_enabled}")
        print(f"[DECISION] csp_enabled  = {csp_enabled}")
        print(f"[DECISION] frame_mode   = {frame_mode}")

        # =========================
        # CONFIG BUILD (PERFECT HARDENING)
        # =========================
        config = {
            # HTTPS
            "force_https": force_https,
            "force_https_permanent": True,

            # HSTS (FULL)
            "strict_transport_security": hsts_enabled,
            "strict_transport_security_max_age": 63072000,
            "strict_transport_security_include_subdomains": True,
            "strict_transport_security_preload": True,

            # COOKIES
            "session_cookie_secure": not is_dev,
            "session_cookie_http_only": True,
            "session_cookie_samesite": "Lax",

            # CLICKJACKING
            "frame_options": frame_mode,

            # CSP
            "content_security_policy": DEFAULT_CSP if csp_enabled else None,

            # NONCE UNTUK INLINE SCRIPT hanya jika CSP aktif
            "content_security_policy_nonce_in": (
                ["script-src", "style-src"] if csp_enabled else None
            ),

            # HEADERS
            "referrer_policy": referrer_policy,
            "permissions_policy": permissions_policy,

            # EXTRA HARDENING
            "force_file_save": False,
        }

        # =========================
        # MANUAL HEADERS
        # =========================
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
        app.config["TALISMAN_X_CONTENT_TYPE_OPTIONS"] = x_content_type_options

        # =========================
        # CONFIG DEBUG
        # =========================
        print("\n[CONFIG DUMP]")
        for k, v in config.items():
            print(f"[CONFIG] {k} = {v}")

        # =========================
        # APPLY TALISMAN
        # =========================
        fl_talisman.init_app(app, **config)

        # =========================
        # MODERN SECURITY HEADERS
        # =========================
        @app.after_request
        def apply_modern_security_headers(response):

            # =========================
            # MIME SNIFFING PROTECTION
            # =========================
            response.headers["X-Content-Type-Options"] = "nosniff"

            # =========================
            # PROCESS ISOLATION
            # =========================
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

            # =========================
            # RESOURCE ISOLATION
            # =========================
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

            # =========================
            # BROWSER MEMORY ISOLATION
            # =========================
            response.headers["Origin-Agent-Cluster"] = "?1"

            # =========================
            # PRODUCTION ONLY
            # =========================
            if not is_dev:
                response.headers[
                    "Cross-Origin-Embedder-Policy"
                ] = "require-corp"

            return response

        # =========================
        # FINAL STATUS
        # =========================
        print("\n=========================")
        print("[TALISMAN INIT SUCCESS]")
        print("=========================\n")

        print(f"[OK] MODE           : {mode}")
        print(f"[OK] FORCE HTTPS    : {force_https}")
        print(f"[OK] HSTS (2Y)      : {hsts_enabled}")
        print(f"[OK] CSP            : {csp_enabled}")
        print(f"[OK] FRAME POLICY   : {frame_mode}")
        print(f"[OK] COOKIE SECURE  : {not is_dev}")
        print(f"[OK] X-CTO NOSNIFF  : ENABLED")
        print(f"[OK] PERMISSIONS    : ENABLED")
        print(f"[OK] COOP           : ENABLED")
        print(f"[OK] CORP           : ENABLED")
        print(f"[OK] OAC            : ENABLED")

        if not is_dev:
            print(f"[OK] COEP           : ENABLED")


        if is_dev:
            print("\n[SECURITY SCORE]")
            print("→ DEVELOPMENT PROFILE 🧪")

        else:
            print("\n[SECURITY SCORE]")
            print("→ ENTERPRISE-GRADE HARDENED 🔥🔥🔥")

    except Exception as e:

        print("\n=========================")
        print("[TALISMAN ERROR]")
        print("=========================\n")

        print(f"[ERROR] {e}")
        traceback.print_exc()

        try:
            print("\n[FALLBACK SAFE MODE]")

            fl_talisman.init_app(
                app,
                force_https=False,
                strict_transport_security=False,
                frame_options="SAMEORIGIN",
                session_cookie_secure=False,
                session_cookie_http_only=True,
                referrer_policy="strict-origin-when-cross-origin",
            )

            print("[FALLBACK SUCCESS] Minimal secure mode active")

        except Exception as fatal:
            print("[FATAL ERROR]")
            print(fatal)
            
            traceback.print_exc()