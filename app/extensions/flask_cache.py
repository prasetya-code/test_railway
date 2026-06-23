"""
Tidak perlu ada middleware karena sudah di handle dengan @fl_cache.cached(
    timeout=60, response_filter=lambda r: getattr(r, "status_code", 200) == 200
) yang ada pada route
"""

from flask_caching import Cache
from ..utils.redis_utility.redis_config import REDIS_CACHE_URL
from ..utils.redis_utility.redis_availability import is_cache_redis_available

from pathlib import Path
import os
import traceback

fl_cache = Cache()

# =========================
# CACHE DIRECTORY
# =========================
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent

CACHE_PATH = PROJECT_ROOT / "tmp" / "flask_cache"


def ensure_cache_dir():
    try:
        CACHE_PATH.mkdir(parents=True, exist_ok=True)
        print(f"[CACHE] Directory ready: {CACHE_PATH}")

    except Exception as e:
        print(f"[CACHE ERROR] Failed to create cache directory: {e}")
        traceback.print_exc()


# =========================
# CONFIG (STATIC ONLY)
# =========================
class CacheConfig:
    """
    CACHE_TYPE options:

    1. SimpleCache
    2. RedisCache
    3. FileSystemCache
    4. NullCache
    """

    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    CACHE_THRESHOLD = int(os.getenv("CACHE_THRESHOLD", 500))
    CACHE_IGNORE_ERRORS = True
    CACHE_KEY_PREFIX = os.getenv("CACHE_KEY_PREFIX", "myapp_")

    CACHE_REDIS_URL = REDIS_CACHE_URL
    CACHE_DIR = str(CACHE_PATH)
    CACHE_NO_NULL_WARNING = True


# =========================
# CACHE INITIALIZER HELPER
# =========================
def _init_cache_backend(app, cache_type):
    global fl_cache

    print("\n[CACHE BACKEND INIT]")
    print(f"[BACKEND] Selected type = {cache_type}")

    app.config["CACHE_TYPE"] = cache_type

    if cache_type == "FileSystemCache":
        ensure_cache_dir()

    cache_instance = Cache()
    cache_instance.init_app(app)

    fl_cache = cache_instance

    print("[BACKEND] Cache instance initialized")
    return cache_instance


# =========================
# INIT CACHE
# =========================
def init_cache(app):
    try:
        print("\n=========================")
        print("[CACHE INIT START]")
        print("=========================\n")

        # =========================
        # LOAD STATIC CONFIG
        # =========================
        app.config.from_object(CacheConfig)

        # =========================
        # ENV CONTROL
        # =========================
        USE_REDIS_CACHE_RAW = os.getenv("USE_REDIS_CACHE", "true")
        USE_REDIS_CACHE = USE_REDIS_CACHE_RAW.lower() == "true"

        # =========================
        # GLOBAL CONTROL
        # =========================
        global_redis = app.config.get("GLOBAL_REDIS", True)

        print("[INPUT CONFIG]")
        print(f"[INPUT] GLOBAL_REDIS (app.config) = {global_redis}")
        print(f"[INPUT] USE_REDIS_CACHE (raw)     = {USE_REDIS_CACHE_RAW}")
        print(f"[INPUT] USE_REDIS_CACHE (bool)    = {USE_REDIS_CACHE}")

        # =========================
        # DECISION FLOW
        # =========================
        cache_type = None
        decision_reason = None

        if not global_redis:
            cache_type = "SimpleCache"
            decision_reason = "GLOBAL_REDIS=False → force SimpleCache"
            print("\n[CACHE DECISION] Disabled Redis by GLOBAL_REDIS")

        elif not USE_REDIS_CACHE:
            cache_type = "SimpleCache"
            decision_reason = "USE_REDIS_CACHE=False → force SimpleCache"
            print("\n[CACHE DECISION] Disabled Redis by ENV")

        else:
            print("\n[CACHE DECISION] Redis allowed → checking availability...")

            if is_cache_redis_available():
                cache_type = "RedisCache"
                decision_reason = "Redis available → using RedisCache"
                print("[CACHE DECISION] Redis AVAILABLE → USING RedisCache")

            else:
                cache_type = "SimpleCache"
                decision_reason = "Redis not available → fallback SimpleCache"
                print("[CACHE WARNING] Redis NOT available → fallback SimpleCache")

        # =========================
        # DECISION RESULT TRACE
        # =========================
        print("\n[CACHE DECISION RESULT]")
        print(f"[RESULT] cache_type = {cache_type}")
        print(f"[RESULT] reason     = {decision_reason}")

        # =========================
        # APPLY CACHE TYPE
        # =========================
        _init_cache_backend(app, cache_type)

        # =========================
        # FILESYSTEM HANDLING
        # =========================
        if cache_type == "FileSystemCache":
            print("[CACHE] Using FileSystemCache backend")
            print(f"[CACHE] Directory = {CACHE_PATH}")

        print("\n[CACHE INIT SUCCESS]")
        print(f"[CACHE] Active backend: {cache_type}\n")

    except Exception as e:
        print(f"\n[CACHE ERROR] Failed to initialize cache: {e}")
        traceback.print_exc()

        # =========================
        # FALLBACK
        # =========================
        try:
            print("\n[CACHE FALLBACK] Switching to SimpleCache")

            _init_cache_backend(app, "SimpleCache")

            print("[CACHE FALLBACK SUCCESS] SimpleCache active\n")

        except Exception as simple_error:
            print(f"[CACHE ERROR] SimpleCache fallback failed: {simple_error}")
            traceback.print_exc()

            try:
                print("\n[CACHE EMERGENCY FALLBACK] FileSystemCache")

                _init_cache_backend(app, "FileSystemCache")

                print(f"[CACHE EMERGENCY OK] Using {CACHE_PATH}\n")

            except Exception as filesystem_error:
                print(f"[CACHE CRITICAL] All fallback failed: {filesystem_error}")
                traceback.print_exc()
                raise
