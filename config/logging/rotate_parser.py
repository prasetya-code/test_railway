import os
import logging

from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from flask import (
    has_request_context,
    request,
)

from pythonjsonlogger.json import JsonFormatter


# =========================================================
# LOG DIRECTORY
# =========================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

LOG_DIR = os.path.join(
    ROOT_DIR,
    "logs",
)

os.makedirs(
    LOG_DIR,
    exist_ok=True,
)


# =========================================================
# ACCESS FILTER
# =========================================================


class AccessContextFilter(logging.Filter):
    def filter(self, record):

        if has_request_context():
            # -------------------------------------
            # COMMON
            # -------------------------------------

            record.request_id = getattr(
                record,
                "request_id",
                None,
            )

            record.client_ip = request.headers.get(
                "X-Forwarded-For",
                request.remote_addr,
            )

            # -------------------------------------
            # HTTP
            # -------------------------------------

            record.method = request.method

            record.path = request.path

            record.query_string = request.query_string.decode(
                "utf-8",
                errors="ignore",
            )

            record.http_version = request.environ.get("SERVER_PROTOCOL")

            record.referer = request.referrer

            record.host = request.host

            # -------------------------------------
            # UA
            # -------------------------------------

            record.user_agent = request.headers.get("User-Agent")

        return True


# =========================================================
# DEFAULT FIELD VALUE FILTER
# =========================================================


class DefaultFieldFilter(logging.Filter):
    def __init__(self, fields):
        super().__init__()
        self.fields = fields

    def filter(self, record):

        for field in self.fields:
            if not hasattr(record, field):
                setattr(
                    record,
                    field,
                    None,
                )

        return True


# =========================================================
# LOGGER SETUP
# =========================================================


def setup_logger(
    logger_name,
    fields,
    level=logging.INFO,
):

    logger = logging.getLogger(logger_name)

    logger.setLevel(level)

    logger.propagate = False

    if logger.handlers:
        return logger

    current_date = datetime.now().strftime("%Y-%m-%d")

    log_filename = f"{logger_name.lower()}_{current_date}.log"

    log_path = os.path.join(
        LOG_DIR,
        log_filename,
    )

    handler = TimedRotatingFileHandler(
        filename=log_path,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )

    formatter = JsonFormatter(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s "
        "%(message)s " + " ".join(f"%({field})s" for field in fields)
    )

    handler.setFormatter(formatter)

    logger.addFilter(DefaultFieldFilter(fields))

    if logger_name == "ACCESS":
        logger.addFilter(AccessContextFilter())

    logger.addHandler(handler)

    return logger
