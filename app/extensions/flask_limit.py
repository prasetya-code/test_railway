from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ..utils.redis_utility.redis_config import REDIS_LIMIT_URL
from ..utils.redis_utility.redis_availability import is_limit_redis_available

import os
import traceback

# =========================
# CONFIG
# =========================
DEFAULT = ["200 per day", "50 per hour"]
GET_REDIS_URL = REDIS_LIMIT_URL
KEY_PREFIX = os.getenv("LIMITER_KEY_PREFIX", "rl:")

# =========================
# ENV CONTROL (SECONDARY)
# =========================
# Change val env (str) into boolean (TRUE / FALSE)
USE_REDIS_LIMITER_RAW = os.getenv("USE_REDIS_LIMITER", "true")

# normalisasi debug-friendly
USE_REDIS_LIMITER = USE_REDIS_LIMITER_RAW.lower() == "true"


# =========================
# KEY FUNCTION
# =========================
def default_key_func():
    try:
        return get_remote_address()

    except Exception as e:
        print(f"[LIMITER ERROR] Failed to get remote address: {e}")
        traceback.print_exc()
        return "unknown"


# =========================
# RATE LIMIT STRATEGY (Limiter(strategy=""))
# =========================
"""
1. "fixed-window"
   - Menghitung request dalam interval waktu tetap
   - Lebih ringan & sederhana
   - Bisa terjadi burst di awal window

2. "moving-window"
   - Sliding window (lebih akurat & adil)
   - Direkomendasikan untuk production

3. "sliding-window-counter"
   - Kombinasi fixed & moving window
   - Lebih efisien dengan akurasi cukup baik

Catatan:
- Gunakan "moving-window" untuk akurasi terbaik
- "fixed-window" cocok jika butuh performa tinggi
- Strategy ini optimal jika menggunakan Redis (shared storage)
"""


# =========================
# LIMITER INSTANCE
# =========================
fl_limiter = Limiter(
    key_func=default_key_func,
    default_limits=DEFAULT,
    strategy="moving-window",
    headers_enabled=True,
    swallow_errors=True,
    key_prefix=KEY_PREFIX,
)


# =========================
# INIT LIMITER
# =========================
def init_limiter(app):
    try:
        print("\n=========================")
        print("[LIMITER INIT START]")
        print("=========================\n")

        # =========================
        # GLOBAL CONTROL (MASTER SWITCH)
        # =========================
        global_redis = app.config.get("GLOBAL_REDIS", True)

        print("[DECISION INPUT]")
        print(f"[INPUT] app.config GLOBAL_REDIS = {global_redis}")
        print(f"[INPUT] USE_REDIS_LIMITER       = {USE_REDIS_LIMITER}\n")

        # =========================
        # STORAGE DECISION
        # =========================
        # PRIORITY:
        # 1. Global Redis
        # 2. ENV (USE_REDIS_LIMITER)
        # 3. Redis availability
        #

        storage_uri = None
        decision_reason = None

        if not global_redis:
            storage_uri = "memory://"
            decision_reason = "GLOBAL_REDIS is False → force memory storage"
            print("[LIMITER DECISION] Redis DISABLED by GLOBAL_REDIS")

        elif not USE_REDIS_LIMITER:
            storage_uri = "memory://"
            decision_reason = "USE_REDIS_LIMITER is False → force memory storage"
            print("[LIMITER DECISION] Redis DISABLED by ENV")

        else:
            print("[LIMITER DECISION] Redis allowed → checking availability...")

            if is_limit_redis_available():
                storage_uri = GET_REDIS_URL
                decision_reason = "Redis available → using Redis storage"
                print("[LIMITER DECISION] Redis AVAILABLE → USING REDIS")
            else:
                storage_uri = "memory://"
                decision_reason = "Redis not available → fallback memory"
                print("[LIMITER WARNING] Redis NOT available → fallback memory")

        print("\n[DECISION RESULT]")
        print(f"[RESULT] storage_uri = {storage_uri}")
        print(f"[RESULT] reason      = {decision_reason}")

        # =========================
        # APPLY CONFIG
        # =========================
        app.config["RATELIMIT_STORAGE_URI"] = storage_uri
        app.config["RATELIMIT_KEY_PREFIX"] = KEY_PREFIX
        app.config["RATELIMIT_SWALLOW_ERRORS"] = True

        print("\n[FLASK CONFIG APPLIED]")
        print(f"[CONFIG] RATELIMIT_STORAGE_URI = {storage_uri}")
        print(f"[CONFIG] RATELIMIT_KEY_PREFIX  = {KEY_PREFIX}")
        print("[CONFIG] SWALLOW_ERRORS        = True")

        # =========================
        # INIT LIMITER
        # =========================
        fl_limiter.init_app(app)

        print("\n[LIMITER INIT SUCCESS]")
        print(f"[OK] Limiter initialized using: {storage_uri}\n")

    except Exception as e:
        print(f"\n[LIMITER ERROR] Failed to initialize limiter: {e}")
        traceback.print_exc()

        # =========================
        # FALLBACK MANUAL
        # =========================
        try:
            print("\n[FAILSAFE FALLBACK]")
            print("[FALLBACK] Switching to memory://")

            app.config["RATELIMIT_STORAGE_URI"] = "memory://"

            fl_limiter.init_app(app)

            print("[FALLBACK SUCCESS] Limiter running in memory mode")

        except Exception as fallback_error:
            print(f"[FATAL FALLBACK ERROR] {fallback_error}")
            traceback.print_exc()
