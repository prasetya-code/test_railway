import redis
import traceback
from urllib.parse import urlparse

from .redis_config import (
    REDIS_CACHE_URL,
    REDIS_LIMIT_URL,
    REDIS_COMMON_CONFIG,
)

from .redis_debug import (
    debug_redis_url,
    debug_check_port,
)

# =========================
# GLOBAL CLIENT
# =========================
_cache_client = None
_limit_client = None


# =========================
# HEALTH CHECK (SINGLE)
# =========================
def is_alive(client):
    try:
        client.ping()
        return True

    except Exception as e:
        print(f"[REDIS WARNING] Client not alive: {e}")
        traceback.print_exc()
        return False


# =========================
# CREATE CLIENT
# =========================
def create_client(url):
    try:
        print(f"[REDIS] Creating client for {url}")

        debug_redis_url(url)

        client = redis.Redis.from_url(url, **REDIS_COMMON_CONFIG)

        return client

    except Exception as e:
        print(f"[REDIS ERROR] Failed to create client: {e}")
        traceback.print_exc()
        return None


# =========================
# CACHE REDIS
# =========================
def get_cache_redis():
    global _cache_client

    try:
        if _cache_client and is_alive(_cache_client):
            print("[REDIS CACHE] Using existing alive connection")
            return _cache_client

        print("[REDIS CACHE] Connecting...")

        parsed = urlparse(REDIS_CACHE_URL)

        debug_check_port(parsed.hostname, parsed.port)

        client = create_client(REDIS_CACHE_URL)

        if client is None:
            print("[REDIS CACHE] Client creation failed")
            return None

        print("[REDIS CACHE] Pinging server...")
        client.ping()

        print("[REDIS CACHE] Connected successfully ✅")

        _cache_client = client
        return _cache_client

    except Exception as e:
        print(f"[REDIS CACHE ERROR] Connection failed: {e}")

        traceback.print_exc()

        _cache_client = None
        return None


# =========================
# LIMIT REDIS
# =========================
def get_limit_redis():
    global _limit_client

    try:
        if _limit_client and is_alive(_limit_client):
            print("[REDIS LIMIT] Using existing alive connection")
            return _limit_client

        print("[REDIS LIMIT] Connecting...")

        parsed = urlparse(REDIS_LIMIT_URL)

        debug_check_port(parsed.hostname, parsed.port)

        client = create_client(REDIS_LIMIT_URL)

        if client is None:
            print("[REDIS LIMIT] Client creation failed")
            return None

        print("[REDIS LIMIT] Pinging server...")
        client.ping()

        print("[REDIS LIMIT] Connected successfully ✅")

        _limit_client = client
        return _limit_client

    except Exception as e:
        print(f"[REDIS LIMIT ERROR] Connection failed: {e}")

        traceback.print_exc()

        _limit_client = None
        return None
