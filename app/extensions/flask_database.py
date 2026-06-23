import traceback


def init_database(app):
    global _DB_INITIALIZED

    print("=" * 15)
    print("INIT DATABASE")
    print("=" * 15)

    try:
        print("test")

    except RuntimeError as e:
        print("[WARN]", e)
        return app

    except Exception:
        print("[FATAL]")
        print(traceback.format_exc())
        raise

    return app
