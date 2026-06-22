""" Tidak perlu ada middleware karena sudah di handle dengan @fl_cache.cached(
    timeout=60, response_filter=lambda r: getattr(r, "status_code", 200) == 200
) yang ada pada route """

from flask_caching import Cache
from .redis_client import is_cache_redis_available, REDIS_CACHE_URL

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
    """CACHE_TYPE options (yang paling sering digunakan):

    1. "SimpleCache"
       - In-memory cache (fallback default)
       - Cocok untuk development / aplikasi kecil

    2. "RedisCache"
       - Menggunakan Redis sebagai backend
       - Cocok untuk production (scalable & shared cache)

    3. "FileSystemCache"
       - Cache disimpan di filesystem (disk)
       - Perlu set CACHE_DIR
       - Alternatif jika tidak ada Redis

    4. "NullCache"
       - Tidak melakukan caching sama sekali
       - Berguna untuk debugging

    Catatan:
    - Gunakan RedisCache untuk production jika memungkinkan
    - SimpleCache tidak cocok untuk multi-worker (misal gunicorn)

    ⚠️ IMPORTANT:
    - Class ini hanya berisi konfigurasi statis
    - Logic pemilihan CACHE_TYPE dilakukan di init_cache()
    """

    # =========================
    # GENERAL CACHE SETTINGS
    # =========================
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    CACHE_THRESHOLD = int(os.getenv("CACHE_THRESHOLD", 500))
    CACHE_IGNORE_ERRORS = True
    CACHE_KEY_PREFIX = os.getenv("CACHE_KEY_PREFIX", "myapp_")

    # =========================
    # REDIS CONFIG
    # =========================
    CACHE_REDIS_URL = REDIS_CACHE_URL

    # =========================
    # FILESYSTEM CONFIG
    # =========================
    CACHE_DIR = str(CACHE_PATH)

    # Disable warning untuk null cache
    CACHE_NO_NULL_WARNING = True


# =========================
# CACHE INITIALIZER HELPER
# =========================
def _init_cache_backend(app, cache_type):
    """
    Membuat instance Cache baru untuk setiap percobaan init.
    Lebih aman dibanding memanggil init_app() berkali-kali
    pada instance Cache yang sama.
    """
    global fl_cache

    app.config["CACHE_TYPE"] = cache_type

    if cache_type == "FileSystemCache":
        ensure_cache_dir()

    cache_instance = Cache()
    cache_instance.init_app(app)

    fl_cache = cache_instance

    return cache_instance


# =========================
# INIT CACHE
# =========================
def init_cache(app):
    try:
        # =========================
        # LOAD STATIC CONFIG
        # =========================
        app.config.from_object(CacheConfig)

        # =========================
        # ENV CONTROL (OPTIONAL)
        # =========================
        USE_REDIS_CACHE = (
            os.getenv("USE_REDIS_CACHE", "true").lower() == "true"
        )

        # =========================
        # GLOBAL CONTROL (MASTER SWITCH)
        # =========================
        global_redis = app.config.get("GLOBAL_REDIS", True)

        print(f"[CACHE] ENV USE_REDIS_CACHE status: {USE_REDIS_CACHE}")

        # =========================
        # DECISION FLOW
        # =========================
        if not global_redis:
            print("[CACHE] Disabled Redis")
            cache_type = "SimpleCache"

        elif not USE_REDIS_CACHE:
            print("[CACHE] Disabled via ENV → using SimpleCache")
            cache_type = "SimpleCache"

        else:
            print("[CACHE] Checking Redis availability...")

            if is_cache_redis_available():
                print("[CACHE] Redis available → using RedisCache")
                cache_type = "RedisCache"
                
            else:
                print(
                    "[CACHE WARNING] Redis not available → fallback to SimpleCache"
                )
                cache_type = "SimpleCache"

        # =========================
        # APPLY CACHE TYPE
        # =========================
        _init_cache_backend(app, cache_type)

        # =========================
        # FILESYSTEM HANDLING
        # =========================
        if cache_type == "FileSystemCache":
            print("[CACHE] Using FileSystemCache")

        print(f"[CACHE] Initialized with type: {cache_type}")

        if cache_type == "FileSystemCache":
            print(f"[CACHE] Cache directory: {CACHE_PATH}")

        print()

    except Exception as e:
        print(f"[CACHE ERROR] Failed to initialize cache: {e}")
        traceback.print_exc()

        # =========================
        # FALLBACK
        # =========================
        try:
            print("[CACHE] Falling back to SimpleCache")

            _init_cache_backend(app, "SimpleCache")

            print("[CACHE] SimpleCache initialized successfully\n")

        except Exception as simple_error:
            print(
                f"[CACHE ERROR] SimpleCache fallback failed: {simple_error}"
            )
            traceback.print_exc()

            try:
                print("[CACHE] Falling back to FileSystemCache")

                _init_cache_backend(app, "FileSystemCache")

                print(
                    f"[CACHE] FileSystemCache initialized successfully "
                    f"at {CACHE_PATH}\n"
                )

            except Exception as filesystem_error:
                print(
                    "[CACHE CRITICAL] FileSystemCache fallback failed: "
                    f"{filesystem_error}"
                )
                traceback.print_exc()
                raise