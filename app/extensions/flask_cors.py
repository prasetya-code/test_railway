from flask_cors import CORS

import os
import traceback


# =========================
# CORS INSTANCE
# =========================
fl_cors = CORS()


# =========================
# CONFIGURATION PATH
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# =========================
# CONFIG CLASS
# =========================
class CORSConfig:
    """
    Static configuration for Flask-CORS.

    This is equivalent to CacheConfig style.
    """

    # =========================
    # ORIGINS
    # =========================
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # =========================
    # METHODS
    # =========================
    CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    # =========================
    # HEADERS
    # =========================
    CORS_ALLOW_HEADERS = [
        "Content-Type",
        "Authorization",
        "X-API-Key",
        "X-Request-ID",
    ]

    # =========================
    # EXPOSE HEADERS
    # =========================
    CORS_EXPOSE_HEADERS = [
        "Content-Type",
        "Content-Length",
        "ETag",
        "X-Request-ID",
    ]

    # =========================
    # CREDENTIALS
    # =========================
    CORS_SUPPORTS_CREDENTIALS = True

    # =========================
    # PREFLIGHT CACHE
    # =========================
    CORS_MAX_AGE = 600

    # =========================
    # RESOURCES
    # =========================
    CORS_RESOURCES = {r"/api/*": {"origins": CORS_ORIGINS}}


# =========================
# INIT CORS
# =========================
def init_cors(app):
    """
    Initialize Flask-CORS with config + safety checks
    """

    try:
        # =========================
        # LOAD CONFIG
        # =========================
        app.config.from_object(CORSConfig)

        print(f"[CORS] Origins: {CORSConfig.CORS_ORIGINS}")
        print(f"[CORS] Methods: {CORSConfig.CORS_METHODS}")
        print("[CORS] Initializing flask-cors...")

        # =========================
        # ENV CONTROL (OPTIONAL)
        # =========================
        ENABLE_CORS = os.getenv("ENABLE_CORS", "true").lower() == "true"

        if not ENABLE_CORS:
            print("[CORS] Disabled via ENV")
            return

        # =========================
        # INIT FLASK-CORS
        # =========================
        fl_cors.init_app(
            app,
            resources=CORSConfig.CORS_RESOURCES,
            supports_credentials=CORSConfig.CORS_SUPPORTS_CREDENTIALS,
            allow_headers=CORSConfig.CORS_ALLOW_HEADERS,
            expose_headers=CORSConfig.CORS_EXPOSE_HEADERS,
            max_age=CORSConfig.CORS_MAX_AGE,
        )

        print("[CORS] Initialized successfully \n")

    except Exception as e:
        print(f"[CORS ERROR] Failed to initialize CORS: {e}")
        traceback.print_exc()

        # =========================
        # FALLBACK SAFE MODE
        # =========================
        try:
            print("[CORS] Fallback: enabling permissive CORS")

            CORS(
                app,
                resources={r"/*": {"origins": "*"}},
                supports_credentials=False,
            )

        except Exception as fallback_error:
            print(f"[CORS CRITICAL] Fallback failed: {fallback_error}")
            traceback.print_exc()
