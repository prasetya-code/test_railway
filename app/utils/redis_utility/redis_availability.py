import traceback

from .redis_client import (
    get_cache_redis,
    get_limit_redis,
)


# =========================
# AVAILABILITY CHECK
# =========================
def is_cache_redis_available():
    try:
        return get_cache_redis() is not None

    except Exception as e:
        print(f"[REDIS CACHE CHECK ERROR] {e}")

        traceback.print_exc()

        return False


def is_limit_redis_available():
    try:
        return get_limit_redis() is not None

    except Exception as e:
        print(f"[REDIS LIMIT CHECK ERROR] {e}")

        traceback.print_exc()

        return False
