import traceback

from ..utils.sqlalchemy.sqlalchemy_engine import apply_config, init_extension, verify_connection
from ..utils.sqlalchemy.sqlalchemy_config import build_sqlalchemy_config
from ..utils.sqlalchemy.sqlalchemy_validation import validate_config, validate_not_initialized, _DB_INITIALIZED
from ..utils.sqlalchemy.sqlalchemy_tables import create_tables


def init_database(app):
    global _DB_INITIALIZED

    print("=" * 50)
    print("INIT DATABASE")
    print("=" * 50)

    try:
        validate_not_initialized()
        validate_config()

        config = build_sqlalchemy_config()
        apply_config(app, config)

        init_extension(app)
        verify_connection(app)
        create_tables(app)

        _DB_INITIALIZED = True

        print("[OK] DB initialized")

    except RuntimeError as e:
        print("[WARN]", e)
        return app

    except Exception:
        print("[FATAL]")
        print(traceback.format_exc())
        raise

    return app