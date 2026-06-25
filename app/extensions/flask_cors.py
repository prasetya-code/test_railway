from flask_cors import CORS
import traceback

# =========================
# INSTANCE
# =========================
fl_cors = CORS()

# =========================
# DEFAULT PRODUCTION ORIGINS
# =========================
DEFAULT_ALLOWED_ORIGINS = [
    "https://app.company.com",
    "https://admin.company.com",
]


# =========================
# INIT CORS
# =========================
def init_cors(app):

    try:
        print("\n=========================")
        print("[CORS INIT START]")
        print("=========================\n")

        # =========================
        # GLOBAL CONTROL
        # =========================
        global_cors = app.config.get("GLOBAL_CORS", True)

        print("[DECISION INPUT]")
        print(f"[INPUT] GLOBAL_CORS = {global_cors}")

        # =========================
        # MODE DECISION
        # =========================
        if global_cors:
            mode = "production"
            is_dev = False
        else:
            mode = "development"
            is_dev = True

        print("\n[MODE DECISION]")
        print(f"[MODE] ACTIVE_MODE = {mode}")

        # =========================
        # DEV CONFIG
        # =========================
        if is_dev:
            cors_config = {
                "resources": {r"/*": {"origins": "*"}},
                "supports_credentials": False,
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Content-Type",
                    "Authorization",
                    "X-Requested-With",
                    "Accept",
                    "Origin",
                ],
                "expose_headers": ["Content-Type"],
                # =========================
                # CORS OPTIMIZATION
                # =========================
                "vary_header": True,
                "send_wildcard": True,
                "automatic_options": True,
                # =========================
                # PREFLIGHT CACHE
                # =========================
                "max_age": 600,
            }

        # =========================
        # PROD CONFIG
        # =========================
        else:
            allowed_origins = app.config.get(
                "CORS_ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS
            )

            cors_config = {
                "resources": {r"/*": {"origins": allowed_origins}},
                "supports_credentials": True,
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin"],
                "expose_headers": ["Content-Type", "Content-Length", "X-Request-ID"],
                # =========================
                # CORS HARDENING
                # =========================
                "vary_header": True,
                "send_wildcard": False,
                "automatic_options": True,
                # =========================
                # PREFLIGHT CACHE
                # =========================
                "max_age": 86400,
            }

        print("\n[CONFIG DUMP]")
        for k, v in cors_config.items():
            print(f"[CONFIG] {k} = {v}")

        # =========================
        # APPLY CORS
        # =========================
        fl_cors.init_app(app, **cors_config)

        print("\n=========================")
        print("[CORS INIT SUCCESS]")
        print("=========================\n")

        print(f"[OK] MODE            : {mode}")

        print(f"[OK] CREDENTIALS     : {cors_config['supports_credentials']}")

        print(f"[OK] MAX AGE         : {cors_config['max_age']}")

        print(f"[OK] VARY HEADER     : {cors_config['vary_header']}")

        print(f"[OK] WILDCARD MODE   : {cors_config['send_wildcard']}")

        print(f"[OK] AUTO OPTIONS    : {cors_config['automatic_options']}")

        print("\n[SECURITY LEVEL]")

        if is_dev:
            print("→ DEVELOPMENT PROFILE 🧪\n")
        else:
            print("→ PRODUCTION HARDENED 🔥\n")

    except Exception as e:
        print("\n=========================")
        print("[CORS ERROR]")
        print("=========================\n")

        print(e)
        traceback.print_exc()

        try:
            print("\n[FALLBACK MODE]")

            fallback_config = {
                "resources": {r"/*": {"origins": "*"}},
                "supports_credentials": False,
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "vary_header": True,
                "send_wildcard": True,
                "automatic_options": True,
                "max_age": 300,
            }

            print("[FALLBACK CONFIG]")
            for k, v in fallback_config.items():
                print(f"[FALLBACK] {k} = {v}")

            fl_cors.init_app(app, **fallback_config)

            print("\n[FALLBACK SUCCESS]")
            print("[OK] Minimal CORS mode active")

        except Exception as fatal:
            print("\n[FATAL ERROR]")
            print(fatal)
            traceback.print_exc()
