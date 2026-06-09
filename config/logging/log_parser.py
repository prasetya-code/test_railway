from .rotate_parser import setup_logger

# =========================================================
# FIELD REGISTRY
# =========================================================

FIELD_GROUPS = {
    "common": [
        "asctime",
        "levelname",
        "name",
        "message",
        "request_id",
        "client_ip",
        "filename",
        "funcName",
        "lineno",
    ],
    "geo": [
        "city",
        "country",
        "lat",
        "lon",
        "source",
        "confidence",
    ],
    "http": [
        "method",
        "path",
        "query_string",
        "http_version",
        "referer",
        "status_code",
        "bytes_sent",
        "response_time",
        "host",
    ],
    "ua": [
        "user_agent",
        "device",
        "os",
        "os_version",
        "browser",
        "browser_version",
    ],
    "app": [
        "environment",
        "app_version",
        "hostname",
        "pid",
        "tid",
    ],
    "url": [
        "url",
    ],
    "security": [
        "event_type",
        "threat_type",
        "severity",
        "auth_user",
        "auth_method",
        "login_result",
        "blocked",
        "log_hash",
    ],
}


# =========================================================
# LOGGER SCHEMAS
# =========================================================

LOGGER_SCHEMAS = {
    "APP": (
        "common",
        "app",
        "url",
        "http",
    ),
    "ACCESS": (
        "common",
        "geo",
        "http",
        "ua",
    ),
    "SECURITY": (
        "common",
        "geo",
        "ua",
        "security",
        "url",
        "http",
    ),
}


# =========================================================
# FIELD COMPOSER
# =========================================================


def compose_fields(*groups):
    """
    Merge field groups while preserving order
    and removing duplicates.
    """

    fields = []

    for group in groups:
        fields.extend(FIELD_GROUPS.get(group, []))

    return list(dict.fromkeys(fields))


# =========================================================
# LOGGER FIELDS
# =========================================================

APP_FIELDS = compose_fields(*LOGGER_SCHEMAS["APP"])

ACCESS_FIELDS = compose_fields(*LOGGER_SCHEMAS["ACCESS"])

SECURITY_FIELDS = compose_fields(*LOGGER_SCHEMAS["SECURITY"])


# =========================================================
# CENTRALIZED LOGGERS
# =========================================================

app_logger = setup_logger(
    logger_name="APP",
    fields=APP_FIELDS,
)

access_logger = setup_logger(
    logger_name="ACCESS",
    fields=ACCESS_FIELDS,
)

security_logger = setup_logger(
    logger_name="SECURITY",
    fields=SECURITY_FIELDS,
)
