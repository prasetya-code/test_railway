import os
from redis.retry import Retry
from redis.backoff import ExponentialBackoff

# =========================
# REDIS URL CONFIG
# =========================
REDIS_CACHE_URL = os.getenv("REDIS_CACHE_URL", "redis://localhost:6379/1")

REDIS_LIMIT_URL = os.getenv("REDIS_LIMIT_URL", "redis://localhost:6379/2")

# =========================
# TIMEOUT (dalam detik)
# =========================
TIMEOUT = 5  # (recommended: normal range

REDIS_COMMON_CONFIG = {
    "socket_connect_timeout": TIMEOUT,
    "socket_timeout": TIMEOUT,
    # =========================
    # CONNECTION POOL
    # =========================
    "max_connections": 20,
    # =========================
    # RETRY STRATEGY (versi simpel)
    # =========================
    "retry": Retry(ExponentialBackoff(), 3),
    "retry_on_timeout": True,
}
