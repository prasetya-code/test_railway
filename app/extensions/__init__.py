import traceback

# =========================
# 🔥 GLOBAL CONTROL
# =========================
GLOBAL_REDIS = False        # True activate redis
GLOBAL_TALISMAN = True     # True activate production


def register_extension(app):

    try:
        from .flask_compressing import init_compress
        from .flask_cache import init_cache
        from .flask_limit import init_limiter
        from .flask_talisman import init_talisman  # 👈 TAMBAHAN BARU

        # =========================
        # GLOBAL CONFIG INJECTION
        # =========================
        app.config["GLOBAL_REDIS"] = GLOBAL_REDIS
        app.config["GLOBAL_TALISMAN"] = GLOBAL_TALISMAN

        print("\n==========================================")
        print(f"[GLOBAL CONFIG] GLOBAL_REDIS: {GLOBAL_REDIS}")
        print(f"[GLOBAL CONFIG] GLOBAL_TALISMAN: {GLOBAL_TALISMAN}")
        print("==========================================\n")

        # =========================
        # INIT EXTENSIONS
        # =========================
        init_compress(app)
        init_cache(app)
        init_limiter(app)

        # 👉 TALISMAN (BARU)
        init_talisman(app)

    except Exception as e:

        print("\nEXTENSION gagal diregister")
        print("ERROR:", e)

        traceback.print_exc()