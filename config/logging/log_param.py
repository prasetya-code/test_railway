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
# SECURITY EVENT REGISTRY (CONSISTENT SCHEMA)
# =========================================================

SECURITY_EVENTS = {
    "RATE_LIMIT_EXCEEDED": {
        "event_type": "RATE_LIMIT",
        "threat_type": None,
        "severity": "MEDIUM",
        "auth_user": None,
        "auth_method": None,
        "login_result": None,
        "blocked": True,
        "log_hash": None,
    },
    "INVALID_TOKEN": {
        "event_type": "AUTH",
        "threat_type": "INVALID_TOKEN",
        "severity": "HIGH",
        "auth_user": None,
        "auth_method": "JWT",
        "login_result": "FAILED",
        "blocked": True,
        "log_hash": None,
    },
    "LOGIN_FAILED": {
        "event_type": "LOGIN",
        "threat_type": None,
        "severity": "MEDIUM",
        "auth_user": None,
        "auth_method": "PASSWORD",
        "login_result": "FAILED",
        "blocked": False,
        "log_hash": None,
    },
    "FORBIDDEN_ACCESS": {
        "event_type": "AUTH",
        "threat_type": "FORBIDDEN",
        "severity": "HIGH",
        "auth_user": None,
        "auth_method": None,
        "login_result": None,
        "blocked": True,
        "log_hash": None,
    },
}
