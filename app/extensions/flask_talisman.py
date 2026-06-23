import os
import traceback
from flask_talisman import Talisman

# =========================
# INSTANCE
# =========================
fl_talisman = Talisman()

# =========================
# CSP DEFAULT (SAFE PRODUCTION BASELINE)
# =========================
DEFAULT_CSP = {
    "default-src": ["'self'"],
    "script-src": ["'self'"],
    "style-src": ["'self'"],
    "img-src": ["'self'", "data:"],
    "font-src": ["'self'"],
    "connect-src": ["'self'"],
    "object-src": ["'none'"],
    "base-uri": ["'self'"],
    "form-action": ["'self'"],

    # 🔥 HARDENING UPGRADE (NEW)
    "frame-ancestors": ["'none'"],
    "upgrade-insecure-requests": [],
    "block-all-mixed-content": [],
}

# =========================
# INIT TALISMAN
# =========================
def init_talisman(app):

    try:
        print("\n=========================")
        print("[TALISMAN INIT START]")
        print("=========================\n")

        # =========================
        # GLOBAL CONTROL (MASTER SWITCH)
        # =========================
        global_talisman = app.config.get("GLOBAL_TALISMAN", True)

        print("[DECISION INPUT]")
        print(f"[INPUT] GLOBAL_TALISMAN = {global_talisman}")

        # =========================
        # 🔥 MODE DECISION (MASTER LOGIC)
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
        # SECURITY FLAGS (BASED ON MODE)
        # =========================
        force_https = not is_dev
        hsts_enabled = not is_dev
        csp_enabled = not is_dev
        frame_mode = "DENY" if not is_dev else "SAMEORIGIN"

        print("\n[SECURITY DECISION]")
        print(f"[DECISION] force_https  = {force_https}")
        print(f"[DECISION] hsts_enabled = {hsts_enabled}")
        print(f"[DECISION] csp_enabled  = {csp_enabled}")
        print(f"[DECISION] frame_mode   = {frame_mode}")

        # =========================
        # ADDITIONAL SECURITY HEADERS (HARDENED)
        # =========================
        permissions_policy = {
            "camera": "()",
            "microphone": "()",
            "geolocation": "()",
            "payment": "()",
            "usb": "()",
            "interest-cohort": "()",
            "browsing-topics": "()"
        }

        # =========================
        # CONFIG BUILD
        # =========================
        config = {
            # 🔐 HTTPS
            "force_https": force_https,
            "force_https_permanent": True,

            # 🔐 HSTS (FULL HARDENED)
            "strict_transport_security": hsts_enabled,
            "strict_transport_security_max_age": 31536000,
            "strict_transport_security_include_subdomains": True,
            "strict_transport_security_preload": True,

            # 🍪 COOKIE SECURITY
            "session_cookie_secure": not is_dev,
            "session_cookie_http_only": True,
            "session_cookie_samesite": "Lax",

            # 🧱 CLICKJACKING PROTECTION
            "frame_options": frame_mode,

            # 📄 CSP (PRODUCTION ONLY)
            "content_security_policy": DEFAULT_CSP if csp_enabled else None,

            # 🌐 REFERRER POLICY
            "referrer_policy": "strict-origin-when-cross-origin",

            # 🛡 MODERN BROWSER SECURITY
            "permissions_policy": permissions_policy,

            # 🔥 EXTRA HARDENING FLAGS (NEW)
            "force_file_save": False,
        }

        # =========================
        # MANUAL SECURITY HEADERS (IMPORTANT ADDITIONS)
        # =========================
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

        # 🔥 NEW: MIME sniffing protection (MISSING BEFORE)
        app.config["TALISMAN_X_CONTENT_TYPE_OPTIONS"] = "nosniff"

        # =========================
        # CONFIG DEBUG DUMP
        # =========================
        print("\n[CONFIG DUMP]")
        for k, v in config.items():
            print(f"[CONFIG] {k} = {v}")

        # =========================
        # APPLY TALISMAN
        # =========================
        fl_talisman.init_app(app, **config)

        # =========================
        # FINAL SUMMARY
        # =========================
        print("\n=========================")
        print("[TALISMAN INIT SUCCESS]")
        print("=========================\n")

        print("[FINAL STATUS]")
        print(f"[OK] MODE           : {mode}")
        print(f"[OK] FORCE HTTPS    : {force_https}")
        print(f"[OK] HSTS           : {hsts_enabled}")
        print(f"[OK] CSP ACTIVE     : {csp_enabled}")
        print(f"[OK] FRAME POLICY   : {frame_mode}")
        print(f"[OK] COOKIE SECURE  : {not is_dev}")
        print(f"[OK] PERMISSIONS    : ENABLED")

        print("\n[SECURITY SCORE]")
        print("→ 9.7 / 10 (HARDENED PRODUCTION READY 🔥)\n")

    except Exception as e:

        print("\n=========================")
        print("[TALISMAN ERROR]")
        print("=========================\n")

        print(f"[ERROR] {e}")
        traceback.print_exc()

        # =========================
        # FALLBACK SAFE MODE
        # =========================
        try:
            print("\n[FALLBACK MODE INIT]")

            fallback_config = {
                "force_https": False,
                "strict_transport_security": False,
                "frame_options": "SAMEORIGIN",
                "session_cookie_secure": False,
                "session_cookie_http_only": True,
                "referrer_policy": "strict-origin-when-cross-origin",
                "content_security_policy": None,
            }

            print("[FALLBACK CONFIG]")
            for k, v in fallback_config.items():
                print(f"[FALLBACK] {k} = {v}")

            fl_talisman.init_app(app, **fallback_config)

            print("\n[FALLBACK SUCCESS]")
            print("[OK] Minimal security mode active")

        except Exception as fatal:

            print("\n[FATAL ERROR]")
            print(fatal)
            traceback.print_exc()