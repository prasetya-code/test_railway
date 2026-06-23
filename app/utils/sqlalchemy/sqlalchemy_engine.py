import traceback
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from flask_sqlalchemy import SQLAlchemy

fl_db = SQLAlchemy()


def apply_config(app, config):
    try:
        for k, v in config.items():
            app.config[k] = v
    except Exception:
        print(traceback.format_exc())
        raise RuntimeError("Gagal apply config")


def init_extension(app):
    try:
        fl_db.init_app(app)
    except Exception:
        print(traceback.format_exc())
        raise RuntimeError("Gagal init SQLAlchemy")


def verify_connection(app):
    from .sqlalchemy_config import DB_HOST, DB_PORT, DB_NAME

    try:
        with app.app_context():
            with fl_db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        print(f"DB OK {DB_HOST}:{DB_PORT}/{DB_NAME}")

    except OperationalError:
        print(traceback.format_exc())
        raise