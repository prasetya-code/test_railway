from typing import Dict

DB_DRIVER   = "postgresql+psycopg"
DB_USER     = "user"
DB_PASSWORD = "password"
DB_HOST     = "localhost"
DB_PORT     = 5432
DB_NAME     = "app_db"

DATABASE_URI = (
    f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_SLOW_DB_QUERY_TIME_WARNING = 0.5
SQLALCHEMY_COMMIT_ON_TEARDOWN = False

POOL_SIZE = 10
MAX_OVERFLOW = 20
POOL_TIMEOUT = 30
POOL_RECYCLE = 1800
POOL_PRE_PING = True
ENGINE_FUTURE = True

EXECUTION_OPTIONS = {
    "execution_options": {
        "postgresql_readonly": False,
        "postgresql_deferrable": False,
    }
}

CONNECT_ARGS = {
    "connect_timeout": 10,
    "options": "-c statement_timeout=30000",
}

SESSION_OPTIONS = {
    "expire_on_commit": True,
    "autoflush": True,
    "autocommit": False,
}

USE_AUTO_CREATE_TABLES = False


def build_engine_options() -> Dict:
    return {
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "pool_timeout": POOL_TIMEOUT,
        "pool_recycle": POOL_RECYCLE,
        "pool_pre_ping": POOL_PRE_PING,
        "future": ENGINE_FUTURE,
        "connect_args": CONNECT_ARGS,
        **EXECUTION_OPTIONS,
    }


def build_sqlalchemy_config() -> Dict:
    return {
        "SQLALCHEMY_DATABASE_URI": DATABASE_URI,
        "SQLALCHEMY_TRACK_MODIFICATIONS": SQLALCHEMY_TRACK_MODIFICATIONS,
        "SQLALCHEMY_ECHO": SQLALCHEMY_ECHO,
        "SQLALCHEMY_RECORD_QUERIES": SQLALCHEMY_RECORD_QUERIES,
        "SQLALCHEMY_ENGINE_OPTIONS": build_engine_options(),
    }